#!/usr/bin/env python3
"""Mechanical QA for an offer deck (.pptx).

Usage: deck_qa.py DECK.pptx [--config qa.json] [--fix-app-xml]

Checks that do not need a config:
  - every XML part parses; slide size is 13.333 x 7.5 in; no shape leaves the slide
  - pictures are not distorted
  - no em dash in slide text, tables, speaker notes or document properties
  - no placeholder text (TODO, Lorem, [Your ..., xxx); example.com only when "demo" is true
  - no two slides share a title; no long sentence appears on exactly two content slides
  - a comparison table uses check marks, not dot or bullet markers

With a config (JSON), it also checks:
  {
    "slides": 12,                          expected slide count
    "demo": false,                         demo decks may use example.com
    "packages": [                          as they must be written on the slides
      {"name": "Foundation", "price": "750 EUR", "support": "35 EUR", "slide": 6}
    ],
    "comparison_slide": 9,                 lists every package name and price; needs check marks
    "recommended": {"name": "Growth", "slides": [11]},   name and price must appear on these
    "banned": ["Reference Deck Name", "Earlier Client"], strings that must not appear anywhere
    "banned_regex": ["(?<!\\d)600 EUR"],   superseded prices and the like
    "content_slides": [2, 3, 4, 5],        slides scanned for repeated sentences (default: all but first and last)
    "contrast": [["1E0F07", "F6EEDF", 4.5, "text on page"]]   [text hex, background hex, minimum, label]
  }

Whitespace and non-breaking spaces are treated as equal when matching prices.
--fix-app-xml escapes the bare ampersand pptxgenjs writes into docProps/app.xml (company name).
Exit code 0 when nothing is wrong, 1 otherwise. Needs python-pptx, Pillow and lxml.
"""
import argparse
import io
import json
import re
import shutil
import sys
import tempfile
import zipfile

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Emu

EM_DASH = chr(0x2014)
PLACEHOLDERS = ["TODO", "Lorem", "[Your", "xxx", "[phone]", "[website]", "[Agency"]
DOT_MARKERS = ["•", "●", "·", "○"]  # bullet, black circle, middle dot, white circle


def norm(s):
    return re.sub(r"\s+", " ", s.replace(" ", " ").replace(" ", " ")).strip()


def fix_app_xml(path):
    tmp = tempfile.mktemp(suffix=".pptx")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/app.xml":
                text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", data.decode("utf-8"))
                data = text.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)


def luminance(hex_):
    ch = [int(hex_[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def shape_texts(shape):
    """Yield every text string in a shape, including table cells and grouped shapes."""
    if shape.shape_type == 6:  # group
        for sub in shape.shapes:
            yield from shape_texts(sub)
        return
    if shape.has_text_frame:
        yield shape.text_frame.text
    if getattr(shape, "has_table", False) and shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                yield cell.text


def table_cells(slide):
    for shape in slide.shapes:
        if getattr(shape, "has_table", False) and shape.has_table:
            for row in shape.table.rows:
                yield [cell.text for cell in row.cells]


def slide_title(slide):
    """The text of the largest-font run on the slide, which is the title in a normal layout."""
    best, title = 0, ""
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for par in shape.text_frame.paragraphs:
            for run in par.runs:
                size = run.font.size.pt if run.font.size else 0
                if size > best and run.text.strip():
                    best, title = size, shape.text_frame.text.strip()
    return norm(title)


def run(deck, cfg, fix):
    problems = []
    if fix:
        fix_app_xml(deck)
    with zipfile.ZipFile(deck) as z:
        for name in z.namelist():
            if name.endswith((".xml", ".rels")):
                try:
                    etree.fromstring(z.read(name))
                except etree.XMLSyntaxError as e:
                    problems.append(f"XML parse error in {name}: {e}")

    prs = Presentation(deck)
    width, height = prs.slide_width, prs.slide_height
    count = len(prs.slides)
    if "slides" in cfg and count != cfg["slides"]:
        problems.append(f"expected {cfg['slides']} slides, found {count}")
    if (round(Emu(width).inches, 3), round(Emu(height).inches, 3)) != (13.333, 7.5):
        problems.append("slide size is not 13.333 x 7.5 in (16:9)")

    props = prs.core_properties
    for label, value in (("title", props.title), ("author", props.author), ("subject", props.subject)):
        if value and EM_DASH in value:
            problems.append(f"em dash in document property {label}")

    banned = list(cfg.get("banned", [])) + PLACEHOLDERS
    if not cfg.get("demo"):
        banned.append("example.com")
    banned_regex = cfg.get("banned_regex", [])

    texts, titles, sentences = {}, {}, {}
    content = cfg.get("content_slides") or list(range(2, max(count, 2)))
    for i, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.left is None:
                continue
            if shape.left < 0 or shape.top < 0 or shape.left + shape.width > width + 12700 or shape.top + shape.height > height + 12700:
                problems.append(f"slide {i}: shape '{shape.name}' extends outside the slide")
            if shape.shape_type == 13:  # picture
                image = Image.open(io.BytesIO(shape.image.blob))
                src, box = image.width / image.height, shape.width / shape.height
                cropped = any(getattr(shape, a, 0) for a in ("crop_left", "crop_right", "crop_top", "crop_bottom"))
                if not cropped and abs(src - box) / src > 0.01:
                    problems.append(f"slide {i}: picture '{shape.name}' is distorted (image {src:.3f}, frame {box:.3f})")
        parts = [t for shape in slide.shapes for t in shape_texts(shape)]
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        text = "\n".join(parts)
        texts[i] = norm(text)
        for where, body in (("slide", text), ("notes", notes)):
            if EM_DASH in body:
                problems.append(f"slide {i}: em dash in {where} text")
        for b in banned:
            if b.lower() in (text + "\n" + notes).lower():
                problems.append(f"slide {i}: banned string {b!r}")
        for pattern in banned_regex:
            if re.search(pattern, text.replace(" ", " ")) or re.search(pattern, text):
                problems.append(f"slide {i}: matches banned pattern {pattern!r}")

        title = slide_title(slide)
        if title and i > 1:
            if title in titles:
                problems.append(f"slides {titles[title]} and {i}: same title {title!r}")
            titles[title] = i
        if i in content:
            for part in parts:
                for sentence in re.split(r"(?<=[.!?])\s+|\n", part):
                    sentence = norm(sentence)
                    if len(sentence) > 40:
                        sentences.setdefault(sentence, set()).add(i)

    # A sentence on exactly two slides is duplicated copy. One on three or more is a template label
    # or footer (package slides repeat their price note), which is deliberate.
    for sentence, where in sentences.items():
        if len(where) == 2:
            a, b = sorted(where)
            problems.append(f"slides {a} and {b}: repeated sentence {sentence[:60]!r}")

    comparison = cfg.get("comparison_slide")
    if comparison:
        slide = prs.slides[comparison - 1]
        cells = [c for row in table_cells(slide) for c in row]
        marks = sum(c.count("✓") + c.count("✔") for c in cells)
        dots = [c for c in cells if any(d in c for d in DOT_MARKERS)]
        if not cells:
            problems.append(f"slide {comparison}: no native table found for the comparison")
        if marks == 0:
            problems.append(f"slide {comparison}: comparison table has no check marks")
        if dots:
            problems.append(f"slide {comparison}: dot or bullet markers in the comparison table: {dots[:3]}")

    for pkg in cfg.get("packages", []):
        name = pkg["name"]
        price, support = norm(pkg["price"]), norm(pkg.get("support", ""))
        slide_no = pkg.get("slide")
        if slide_no:
            body = texts[slide_no]
            for label, value in (("name", name), ("price", price), ("support fee", support)):
                if value and value not in body:
                    problems.append(f"slide {slide_no}: package {name} {label} {value!r} missing")
        if comparison:
            body = texts[comparison]
            for label, value in (("name", name), ("price", price), ("support fee", support)):
                if value and value not in body:
                    problems.append(f"slide {comparison}: comparison lacks {name} {label} {value!r}")
    rec = cfg.get("recommended")
    if rec:
        match = next((p for p in cfg.get("packages", []) if p["name"] == rec["name"]), None)
        for n in rec.get("slides", []):
            if rec["name"] not in texts[n]:
                problems.append(f"slide {n}: recommended package {rec['name']!r} missing")
            if match and norm(match["price"]) not in texts[n]:
                problems.append(f"slide {n}: recommended package price {match['price']!r} missing")

    for fg, bg, need, label in cfg.get("contrast", []):
        ratio = contrast(fg, bg)
        if ratio < need:
            problems.append(f"contrast {label}: {ratio:.2f} is below {need}")

    print(f"slides: {count} | title: {props.title} | author: {props.author}")
    return problems


def main():
    ap = argparse.ArgumentParser(description="Mechanical QA for an offer deck (.pptx). See the file header for the config format.")
    ap.add_argument("deck")
    ap.add_argument("--config", help="JSON file describing what this deck must contain")
    ap.add_argument("--fix-app-xml", action="store_true", help="escape bare ampersands in docProps/app.xml before checking")
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding="utf-8")) if args.config else {}
    problems = run(args.deck, cfg, args.fix_app_xml)
    if problems:
        print("problems:")
        for p in problems:
            print("  -", p)
        return 1
    print("problems: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
