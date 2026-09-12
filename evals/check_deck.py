#!/usr/bin/env python3
"""Mechanical evidence for grading eval runs of the offer-builder skill.

Reads a run's deck (outputs/*.html) and conversation.json (written by run_conversation.py) and
writes <run_dir>/checks.json: language ratios, exact hex codes, fonts, currency strings, tax-rate
mentions, placeholder and demo markers, tool calls, and whether each statistic in the deck
appears in this run's web results. It gathers evidence; judgement calls stay with the grader.

Usage:
  python check_deck.py --iteration <iteration_dir>          # every eval-*/*/run-* directory
  python check_deck.py --run <run_dir> --eval-id 1
"""

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path

GOLD_HEXES = ["#c9a84c", "#e8c97a"]  # the old built-in gold accent pair
NEUTRAL_FALLBACK_HEXES = ["#f7f7f5", "#16181d", "#3a5a8c"]
EN_TIER_NAMES = re.compile(r"\b(foundation|growth|dominance)\b", re.I)
WEB_TOOLS = {"WebSearch", "WebFetch"}

SPEC = {
    1: {"lang": "pl", "hexes": ["#0f1b2d", "#f4f6fa", "#2bb3a3", "#ff7a59"], "fonts": ["Manrope", "Inter"],
        "currency_ok": ["zł", "PLN"], "currency_bad": ["€", "EUR", "$", "лв", "BGN"],
        "agency": "Kestrel Web", "email": "hello@kestrelweb.example", "translate_tiers": True},
    2: {"lang": "en", "hexes": ["#faf7f2", "#1b3a4b", "#e4572e"], "fonts": ["Fraunces", "DM Sans"],
        "currency_ok": ["£", "GBP"], "currency_bad": ["€", "EUR", "лв", "BGN"],
        "agency": "Fernhill Studio", "email": "hello@fernhill.example"},
    3: {"lang": "en", "hexes": [], "fonts": [], "currency_ok": ["CAD", "CA$", "C$", "$"],
        "currency_bad": ["€", "EUR", "лв", "BGN"], "fallback": True},
    4: {"lang": "en", "hexes": ["#111827", "#f9fafb", "#22d3ee"], "fonts": ["Space Grotesk", "Inter"],
        "currency_ok": ["$", "USD"], "currency_bad": ["€", "EUR", "лв", "BGN"],
        "agency": "Northbeam Digital", "email": "hello@northbeam.example", "demo": True},
    5: {"automation": True},
    6: {"lang": "en", "hexes": ["#ffffff", "#1d1d1f", "#0a7cff"], "fonts": ["Inter"],
        "currency_ok": ["€", "EUR"], "currency_bad": ["лв", "BGN"],
        "agency": "Pixelkraft", "email": "studio@pixelkraft.example"},
    7: {"lang": "bg", "hexes": ["#0a0a0a", "#f5f5f5", "#d1a945"], "fonts": ["Playfair Display", "Inter"],
        "currency_ok": ["€", "EUR", "евро"], "currency_bad": ["лв", "BGN", "$"],
        "agency": "D&M Web Design", "email": "office@dm-web.example", "translate_tiers": True},
    8: {"lang": "en", "hexes": ["#f4f1ea", "#22313f", "#2f7d5d"], "fonts": ["DM Serif Display", "DM Sans"],
        "currency_ok": ["€", "EUR"], "currency_bad": ["лв", "BGN"],
        "agency": "Greenlane Web", "email": "hello@greenlane.example", "no_web": True},
}

PL_WORDS = {"i", "w", "na", "z", "do", "dla", "się", "że", "jest", "nie", "od", "po", "oraz", "jak", "czy",
            "twój", "twoja", "twoje", "nasz", "nasza", "nasze", "strona", "pakiet", "pakiety", "więcej",
            "który", "która", "które", "przez", "bez", "już", "tylko", "pacjentów", "klientów"}
EN_WORDS = {"the", "and", "for", "your", "with", "of", "is", "our", "you", "in", "that", "more", "this",
            "are", "from", "will", "get", "we"}

PERCENT_RE = re.compile(r"(?<![\d.,])(\d+(?:[.,]\d+)?)\s?(?:%|percent\b|per cent\b|procent\w*|процент\w*)", re.I)
MULT_RE = re.compile(r"(?<![\d.,])(\d+(?:[.,]\d+)?)\s?(?:x|×)(?!\w)|(?<![\d.,])(\d+(?:[.,]\d+)?)\s(?:times|razy|пъти)\b", re.I)
RATIO_RE = re.compile(r"(?<![\d.,])(\d{1,3})\s(?:in|out of|z|от)\s(\d{1,4})\b", re.I)
SCALE_RE = re.compile(r"(?<![\d.,])(\d+(?:[.,]\d+)?)\s?(?:million|billion|mln|mld|милиона?|милиарда?)\b", re.I)
TAX_RATE_RE = re.compile(
    r"(?:VAT|ДДС|HST|GST|PST|QST|sales tax|podat\w*|DPH|IVA|MwSt|tax)[^.\n%]{0,25}?\d{1,2}(?:[.,]\d)?\s?%"
    r"|\d{1,2}(?:[.,]\d)?\s?%[^.\n]{0,25}?(?:VAT|ДДС|HST|GST|PST|QST|sales tax|podat\w*|tax)", re.I)
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
EMAIL_RE = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")
DOMAIN_RE = re.compile(r"\b(?:https?://)?(?:www\.)?((?:[a-z0-9-]+\.)+(?:com|net|org|io|co|us|ca|uk|de|pl|bg|si|ie|eu|example|test))\b", re.I)
NANP_PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")
INTL_PHONE_RE = re.compile(r"\+\d{1,3}[\s\d().-]{7,}\d")
ADDRESS_RE = re.compile(r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s){1,3}(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Way|Place|Pl\.?|Court|Ct\.?)(?!\w)")
PLACEHOLDER_RE = re.compile(r"\[[^\]\n]{2,40}\]")


class DeckParser(HTMLParser):
    SKIP = {"script", "style", "head", "noscript", "svg", "template"}
    BREAK = {"br", "p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "tr", "section",
             "article", "header", "footer", "span", "button", "a", "small", "strong", "em", "b", "i"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang, self.skip, self.in_style, self.slides = None, 0, False, 0
        self.text, self.comments, self.css, self.links, self.hrefs = [], [], [], [], []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "link" and a.get("href"):
            self.links.append(a["href"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        if a.get("style"):
            self.css.append(a["style"])
        if "slide" in a.get("class", "").split():
            self.slides += 1
        if tag in self.SKIP:
            self.skip += 1
            self.in_style = self.in_style or tag == "style"
        elif tag in self.BREAK:
            self.text.append(" ")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            if tag == "style":
                self.in_style = False
        elif tag in self.BREAK:
            self.text.append(" ")

    def handle_data(self, data):
        if self.in_style:
            self.css.append(data)
        elif not self.skip:
            self.text.append(data)

    def handle_comment(self, data):
        self.comments.append(data.strip())


def norm_hex(h: str) -> str:
    h = h.lower()
    return "#" + "".join(c * 2 for c in h[1:]) if len(h) == 4 else h


def find_deck(outputs: Path):
    decks = list(outputs.glob("*.html"))
    if not decks:
        return None
    return max(decks, key=lambda p: ("slide" in p.read_text(encoding="utf-8", errors="replace"), p.stat().st_size))


def root_vars(css: str) -> dict:
    out = {}
    for block in re.findall(r":root\s*\{([^}]*)\}", css):
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);?", block):
            out[name] = value.strip()
    return out


def language_scores(text: str) -> dict:
    words = re.findall(r"[^\W\d_]+", text.lower())
    pl = sum(w in PL_WORDS for w in words)
    en = sum(w in EN_WORDS for w in words)
    letters = re.findall(r"[^\W\d_]", text)
    cyr = sum("Ѐ" <= ch <= "ӿ" for ch in letters)
    return {"words": len(words), "polish_stopwords": pl, "english_stopwords": en,
            "polish_share": round(pl / max(1, pl + en), 3),
            "cyrillic_letter_share": round(cyr / max(1, len(letters)), 3)}


def num_regex(num: str) -> str:
    n = re.sub(r"[\s  ]", "", num)
    if re.fullmatch(r"\d+[.,]\d+", n):
        a, b = re.split(r"[.,]", n)
        return rf"{a}[.,]{b}"
    return re.escape(n)


def find_claims(text: str) -> list:
    claims = []
    for kind, rx in (("percent", PERCENT_RE), ("multiplier", MULT_RE), ("ratio", RATIO_RE), ("scale", SCALE_RE)):
        for m in rx.finditer(text):
            claims.append({"kind": kind, "figure": m.group(0).strip(),
                           "context": text[max(0, m.start() - 80): m.end() + 80].strip()})
    return claims


def trace(claim: dict, corpus: str, persona_numbers: set) -> dict:
    nums = re.findall(r"\d+(?:[.,]\d+)?", claim["figure"])
    first = num_regex(nums[0])
    kind = claim["kind"]
    if kind == "percent":
        strong = rf"(?<![\d.,]){first}\s?(?:%|percent|per cent)"
    elif kind == "multiplier":
        strong = rf"(?<![\d.,]){first}\s?(?:x|×|times|-fold|fold)"
    elif kind == "ratio" and len(nums) > 1:
        strong = rf"(?<![\d.,]){nums[0]}\s(?:in|out of|of)\s{nums[1]}\b"
    else:
        strong = rf"(?<![\d.,]){first}\s?(?:million|billion|m\b|bn|mln)"
    return {**claim,
            "in_web_results": re.search(strong, corpus, re.I) is not None,
            "number_anywhere_in_web_results": re.search(rf"(?<![\d.,]){first}(?!\d)", corpus) is not None,
            "matches_client_supplied_number": re.sub(r"[.,]", "", nums[0]) in persona_numbers}


def conversation_facts(conv: list) -> dict:
    id_to_name, web_calls, web_ok, queries, fetched = {}, 0, 0, [], []
    corpus_parts, first_web_ok, first_deck_write, idx = [], None, None, 0
    assistant_by_turn = []
    for t in conv:
        texts = []
        for item in t["items"]:
            idx += 1
            if item["kind"] == "text":
                texts.append(item["text"])
            elif item["kind"] == "tool_use":
                id_to_name[item["id"]] = item["name"]
                if item["name"] in WEB_TOOLS:
                    web_calls += 1
                    if item["name"] == "WebSearch":
                        queries.append(item["input"].get("query"))
                    else:
                        fetched.append(item["input"].get("url"))
                if item["name"] == "Write" and str(item["input"].get("file_path", "")).lower().endswith(".html"):
                    first_deck_write = first_deck_write or idx
            elif item["kind"] == "tool_result":
                if id_to_name.get(item["tool_use_id"]) in WEB_TOOLS and not item["is_error"] and item["text"].strip():
                    web_ok += 1
                    corpus_parts.append(item["text"])
                    first_web_ok = first_web_ok or idx
        assistant_by_turn.append("\n\n".join(texts))
    return {"web_calls": web_calls, "web_results_ok": web_ok, "search_queries": queries, "fetched_urls": fetched,
            "first_web_result_item": first_web_ok, "first_deck_write_item": first_deck_write,
            "research_before_deck": bool(first_web_ok and first_deck_write and first_web_ok < first_deck_write),
            "corpus": "\n".join(corpus_parts), "assistant_by_turn": assistant_by_turn}


def asked_before_reveal(conv: list, assistant_by_turn: list, reveal_rx: str, ask_rx: str) -> dict:
    for i, t in enumerate(conv):
        if i > 0 and re.search(reveal_rx, t["user"], re.I):
            return {"revealed_on_turn": t["turn"],
                    "asked_in_previous_message": bool(re.search(ask_rx, assistant_by_turn[i - 1], re.I))}
    return {"revealed_on_turn": None, "asked_in_previous_message": False}


def check_run(run_dir: Path, eval_id: int, persona: str) -> dict:
    spec = SPEC.get(eval_id, {})
    conv = json.loads((run_dir / "conversation.json").read_text(encoding="utf-8"))
    facts = conversation_facts(conv)
    chat = "\n\n".join(facts["assistant_by_turn"])
    persona_numbers = {re.sub(r"[.,]", "", n) for n in re.findall(r"\d[\d,.]*", persona)}
    out = {"eval_id": eval_id, "run_dir": str(run_dir), "turns": len(conv),
           "research": {k: v for k, v in facts.items() if k not in ("corpus", "assistant_by_turn")}}

    deck_path = find_deck(run_dir / "outputs")
    out["deck"] = {"path": str(deck_path) if deck_path else None}
    if deck_path:
        raw = deck_path.read_text(encoding="utf-8", errors="replace")
        parser = DeckParser()
        parser.feed(raw)
        text = re.sub(r"[ \t\r\n]+", " ", "".join(parser.text)).strip()
        css = "\n".join(parser.css)
        hexes = sorted({norm_hex(h) for h in HEX_RE.findall(css)})
        rv = root_vars(css)
        google = [f.split(":")[0].replace("+", " ") for href in parser.links if "fonts.googleapis.com" in href
                  for f in re.findall(r"family=([^&]+)", href)]
        out["deck"].update({
            "bytes": len(raw), "slides": parser.slides, "html_lang": parser.lang,
            "visible_text_chars": len(text), "language": language_scores(text),
            "root_vars": rv, "css_hexes": hexes,
            "expected_hexes_present": {h: h in hexes or h in [norm_hex(v) for v in rv.values() if v.startswith("#")]
                                       for h in spec.get("hexes", [])},
            "gold_hexes_present": [h for h in GOLD_HEXES if h in hexes],
            "neutral_fallback_hexes_present": [h for h in NEUTRAL_FALLBACK_HEXES if h in hexes],
            "google_fonts": google,
            "expected_fonts_declared": {f: (f in css) or (f in google) for f in spec.get("fonts", [])},
            "playfair_declared": "Playfair" in css or any("Playfair" in g for g in google),
            "english_tier_names": sorted({m.group(0) for m in EN_TIER_NAMES.finditer(text)}),
            "currency_ok_counts": {c: text.count(c) for c in spec.get("currency_ok", [])},
            "currency_bad_counts": {c: len(re.findall(rf"(?<![A-Za-z]){re.escape(c)}(?![A-Za-z])", text))
                                    for c in spec.get("currency_bad", [])},
            "price_samples": re.findall(
                r"(?:[£$€]|CA\$|C\$|PLN|EUR|GBP|USD|CAD)\s?\d[\d\s  .,’']*\d"
                r"|\d[\d\s  .,’']*\d\s?(?:zł|PLN|€|EUR|£|GBP|USD|CAD|лв|BGN|евро)", text)[:20],
            "tax_rate_mentions": [m.group(0) for m in TAX_RATE_RE.finditer(text)],
            "d_and_m_mentions": text.count("D&M"),
            "cyrillic_words": re.findall(r"[Ѐ-ӿ]{3,}", text)[:10],
            "agency_name_present": spec.get("agency", "") in text if spec.get("agency") else None,
            "agency_email_present": spec.get("email", "") in text or spec.get("email", "") in raw if spec.get("email") else None,
            "placeholders": PLACEHOLDER_RE.findall(text)[:15],
            "html_comments": [c[:120] for c in parser.comments][:10],
            "fallback_comment": any("fallback" in c.lower() for c in parser.comments),
        })
        claims = [trace(c, facts["corpus"], persona_numbers) for c in find_claims(text)]
        out["deck"]["claims"] = claims
        out["deck"]["claims_summary"] = {
            "total": len(claims),
            "in_web_results": sum(c["in_web_results"] for c in claims),
            "client_supplied": sum(c["matches_client_supplied_number"] for c in claims),
            "untraced": sum(not c["in_web_results"] and not c["matches_client_supplied_number"] for c in claims)}
        if spec.get("demo"):
            domains = sorted({d.lower() for d in EMAIL_RE.findall(text + " " + raw)} | {d.lower() for d in DOMAIN_RE.findall(text)})
            reserved = lambda d: d.endswith((".example", ".test", ".invalid", "example.com", "example.org", "example.net"))
            out["demo"] = {
                "domains": domains, "non_reserved_domains": [d for d in domains if not reserved(d)],
                "phones": NANP_PHONE_RE.findall(text) + INTL_PHONE_RE.findall(text),
                "street_addresses": ADDRESS_RE.findall(text),
                "demo_marker": bool(re.search(r"\bdemo\b", text, re.I)) and bool(re.search(r"fictional|fictitious|sample|made-up|invented", text, re.I)),
            }
    if spec.get("fallback"):
        out["fallback_notice_in_chat"] = bool(re.search(
            r"(placeholder|fallback|default|neutral|generic)[^.\n]{0,80}(identity|brand|branding|look|palette|agency|name|colou?rs?)"
            r"|(identity|brand|branding|agency name)[^.\n]{0,80}(placeholder|fallback|default|neutral|generic)", chat, re.I))
    if eval_id == 1:
        out["asked_language"] = asked_before_reveal(conv, facts["assistant_by_turn"], r"polish|polsk", r"language|język|jezyk")
        out["asked_currency"] = asked_before_reveal(conv, facts["assistant_by_turn"], r"\bPLN\b|zł|złot", r"currency|waluta|PLN|zł")
    if spec.get("automation"):
        out["automation"] = {
            "deck_created": deck_path is not None,
            "money_in_chat": re.findall(r"(?:\$|USD)\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*\s?(?:USD|\$)", chat)[:20],
            "pushes_delivered": sum(bool(re.search(r"make up|invent", t["user"], re.I)) for t in conv),
            "final_assistant_message": facts["assistant_by_turn"][-1][-1500:] if facts["assistant_by_turn"] else "",
        }
    if spec.get("no_web"):
        out["no_search_notice_in_chat"] = bool(re.search(
            r"(can't|cannot|can not|unable|don't have|do not have|no|without)\s[^.\n]{0,50}(search|web|internet|brows|research|look up)", chat, re.I))
    return out


def summarize(res: dict) -> str:
    d = res.get("deck", {})
    bits = [f"eval-{res['eval_id']}", Path(res["run_dir"]).parent.name, Path(res["run_dir"]).name,
            f"turns={res['turns']}", f"web_ok={res['research']['web_results_ok']}",
            f"deck={'yes' if d.get('path') else 'no'}"]
    if d.get("path"):
        cs = d["claims_summary"]
        bits += [f"lang={d['html_lang']}", f"slides={d['slides']}",
                 f"claims={cs['total']} traced={cs['in_web_results']} client={cs['client_supplied']} untraced={cs['untraced']}",
                 f"gold={d['gold_hexes_present']}", f"bad_currency={ {k: v for k, v in d['currency_bad_counts'].items() if v} }",
                 f"en_tiers={d['english_tier_names']}"]
    return " | ".join(bits)


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect mechanical grading evidence for eval runs.")
    ap.add_argument("--iteration", type=Path)
    ap.add_argument("--run", type=Path)
    ap.add_argument("--eval-id", type=int)
    ap.add_argument("--evals", type=Path, default=Path(__file__).with_name("evals.json"))
    args = ap.parse_args()
    personas = {e["id"]: e.get("persona", "") for e in json.loads(args.evals.read_text(encoding="utf-8"))["evals"]}
    runs = []
    if args.iteration:
        for run_dir in sorted(args.iteration.glob("eval-*/*/run-*")):
            if (run_dir / "conversation.json").exists():
                runs.append((run_dir, int(run_dir.parent.parent.name.split("-")[1])))
    elif args.run and args.eval_id:
        runs.append((args.run, args.eval_id))
    else:
        ap.error("give --iteration, or --run with --eval-id")
    for run_dir, eval_id in runs:
        res = check_run(run_dir, eval_id, personas.get(eval_id, ""))
        (run_dir / "checks.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print(summarize(res))


if __name__ == "__main__":
    main()
