#!/usr/bin/env python3
"""Check cited figures against the raw source pages, with no summariser in between.

For every line of the assistant's messages that carries a URL (research logs, source lists) and
every link in the deck, fetch the page with urllib, reduce it to text (PDFs via pypdf when it is
installed) and look for each figure from that line. Writes <run_dir>/sources.json.

Statuses per source: verified (every figure found), partial, not_found, unverifiable (fetch
failed, blocked, or no text). Pages that render their text with JavaScript can come back
not_found; those deserve a rendered re-check before being called wrong.

Usage:
  python verify_sources.py --iteration <iteration_dir>
  python verify_sources.py --run <run_dir>
"""

import argparse
import gzip
import io
import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s)\]>\"'`|]+")
FIGURE_RE = re.compile(r"(?<![\w.,/])(\d{1,3}(?:[,.   ]\d{3})+|\d+(?:[.,]\d+)?)\s?(%|percent|per cent|x\b|×|million|billion|bn\b)?", re.I)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
_cache: dict = {}


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.parts = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def fetch_text(url: str) -> tuple[str, str]:
    if url in _cache:
        return _cache[url]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip", "Accept-Language": "en,*;q=0.5"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read(8_000_000)
            if resp.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            ctype = resp.headers.get("Content-Type", "")
        if "pdf" in ctype.lower() or data[:5] == b"%PDF-":
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(data))
                text = "\n".join((page.extract_text() or "") for page in reader.pages[:80])
                result = ("ok (pdf)", text)
            except Exception as exc:  # no pypdf, or an unreadable PDF
                result = (f"unverifiable (pdf: {type(exc).__name__})", "")
        else:
            parser = TextOnly()
            parser.feed(data.decode("utf-8", errors="replace"))
            result = ("ok", " ".join(parser.parts))
    except urllib.error.HTTPError as exc:
        result = (f"unverifiable (HTTP {exc.code})", "")
    except Exception as exc:
        result = (f"unverifiable ({type(exc).__name__})", "")
    _cache[url] = result
    return result


def figure_pattern(number: str, unit: str | None) -> str:
    digits = re.sub(r"[\s  ]", "", number)
    if re.fullmatch(r"\d{1,3}(?:[,.]\d{3})+", digits):
        groups = re.split(r"[,.]", digits)
        core = r"[,.\s  ]?".join(groups)
    elif re.fullmatch(r"\d+[.,]\d+", digits):
        a, b = re.split(r"[.,]", digits)
        core = rf"{a}[.,]{b}"
    else:
        core = re.escape(digits)
    if unit and unit.strip() in ("%", "percent", "per cent"):
        return rf"(?<![\d.,]){core}\s?(?:%|percent|per cent)"
    return rf"(?<![\d.,]){core}(?!\d)"


def figures_in(line: str) -> list[dict]:
    stripped = URL_RE.sub(" ", line)
    stripped = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s+", " ", stripped)  # list numbering
    out = []
    for m in FIGURE_RE.finditer(stripped):
        number, unit = m.group(1), m.group(2)
        plain = re.sub(r"[^\d]", "", number)
        if not unit and re.fullmatch(r"(19[89]\d|20[0-3]\d)", plain):
            continue  # a year, not a figure
        if not unit and len(plain) < 2:
            continue
        out.append({"figure": m.group(0).strip(), "pattern": figure_pattern(number, unit)})
    return out


def collect_citations(run_dir: Path) -> list[dict]:
    conv = json.loads((run_dir / "conversation.json").read_text(encoding="utf-8"))
    cites = []
    for t in conv:
        for item in t["items"]:
            if item["kind"] != "text":
                continue
            for line in item["text"].splitlines():
                for url in URL_RE.findall(line):
                    cites.append({"turn": t["turn"], "url": url.rstrip(".,;:"), "line": line.strip()[:400],
                                  "figures": figures_in(line)})
    return cites


def verify_run(run_dir: Path) -> dict:
    cites = collect_citations(run_dir)
    results = []
    for c in cites:
        status, text = fetch_text(c["url"])
        found = [{"figure": f["figure"], "found": bool(re.search(f["pattern"], text, re.I))} for f in c["figures"]] if text else []
        if not text:
            verdict = status
        elif not c["figures"]:
            verdict = "fetched (no figures on this line)"
        elif all(f["found"] for f in found):
            verdict = "verified"
        elif any(f["found"] for f in found):
            verdict = "partial"
        else:
            verdict = "not_found"
        results.append({**{k: c[k] for k in ("turn", "url", "line")}, "fetch": status, "verdict": verdict, "figures": found})
    summary = {}
    for r in results:
        key = r["verdict"].split(" (")[0]
        summary[key] = summary.get(key, 0) + 1
    out = {"run_dir": str(run_dir), "citations": len(results), "summary": summary, "results": results}
    (run_dir / "sources.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify cited figures against raw source pages.")
    ap.add_argument("--iteration", type=Path)
    ap.add_argument("--run", type=Path)
    args = ap.parse_args()
    if args.iteration:
        runs = [p for p in sorted(args.iteration.glob("eval-*/*/run-*")) if (p / "conversation.json").exists()]
    elif args.run:
        runs = [args.run]
    else:
        ap.error("give --iteration or --run")
    for run_dir in runs:
        res = verify_run(run_dir)
        print(f"{run_dir.parent.parent.name} {run_dir.parent.name} {run_dir.name}: {res['citations']} citations {res['summary']}")


if __name__ == "__main__":
    main()
