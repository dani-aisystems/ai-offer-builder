# Workflow and QA

The order of work for a deck and the gates it must pass. Read this at the start of Phase 4, and run the QA section before calling any deck finished. A deck that was generated without errors is not yet a good deck.

## The loop

```text
Research -> Normalise the brief -> Analyse the reference deck -> Define strategy and packages
-> Map the slide narrative -> Build a first pass -> Render -> Visual critique -> Content critique
-> Reference comparison -> Fix -> Render again -> Final QA (scripts + self-critique)
```

Phases 0 to 3 in SKILL.md cover the first half. This file covers the rest.

## Reference-deck analysis (only when a reference exists)

Do this before designing anything. Open the reference (python-pptx text and geometry, plus a rendered image of every slide) and write a slide map:

| Reference slide | Purpose | Layout and components | Density | Target purpose for this client | Research that feeds it | Content |
|---|---|---|---|---|---|---|

Also record the grid and margins, title and body sizes, card style, price treatment, package structure, comparison convention, recommendation treatment, ROI structure and next-steps structure. Then every new slide is planned as: reference slide, then this client's purpose for it, then the research behind it, then the personalised content, then the build. A slide with no reference counterpart needs a stated reason and an existing component to reuse.

Show the slide map to the user inside the Phase 4 deck plan. Do not add filler slides; add one only when it does a job the reference deck leaves undone (for example "why us" before the packages).

## Slide brief, before each slide is built

Write four lines per slide in the plan: its sales purpose, the question it answers, the facts or research that support it, and what the owner should think or do after it. If two slides have the same answer to "question it answers", merge or rewrite one.

## Build

- Put all copy in one content block and all colours and fonts in the theme constants, so a fix is one edit and a rebuild.
- Build from native shapes, text boxes and tables. Keep the build script outside the deliverable folder.

## Render and critique

1. Render every slide to an image (`soffice --headless --convert-to pdf`, then `pdftoppm -png -r 110`) and look at each one. If no renderer exists, say the layout was measured and not viewed.
2. Critique visually: overlap, clipping, lone words, uneven spacing, stretched images, anything decorative without purpose, deviation from the reference.
3. Critique content: unsupported claims, repeated insights, vague copy, package names and prices that disagree between slides.
4. Fix, rebuild, render again. Repeat until a full pass finds nothing. Re-look at the slides you changed and their neighbours, not only the one you fixed.
5. A rendering in one application is not the client's view. State which application you checked, and that the deck was not opened in PowerPoint or Keynote unless it was.

## Automated checks

Two scripts live in the skill's `scripts/` folder (one level up from `references/`). They need `python-pptx`, `Pillow` and `lxml`.

- `scripts/deck_qa.py <deck.pptx> [--config qa.json]` checks the file structure and rules that a script can enforce: XML validity, slide count and 16:9 size, shapes inside the slide, distorted pictures, em dashes (slides, tables, notes, properties), placeholder and reference-deck strings, duplicate slide titles, sentences repeated across slides, package names and prices consistent across slides, check marks versus dot markers in the comparison table, prices without a figure, and contrast for the colour pairs you list. A config file lists what this deck expects: slide count, package names with prices and support fees, strings that must not appear (the reference deck's name, earlier clients, superseded prices), the slide that holds the comparison table, and contrast pairs. Run `--help` for the format.
- `scripts/fit_check.py <deck.pptx> --fonts <folder>` measures every text box with the real font files at several text widths and reports overflow, overlapping text boxes, lone-word last lines and wrapping table cells. Default widths are 100, 94 and 88 percent, which stands in for PowerPoint and Keynote setting text wider than LibreOffice.

Run both after every rebuild. Fix every finding: do not dismiss one as "probably fine" without checking the slide. A check that is new to a deck can hit a false positive; if so, fix the rule's config, not by ignoring the output.

## Self-critique gate

Before handing over, answer each question honestly against the rendered deck. Any "no" sends you back to the fix step.

**Structure**
- Does every slide deserve to exist, with one clear purpose?
- Do any two slides say essentially the same thing?
- Do the layers run in order: diagnosis, opportunity, strategy, scope, packages, recommendation, ROI, next steps?

**Research**
- Is every business-specific claim verified, supplied, or labelled as an assumption?
- Did anything get invented? Is each recommendation tied to a finding?

**Offer**
- Are the packages meaningfully different, each feature delivered by the site build?
- Does the price ladder make commercial sense, and is the recommendation justified by this client's situation?
- Do names and prices agree on every slide and in the record?

**Design**
- Does the deck read as one system, and does it respect the reference deck?
- Is spacing consistent, alignment intentional, nothing crowded or merely decorative?
- Do the scripts pass, and did you look at every rendered slide?

**Sales**
- Could the owner understand, in a few minutes, the problem, the opportunity, the solution, the options, the price, the likely value and the next action?

## Hand-over note

In the message that delivers the deck, list what the user still has to confirm: claims that rest on public listings, names of projects or people the deck cites, any default you chose, figures that are assumptions, and what you could not check (for example the deck was not opened in PowerPoint). Say which fonts need installing. Keep it short and specific.
