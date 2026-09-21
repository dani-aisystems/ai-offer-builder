#!/usr/bin/env python3
"""Mechanical evidence for grading the project-scope evals of the offer-builder skill.

Reads a run's saved .docx/.pdf (outputs/, recursively, seeded files excluded) and conversation.json,
and writes into the run directory:
  scope.txt           the document's text, one paragraph per line, headings marked with '#'
  scope-page-N.png    renders of the saved PDF's pages, when pdftoppm is available
  scope_checks.json   language ratio, contract/signature wording, prices, tax wording, default and
                      agreed-term markers, fonts, colors, document language, shaded paragraphs,
                      PDF page count, seed integrity, and chat evidence (questions, defaults flagged)
It gathers evidence; judgement calls stay with the grader. Standard library only.

Usage:
  python check_scope.py --iteration <iteration_dir>          # every scope eval run in it
  python check_scope.py --run <run_dir> --eval-id 9
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parent.parent
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# "договор" as a noun (contract) only; "договорен/договорения обхват" (agreed scope) is fine.
CONTRACT_RE = re.compile(r"\bдоговор(?:а|ът|и|ите)?\b|\bспоразумени\w*|\bподпис\w*|\bcontract(?!or)\w*|\bagreement\w*"
                         r"|\bsignature\w*|\bsigned by\b|\bsign here\b", re.I)
DEFAULT_MARKERS = {
    "deposit_25": r"(?<!\d)25\s?%",
    "final_75": r"(?<!\d)75\s?%",
    "materials_5_business_days": r"(?<!\d)5\s+(?:работни|business|working)|\bfive\s+(?:business|working)|\bпет\s+работни",
    "build_10_14": r"(?<!\d)10\s?[–—-]\s?14(?!\d)",
    "viber_or_whatsapp": r"viber|whatsapp",
}
REVISION_COUNT_RE = re.compile(
    r"\b(?:\d+|one|two|three|four|five|един|една|два|две|три|четири|пет)\s+(?:rounds?|кръга?|рунда?|revision rounds?)\b", re.I)
CHAT_DEFAULT_RE = re.compile(r"\(default\)|\bdefaults?\b|по подразбиране|стандартн\w+ услови", re.I)

SPEC = {
    9: {"lang": "bg", "price": r"1[\s.]?100\s?(?:€|евро|EUR)|€\s?1[\s.,]?100", "tax": r"без\s+ДДС",
        "hexes": ["#d1a945"], "fonts": ["Playfair Display", "Inter"], "agency": "Example Digital",
        "defaults_expected": True,
        "watch": {"not_in_offer": r"блог|онлайн плащан|реклам|google ads|английск|многоезич|онлайн магазин"}},
    10: {"lang": "en", "price": r"£\s?2,?400", "tax": r"VAT", "bad_price": r"£\s?2,?650",
         "hexes": ["#1b3a4b", "#e4572e"], "fonts": ["Fraunces", "DM Sans"], "agency": "Fernhill Studio",
         "defaults_expected": False,
         "agreed": {"deposit_50": r"(?<!\d)50\s?%", "three_weeks": r"\b(?:3|three)\s+weeks?\b",
                    "two_rounds": r"\b(?:2|two)\s+(?:rounds?|revision rounds?)\b", "thirty_days": r"\b30[\s-]days?\b"},
         "watch": {"blog": r"\bblog\w*"}},
    11: {"lang": "en", "price": r"(?:CA\$|C\$|\$)\s?2,650", "tax": r"before HST",
         "hexes": ["#d97757"], "fonts": ["Manrope", "Inter"], "agency": "Example Digital",
         "defaults_expected": True,
         "record_only": {"emergency_banner": r"emergency banner|banner[^.\n]{0,60}emergenc",
                         "seo_every_page": r"(?:on-page )?SEO[^.\n]{0,60}(?:every|each) (?:page|service)"
                                           r"|(?:every|each) page[^.\n]{0,60}SEO"},
         "watch": {"package_3_items": r"google (?:search )?ads|landing pages?|community pages|directory listings"
                                      r"|guides? a month|ad spend|local SEO"}},
}


def norm(text: str) -> str:
    return text.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2009", " ")


def contexts(rx: str, text: str, width: int = 70, limit: int = 12) -> list:
    out = []
    for m in re.finditer(rx, text, re.I):
        out.append(text[max(0, m.start() - width):m.end() + width].replace("\n", " / "))
        if len(out) >= limit:
            break
    return out


def attr(el, name: str):
    return el.get(W + name) if el is not None else None


def luminance(hexcode: str) -> float:
    rgb = [int(hexcode.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return round((hi + 0.05) / (lo + 0.05), 2)


def colored_runs(roots: list, styles) -> list:
    """Text runs with an explicit color: text, color, size in pt and boldness (run or paragraph style)."""
    style_rpr = {}
    for s in (styles.iter(W + "style") if styles is not None else []):
        style_rpr[s.get(W + "styleId")] = s.find(W + "rPr")

    def size_bold(rpr, style_id):
        size, bold = None, False
        for props in (rpr, style_rpr.get(style_id)):
            if props is None:
                continue
            sz, b, fonts = props.find(W + "sz"), props.find(W + "b"), props.find(W + "rFonts")
            size = size or (int(sz.get(W + "val")) / 2 if sz is not None else None)
            bold = bold or (b is not None and b.get(W + "val") not in ("0", "false"))
            bold = bold or bool(fonts is not None and re.search(r"bold|black|heavy", fonts.get(W + "ascii") or "", re.I))
        return size, bold

    out = []
    for root in roots:
        for p in root.iter(W + "p"):
            ppr = p.find(W + "pPr")
            style_id = attr(ppr.find(W + "pStyle"), "val") if ppr is not None else None
            for r in p.iter(W + "r"):
                rpr = r.find(W + "rPr")
                color = attr(rpr.find(W + "color"), "val") if rpr is not None else None
                text = "".join(x.text or "" for x in r.iter(W + "t")).strip()
                if color and color != "auto" and text:
                    size, bold = size_bold(rpr, style_id)
                    out.append({"color": "#" + color.lower(), "text": text[:40], "pt": size, "bold": bold})
    return out


def read_docx(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        body = ET.fromstring(z.read("word/document.xml"))
        extra = [ET.fromstring(z.read(n)) for n in names if re.match(r"word/(?:header|footer)\d*\.xml$", n)]
        styles = ET.fromstring(z.read("word/styles.xml")) if "word/styles.xml" in names else None
        core = z.read("docProps/core.xml").decode("utf-8", "replace") if "docProps/core.xml" in names else ""
    lines, headings, shaded = [], [], []
    for p in body.iter(W + "p"):
        text = "".join((t.text or "") if t.tag == W + "t" else "\t" if t.tag == W + "tab" else ""
                       for t in p.iter())
        text = norm(text).strip()
        if not text:
            continue
        ppr = p.find(W + "pPr")
        style = attr(ppr.find(W + "pStyle"), "val") if ppr is not None else None
        if style and re.search(r"heading|title|заглав", style, re.I):
            headings.append(text)
            lines.append(f"# {text}")
        else:
            lines.append(text)
        if ppr is not None and ppr.find(W + "shd") is not None:
            shaded.append(text[:160])
    for tc in body.iter(W + "tc"):
        tcpr = tc.find(W + "tcPr")
        if tcpr is not None and tcpr.find(W + "shd") is not None:
            fill = attr(tcpr.find(W + "shd"), "fill")
            cell = norm("".join(t.text or "" for t in tc.iter(W + "t"))).strip()
            if cell and fill and fill.lower() not in ("auto", "ffffff"):
                shaded.append(f"[cell {fill}] {cell[:160]}")
    header_footer = [norm("".join(t.text or "" for t in root.iter(W + "t"))).strip() for root in extra]
    fonts, langs = set(), set()
    colors = {"document": set(), "styles": set()}  # template styles carry many unused colors
    for root in [body, *extra] + ([styles] if styles is not None else []):
        where = "styles" if root is styles else "document"
        for el in root.iter(W + "rFonts"):
            fonts.update(v for k, v in el.attrib.items() if k in (W + "ascii", W + "hAnsi", W + "cs"))
        for el in root.iter(W + "color"):
            if attr(el, "val") and attr(el, "val") != "auto":
                colors[where].add("#" + attr(el, "val").lower())
        for el in root.iter(W + "shd"):
            if attr(el, "fill") and attr(el, "fill") != "auto":
                colors[where].add("#" + attr(el, "fill").lower())
        for el in root.iter():  # borders and rules carry the color as an attribute
            if attr(el, "color") and attr(el, "color") != "auto":
                colors[where].add("#" + attr(el, "color").lower())
        for el in root.iter(W + "lang"):
            langs.update(el.attrib.values())
    runs = colored_runs([body, *extra], styles)
    title = re.search(r"<dc:title>(.*?)</dc:title>", core, re.S)
    creator = re.search(r"<dc:creator>(.*?)</dc:creator>", core, re.S)
    return {"text": "\n".join(lines), "headings": headings, "shaded": shaded, "header_footer": header_footer,
            "fonts": sorted(fonts), "colors": {k: sorted(v) for k, v in colors.items()}, "langs": sorted(langs),
            "colored_runs": runs,
            "title_property": title.group(1) if title else None, "author_property": creator.group(1) if creator else None}


def pdf_pages(path: Path):
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        if m:
            return int(m.group(1))
    try:
        from pypdf import PdfReader  # optional
        return len(PdfReader(str(path)).pages)
    except Exception:
        return len(re.findall(rb"/Type\s*/Page(?!s)", path.read_bytes())) or None


def render_pages(pdf: Path, run_dir: Path) -> list:
    if not shutil.which("pdftoppm"):
        return []
    for old in run_dir.glob("scope-page-*.png"):
        old.unlink()
    subprocess.run(["pdftoppm", "-png", "-r", "60", str(pdf), str(run_dir / "scope-page")], capture_output=True)
    return sorted(p.name for p in run_dir.glob("scope-page-*.png"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def created_files(outputs: Path) -> list:
    metrics = outputs / "metrics.json"
    if metrics.exists():
        return [outputs / f for f in json.loads(metrics.read_text(encoding="utf-8")).get("files_created", [])]
    return [p for p in outputs.rglob("*") if p.is_file()]


def chat_evidence(conv: list) -> dict:
    texts, docx_turn, reads = [], None, []
    for t in conv:
        said = "\n".join(i["text"] for i in t["items"] if i["kind"] == "text")
        texts.append((t["turn"], said))
        for i in t["items"]:
            if i["kind"] != "tool_use":
                continue
            blob = json.dumps(i["input"], ensure_ascii=False)
            if docx_turn is None and ".docx" in blob and i["name"] in ("Bash", "Write"):
                docx_turn = t["turn"]
            if re.search(r"Offer record|Offer decks|\.pptx", blob):
                reads.append(f"turn {t['turn']} {i['name']}: {blob[:400]}")
    before = [s for turn, s in texts if docx_turn is None or turn < docx_turn]
    questions = [q.strip() for s in before for q in re.findall(r"[^.!?\n]{8,200}\?", s)]
    final = texts[-1][1] if texts else ""
    return {"docx_first_written_on_turn": docx_turn, "questions_before_docx": questions[:20],
            "offer_folder_tool_calls": reads[:15], "final_message": final[-2500:],
            "final_message_chars": len(final), "defaults_flagged_in_chat": bool(CHAT_DEFAULT_RE.search(final))}


def check_run(run_dir: Path, eval_id: int, ev: dict) -> dict:
    spec = SPEC[eval_id]
    outputs = run_dir / "outputs"
    conv = json.loads((run_dir / "conversation.json").read_text(encoding="utf-8"))
    files = created_files(outputs)
    docx = [p for p in files if p.suffix.lower() == ".docx" and not p.name.startswith("~$")]
    pdfs = [p for p in files if p.suffix.lower() == ".pdf"]
    res = {"eval_id": eval_id, "run_dir": str(run_dir), "turns": len(conv),
           "docx_files": [p.relative_to(outputs).as_posix() for p in docx],
           "pdf_files": {p.relative_to(outputs).as_posix(): pdf_pages(p) for p in pdfs},
           "page_renders": render_pages(max(pdfs, key=lambda p: p.stat().st_mtime), run_dir) if pdfs else [],
           "chat": chat_evidence(conv)}
    if ev.get("seed"):
        res["seed_unchanged"] = {
            s["to"]: (outputs / s["to"]).exists() and sha(outputs / s["to"]) == sha(REPO_ROOT / s["from"])
            for s in ev["seed"]}
    if not docx:
        (run_dir / "scope.txt").write_text("(no .docx saved)\n", encoding="utf-8")
        return res
    doc_path = max(docx, key=lambda p: p.stat().st_mtime)
    d = read_docx(doc_path)
    text = d["text"]
    (run_dir / "scope.txt").write_text(f"{doc_path.relative_to(outputs).as_posix()}\n"
                                       f"HEADER/FOOTER: {' | '.join(d['header_footer'])}\n\n{text}\n", encoding="utf-8")
    letters = re.findall(r"[^\W\d_]", text)
    cyr = sum(1 for c in letters if "Ѐ" <= c <= "ӿ")
    words = len(re.findall(r"\w+", text))
    doc = {
        "path": doc_path.relative_to(outputs).as_posix(),
        "words": words,
        "cyrillic_share": round(cyr / len(letters), 3) if letters else 0,
        "first_lines": text.splitlines()[:6],
        "headings": d["headings"][:40],
        "title_property": d["title_property"], "author_property": d["author_property"],
        "doc_langs": d["langs"], "fonts": d["fonts"], "colors": d["colors"],
        "expected_hexes_present": {h: h in d["colors"]["document"] + d["colors"]["styles"] for h in spec["hexes"]},
        "expected_fonts_present": {f: any(f.lower() in x.lower() for x in d["fonts"]) for f in spec["fonts"]},
        "agency_name_present": spec["agency"].lower() in (text + " ".join(d["header_footer"])).lower(),
        # brand hexes used as text color, with contrast on white; WCAG: 4.5:1 body, 3:1 for >=18pt or >=14pt bold
        "brand_color_text": [dict(r, contrast_on_white=contrast(r["color"], "#ffffff")) for r in d["colored_runs"]
                             if r["color"] in spec["hexes"]][:20],
        "shaded_paragraphs": d["shaded"][:12],
        "contract_or_signature_wording": contexts(CONTRACT_RE.pattern, text),
        "price_matches": contexts(spec["price"], text, 40),
        "tax_wording": contexts(spec["tax"], text, 40),
        "tax_rate_stated": contexts(r"(?:ДДС|VAT|HST)[^.\n%]{0,25}\d{1,2}\s?%|\d{1,2}\s?%[^.\n]{0,25}(?:ДДС|VAT|HST)", text),
        "revision_count_stated": contexts(REVISION_COUNT_RE.pattern, text),
        "default_markers": {k: bool(re.search(rx, text, re.I)) for k, rx in DEFAULT_MARKERS.items()},
        "confirmation_line": contexts(r"Потвърждавам|\bI confirm\b|reply[^.\n]{0,60}confirm", text, 80, 4),
    }
    if spec.get("bad_price"):
        doc["superseded_price"] = contexts(spec["bad_price"], text)
    for group in ("agreed", "record_only"):
        if spec.get(group):
            doc[group] = {k: contexts(rx, text, 60, 4) for k, rx in spec[group].items()}
    for k, rx in spec.get("watch", {}).items():
        doc[f"watch_{k}"] = contexts(rx, text, 60)
    res["document"] = doc
    return res


def summarize(res: dict) -> str:
    d = res.get("document", {})
    bits = [f"eval-{res['eval_id']}", Path(res["run_dir"]).parent.name, Path(res["run_dir"]).name,
            f"turns={res['turns']}", f"docx={len(res['docx_files'])}", f"pdf_pages={list(res['pdf_files'].values())}"]
    if d:
        bits += [f"words={d['words']}", f"cyr={d['cyrillic_share']}", f"price={'yes' if d['price_matches'] else 'NO'}",
                 f"contract_words={len(d['contract_or_signature_wording'])}",
                 f"defaults={sum(d['default_markers'].values())}/{len(d['default_markers'])}"]
    if "seed_unchanged" in res:
        bits.append(f"seed_ok={all(res['seed_unchanged'].values())}")
    return " | ".join(bits)


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect mechanical grading evidence for project-scope eval runs.")
    ap.add_argument("--iteration", type=Path)
    ap.add_argument("--run", type=Path)
    ap.add_argument("--eval-id", type=int)
    ap.add_argument("--evals", type=Path, default=Path(__file__).with_name("evals.json"))
    args = ap.parse_args()
    evals = {e["id"]: e for e in json.loads(args.evals.read_text(encoding="utf-8"))["evals"]}
    runs = []
    if args.iteration:
        for run_dir in sorted(args.iteration.glob("eval-*/*/run-*")):
            eval_id = int(run_dir.parent.parent.name.split("-")[1])
            if eval_id in SPEC and (run_dir / "conversation.json").exists():
                runs.append((run_dir, eval_id))
    elif args.run and args.eval_id in SPEC:
        runs.append((args.run, args.eval_id))
    else:
        ap.error("give --iteration, or --run with a scope --eval-id (" + ", ".join(map(str, SPEC)) + ")")
    for run_dir, eval_id in runs:
        res = check_run(run_dir, eval_id, evals.get(eval_id, {}))
        (run_dir / "scope_checks.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print(summarize(res))


if __name__ == "__main__":
    main()
