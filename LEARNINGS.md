# Offer system learnings

Why the skill changed, not a diary. One entry per real offer that led to system changes. Client details are left out on purpose; client-only facts stay in that client's own folder. The skill does not read this file during a run; it is for people maintaining the skill.

## 2026-09-30: restaurant website offer, rebuilt on a reference deck

**What worked**
- Using an earlier offer deck as the template: same slide sequence, components and package structure, with the client's palette and fonts taken from its own photos and logo.
- Giving the opening slides separate jobs (why it matters, what is happening, what to build).
- Checking public-listing findings against the live pages instead of asking the owner, and dropping what could not be confirmed.
- A "why us" slide before the packages, so the price lands after the trust.
- Measuring text fit with the real fonts instead of relying on one renderer.

**What needed correction, and the root cause**

| Correction | Root cause | Change |
|---|---|---|
| Earlier decks discarded; rebuild on the reference deck, one variant | The skill had no reference-deck step, so the first attempts redesigned instead of reusing | Reference-deck analysis and slide map in `workflow-and-qa.md`; "reference deck is the template" in SKILL.md and `deck-design-and-copy.md` |
| No em dashes; check marks, not dots | Existed only in a one-off client checker | Rule in the copy guide; `deck_qa.py` enforces em dashes and dot markers |
| Ads removed from packages, every feature must belong to the site | The built-in ladder put ads in the top tier, though the agency did not deliver them | Package 3 redefined as the fullest site build; ads are a separate add-on; rule added to SKILL.md and `offer-principles.md`; price re-derived from scope, ratios demoted to a sanity check |
| "Confirm it yourself or decide", "you determine" | The workflow handed open questions back to the user | SKILL.md: choose a default and say why; check findings against live sources |
| Logo on the cover instead of a venue photo | Photo rights and brand safety were not considered | Cover preference in `deck-design-and-copy.md` |
| Added a "why us" section, later rewritten around what owners look for in a designer, not around one project | No trust slide; first version over-weighted the agency's own example | Optional "why us" slide in the deck plan; principles in `offer-principles.md` |
| Rating, reservation approach, deposit and proof figures supplied late | Phase 1 never asked for terms, proof or client decisions | "Trust and terms" questions in Phase 1; estimates labelled as estimates |
| Lone words, overlap and a stray "2" on the owner's Mac | Checked only in LibreOffice; Mac apps set text wider | `fit_check.py` at several text widths; render-and-critique loop; "say which application you checked" |
| Review of the finished deck found checks that lived only in the client folder | Checker scripts were client-specific | Generalised into `scripts/deck_qa.py` and `scripts/fit_check.py` |

**Kept out of the skill on purpose (client or reference specific)**
- The client's palette, fonts, prices, figures, wording and language conventions.
- The reference deck's own visual signature (for example its cover image shape). The skill says to copy the system of whatever reference is supplied, not this one.
- A dark or light background, or any single font pairing, as a rule. Those follow the client.
