#!/usr/bin/env python3
"""Generate a Playwright job for layout QA of generated decks.

Run the generated file with the Playwright MCP `browser_run_code` tool (`filename` = the file).
For each deck and viewport the job visits every slide (hidden slides measure 0x0, so each one
has to be shown first), waits for fonts and entry animations, runs layout_probe.js, checks
keyboard and on-screen navigation and the slide counter, and captures screenshots:
  - key slides (1, 2, 6, 8, 9) at 1280x720 into each run's outputs/ (the eval viewer shows them)
  - with --full, every slide at every viewport into <run_dir>/visual-qa/
It writes the JSON result to --result when the code runner allows file access, else returns it.

Usage:
  python make_layout_job.py --root <served dir> --out job.js --result result.json \
      [--base-url http://localhost:8765] <run_dir> ... [--full <run_dir> ...]
"""

import argparse
import json
import urllib.parse
from pathlib import Path

VIEWPORTS = [
    {"name": "desktop-1440x900", "width": 1440, "height": 900, "desktop": True},
    {"name": "laptop-1280x720", "width": 1280, "height": 720, "desktop": True},
    {"name": "phone-390x844", "width": 390, "height": 844, "desktop": False},
    {"name": "phone-landscape-844x390", "width": 844, "height": 390, "desktop": False},
]
KEY_SLIDES = [1, 2, 6, 8, 9]

TEMPLATE = r"""async (page) => {
  const PROBE = __PROBE__;
  const DECKS = __DECKS__;
  const VIEWPORTS = __VIEWPORTS__;
  const KEY_SLIDES = __KEY__;
  const RESULT_PATH = __RESULT__;
  const settle = async () => {
    await page.waitForTimeout(450);
    await page.evaluate(() => Promise.race([
      Promise.all(document.getAnimations().map(a => a.finished.catch(() => null))),
      new Promise(r => setTimeout(r, 1500))]));
  };
  const activeIndex = () => page.evaluate(() => Array.from(document.querySelectorAll('.slide'))
    .findIndex(x => getComputedStyle(x).display !== 'none' && x.getClientRects().length > 0));
  const out = [];
  for (const deck of DECKS) {
    const errors = [];
    // The local test server has no favicon; that 404 is the harness's, not the deck's.
    const onConsole = m => { if (m.type() === 'error' && !/favicon\.ico/.test((m.location() || {}).url || '')) errors.push(m.text().slice(0, 200)); };
    const onError = e => errors.push('pageerror: ' + String(e.message).slice(0, 200));
    page.on('console', onConsole);
    page.on('pageerror', onError);
    const deckOut = { id: deck.id, viewports: [] };
    for (const vp of VIEWPORTS) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(deck.url, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready.then(() => true));
      await page.addScriptTag({ content: PROBE });
      const total = await page.evaluate(() => document.querySelectorAll('.slide').length);
      const vpOut = { viewport: vp.name, total, problems: [], contrastFails: 0, contrastExamples: [], minFont: null };
      const visited = [];
      for (let i = 0; i < total; i++) {
        await settle();
        const r = await page.evaluate(o => window.__probeSlide(o), { desktop: vp.desktop });
        visited.push(r.index);
        if (r.issues.length) vpOut.problems.push({ slide: r.index + 1, issues: r.issues.slice(0, 6) });
        const measured = r.contrast.filter(c => c.ratio !== null);
        vpOut.contrastFails += measured.length;
        for (const c of measured) if (vpOut.contrastExamples.length < 4) vpOut.contrastExamples.push({ slide: r.index + 1, ...c });
        if (r.contrast.some(c => c.ratio === null)) vpOut.gradientNote = 'some text sits on a background image or gradient: check visually';
        if (r.minFont && (!vpOut.minFont || r.minFont.size < vpOut.minFont.size)) vpOut.minFont = { slide: r.index + 1, ...r.minFont };
        if (!vpOut.fontsUsed) vpOut.fontsUsed = r.fontsUsed;
        const n = String(i + 1).padStart(2, '0');
        if (deck.full) await page.screenshot({ path: `${deck.fullDir}/${vp.name}-slide${n}.png` });
        else if (vp.name.startsWith('laptop') && KEY_SLIDES.includes(i + 1)) await page.screenshot({ path: `${deck.keyDir}/shot-1280-slide${n}.png` });
        if (i < total - 1) await page.keyboard.press('ArrowRight');
      }
      vpOut.keyboardNavOk = total > 0 && visited.every((v, k) => v === k);
      if (vp.name.startsWith('laptop')) {
        await page.goto(deck.url, { waitUntil: 'load' });
        await settle();
        await page.keyboard.press('ArrowRight');
        await page.keyboard.press('ArrowRight');
        await settle();
        const third = await activeIndex();
        const counter = await page.evaluate(() => {
          const el = Array.from(document.querySelectorAll('[class*="counter"], [id*="counter"], [class*="count"], [id*="count"]'))
            .find(e => !e.closest('.slide') && e.textContent.trim());
          return el ? el.textContent.trim().replace(/\s+/g, ' ') : null;
        });
        await page.keyboard.press('ArrowLeft');
        await settle();
        const afterLeft = await activeIndex();
        const buttons = page.locator('button:not(.slide button)');
        const count = await buttons.count();
        const clicks = [];
        for (let b = 0; b < count; b++) {
          const btn = buttons.nth(b);
          if (!(await btn.isVisible())) continue;
          const label = (((await btn.getAttribute('aria-label')) || (await btn.innerText())) || '').trim().slice(0, 24);
          const before = await activeIndex();
          await btn.click();
          await settle();
          clicks.push({ label, delta: (await activeIndex()) - before });
        }
        vpOut.nav = { indexAfterTwoRights: third, counterText: counter, counterShows3: counter ? /\b3\b/.test(counter) : false,
          arrowLeftWorks: afterLeft === third - 1, buttons: clicks,
          nextButtonWorks: clicks.some(c => c.delta === 1), prevButtonWorks: clicks.some(c => c.delta === -1) };
      }
      deckOut.viewports.push(vpOut);
    }
    deckOut.fontsLoaded = await page.evaluate(() => Array.from(new Set(Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '')))));
    page.off('console', onConsole);
    page.off('pageerror', onError);
    deckOut.consoleErrors = errors.slice(0, 10);
    out.push(deckOut);
  }
  // The code runner has no file access, so park the results in a blank page. Save them with
  // browser_evaluate(() => JSON.stringify(window.__layoutResults), filename: ...) afterwards.
  await page.goto('about:blank');
  await page.evaluate(r => { window.__layoutResults = r; }, out);
  return `stored ${out.length} deck results in window.__layoutResults (intended file: ${RESULT_PATH})`;
}
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a Playwright layout-QA job for generated decks.")
    ap.add_argument("run_dirs", nargs="*", type=Path)
    ap.add_argument("--full", nargs="*", type=Path, default=[], help="runs that get every slide at every viewport")
    ap.add_argument("--root", type=Path, required=True, help="directory served at --base-url")
    ap.add_argument("--base-url", default="http://localhost:8765")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    args = ap.parse_args()

    probe = Path(__file__).with_name("layout_probe.js").read_text(encoding="utf-8")
    full = {p.resolve() for p in args.full}
    ordered = list(dict.fromkeys(p.resolve() for p in list(args.run_dirs) + list(args.full)))
    decks = []
    for run_dir in ordered:
        htmls = list((run_dir / "outputs").glob("*.html"))
        if not htmls:
            print(f"skip (no deck): {run_dir}")
            continue
        deck = max(htmls, key=lambda p: p.stat().st_size)
        rel = deck.relative_to(args.root.resolve()).as_posix()
        full_dir = run_dir / "visual-qa"
        if run_dir in full:
            full_dir.mkdir(exist_ok=True)
        decks.append({"id": f"{run_dir.parent.parent.name} {run_dir.parent.name} {run_dir.name}",
                      "url": f"{args.base_url}/{urllib.parse.quote(rel)}",
                      "keyDir": (run_dir / "outputs").as_posix(), "full": run_dir in full,
                      "fullDir": full_dir.as_posix()})
    js = (TEMPLATE.replace("__PROBE__", json.dumps(probe))
          .replace("__DECKS__", json.dumps(decks, ensure_ascii=False))
          .replace("__VIEWPORTS__", json.dumps(VIEWPORTS))
          .replace("__KEY__", json.dumps(KEY_SLIDES))
          .replace("__RESULT__", json.dumps(args.result.resolve().as_posix())))
    args.out.write_text(js, encoding="utf-8")
    print(f"{len(decks)} decks -> {args.out}")


if __name__ == "__main__":
    main()
