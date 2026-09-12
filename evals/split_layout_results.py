#!/usr/bin/env python3
"""Split a saved layout-QA result (from make_layout_job.py) into one layout.json per run.

The job identifies each deck as "<eval dir> <config> <run>", which maps back to
<iteration_dir>/<eval dir>/<config>/<run>/layout.json. Prints a one-line summary per deck.

Usage:
  python split_layout_results.py --results layout-results.json --iteration <iteration_dir>
"""

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Split layout-QA results into per-run layout.json files.")
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--iteration", type=Path, required=True)
    args = ap.parse_args()
    raw = json.loads(args.results.read_text(encoding="utf-8"))
    decks = json.loads(raw) if isinstance(raw, str) else raw  # browser_evaluate may save a JSON string
    for deck in decks:
        eval_dir, config, run = deck["id"].split(" ")
        run_dir = args.iteration / eval_dir / config / run
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "layout.json").write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
        parts = []
        for vp in deck["viewports"]:
            nav = vp.get("nav")
            nav_ok = "" if nav is None else f" nav(next={nav['nextButtonWorks']},prev={nav['prevButtonWorks']},counter={nav['counterShows3']})"
            parts.append(f"{vp['viewport']}: {len(vp['problems'])} slides with issues, {vp['contrastFails']} contrast fails,"
                         f" keys={'ok' if vp['keyboardNavOk'] else 'BROKEN'}{nav_ok}")
        print(f"{deck['id']}: console errors={len(deck['consoleErrors'])} fonts={deck.get('fontsLoaded')}")
        for p in parts:
            print("   " + p)


if __name__ == "__main__":
    main()
