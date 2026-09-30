#!/usr/bin/env python3
"""Text-fit check for an offer deck (.pptx), independent of any one renderer.

Usage: fit_check.py DECK.pptx --fonts FOLDER [factor ...]

Measures every text box with the real font files in FOLDER and wraps it the way PowerPoint and Keynote
do. Those apps often set text wider than LibreOffice (non-Latin scripts most of all), so each box is
tested at several width factors: text is inflated by 1/factor. Defaults: 1.0 0.94 0.88.
Flags:
  - a wrapped text box whose text needs more height than the box has (overflow)
  - two text boxes whose rendered areas overlap
  - an orphan: the last line of a wrapped paragraph is one short word or number
  - a table cell that wraps

FOLDER holds .ttf or .otf files. Fonts are matched by the family and style names inside the files, so
"Manrope" and bold resolve to Manrope Bold. A run whose font is not in FOLDER is measured with the first
regular font found there, and the script says so: add the real file to get a real answer.
Exit code 0 when nothing is flagged, 1 otherwise. Needs python-pptx and Pillow.
"""
import argparse
import glob
import os
import sys

from PIL import ImageFont
from pptx import Presentation
from pptx.util import Emu

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
_fonts = {}      # (family lower, bold) -> path
_cache = {}
_missing = set()


def load_fonts(folder):
    paths = glob.glob(os.path.join(folder, "**", "*.ttf"), recursive=True) + glob.glob(os.path.join(folder, "**", "*.otf"), recursive=True)
    for path in sorted(paths):
        try:
            family, style = ImageFont.truetype(path, 12).getname()
        except OSError:
            continue
        bold = "bold" in style.lower() or "black" in style.lower() or "heavy" in style.lower()
        italic = "italic" in style.lower() or "oblique" in style.lower()
        if not italic:
            _fonts.setdefault((family.lower(), bold), path)
    if not _fonts:
        sys.exit(f"no usable .ttf or .otf files found in {folder}")


def font(name, bold, px):
    key = (name.lower(), bold)
    path = _fonts.get(key) or _fonts.get((name.lower(), False))
    if path is None:
        if name not in _missing:
            _missing.add(name)
            print(f"note: font {name!r} not found in the fonts folder; measured with a stand-in, result is approximate")
        path = next(iter(_fonts.values()))
    if (path, px) not in _cache:
        _cache[(path, px)] = ImageFont.truetype(path, px)
    return _cache[(path, px)]


def tokens(par, default_name, default_size=14):
    """(text, font name, bold, size pt, spacing pt) for each word of a paragraph."""
    out = []
    for r in par.runs:
        f = r.font
        size = f.size.pt if f.size else default_size
        name = f.name or default_name
        rpr = r._r.rPr
        spc = int(rpr.get("spc", 0)) / 100 if rpr is not None else 0
        parts = r.text.replace(" ", " ").split(" ")
        for i, w in enumerate(parts):
            out.append((w + (" " if i < len(parts) - 1 else ""), name, bool(f.bold), size, spc))
    return out


def width_pt(tok):
    text, name, bold, size, spc = tok
    return font(name, bold, int(size * 10)).getlength(text) / 10 + spc * len(text)


def wrap(par, box_pt, factor, default_name):
    lines, cur, cw = [], [], 0.0
    for t in tokens(par, default_name):
        w = width_pt(t) / factor
        if cur and cw + width_pt((t[0].rstrip(), *t[1:])) / factor > box_pt:
            lines.append(cur)
            cur, cw = [], 0.0
        cur.append(t)
        cw += w
    lines.append(cur)
    return lines


def line_height(tok, mult):
    ascent, descent = font(tok[1], tok[2], int(tok[3] * 10)).getmetrics()
    return (ascent + descent) / 10 * mult


def para_mult(par):
    el = par._p.find(".//a:lnSpc/a:spcPct", NS)
    return int(el.get("val")) / 100000 if el is not None else 1.0


def insets_pt(shape):
    body = shape.text_frame._txBody.find("a:bodyPr", NS)
    left = int(body.get("lIns", 91440)) / 12700
    right = int(body.get("rIns", 91440)) / 12700
    return left + right


def analyse(shape, factor, default_name):
    """Return (lines, needed height in, ink height in, orphan). Overlap is judged on ink height."""
    box_pt = Emu(shape.width).inches * 72 - insets_pt(shape)
    total = ink = 0.0
    lines_out, orphan = [], None
    for par in shape.text_frame.paragraphs:
        if not par.runs:
            continue
        lines = wrap(par, box_pt, factor, default_name)
        mult = para_mult(par)
        total += sum(max(line_height(t, mult) for t in ln) for ln in lines)
        ink += sum(max(t[3] for t in ln) * 1.15 * mult for ln in lines)
        lines_out += ["".join(t[0] for t in ln).rstrip() for ln in lines]
        if len(lines) > 1:
            last = "".join(t[0] for t in lines[-1]).strip()
            last_w = sum(width_pt(t) for t in lines[-1]) / factor
            if " " not in last.replace(" ", "x") and last_w < 0.35 * box_pt:
                orphan = last
    return lines_out, total / 72, ink / 72, orphan


def rect_of(shape, needed_in):
    x, y, w, h = (Emu(v).inches for v in (shape.left, shape.top, shape.width, shape.height))
    anchor = shape.text_frame._txBody.find("a:bodyPr", NS).get("anchor", "t")
    if anchor == "ctr":
        return x, y + (h - needed_in) / 2, w, needed_in
    return x, y, w, needed_in


def walk(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from walk(sh.shapes)
        else:
            yield sh


def main(deck, factors):
    prs = Presentation(deck)
    default_name = next(iter(_fonts))[0].title()
    issues = 0
    for fac in factors:
        print(f"--- width factor {fac} (text {round((1 / fac - 1) * 100)}% wider)")
        for n, slide in enumerate(prs.slides, 1):
            boxes = []
            for sh in walk(slide.shapes):
                if getattr(sh, "has_table", False) and sh.has_table:
                    for ri, row in enumerate(sh.table.rows):
                        for ci, cell in enumerate(row.cells):
                            cw = Emu(sh.table.columns[ci].width).inches * 72 - 7.2  # default 0.05 in cell margins
                            for par in cell.text_frame.paragraphs:
                                if par.runs and len(wrap(par, cw, fac, default_name)) > 1:
                                    print(f"  s{n} table r{ri}c{ci}: cell wraps: {cell.text!r}")
                                    issues += 1
                    continue
                if not sh.has_text_frame or not sh.text_frame.text.strip():
                    continue
                lines, need, ink, orphan = analyse(sh, fac, default_name)
                height = Emu(sh.height).inches
                label = sh.text_frame.text.replace("\n", " / ")[:46]
                if len(lines) > 1 and need > height + 0.03:
                    print(f"  s{n} overflow {need:.2f} > {height:.2f} in: {label!r}")
                    issues += 1
                if orphan:
                    print(f"  s{n} orphan word {orphan!r}: {label!r}")
                    issues += 1
                boxes.append((rect_of(sh, ink), label))
            for i in range(len(boxes)):
                for j in range(i + 1, len(boxes)):
                    (x1, y1, w1, h1), l1 = boxes[i]
                    (x2, y2, w2, h2), l2 = boxes[j]
                    if x1 < x2 + w2 - 0.02 and x2 < x1 + w1 - 0.02 and y1 < y2 + h2 - 0.02 and y2 < y1 + h1 - 0.02:
                        print(f"  s{n} overlap: {l1!r} x {l2!r}")
                        issues += 1
    print("issues:", issues)
    return 1 if issues else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Text-fit check for an offer deck (.pptx). See the file header.")
    ap.add_argument("deck")
    ap.add_argument("--fonts", required=True, help="folder with the deck's .ttf or .otf files")
    ap.add_argument("factors", nargs="*", type=float, help="width factors (default 1.0 0.94 0.88)")
    a = ap.parse_args()
    load_fonts(a.fonts)
    sys.exit(main(a.deck, a.factors or [1.0, 0.94, 0.88]))
