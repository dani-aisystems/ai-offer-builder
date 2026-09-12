# ai-offer-builder

A Claude skill for agencies. It turns what you know about a prospect into three tiered packages plus a custom option, then into a single-file HTML sales deck. It covers website builds and AI automation/services, and writes in the client's language and currency under the agency's own brand.

It replaces `web-offer-builder`, which hardcoded Bulgarian, EUR and one agency's gold-on-black look, and let the model write "illustrative" statistics.

## What the skill enforces

- **Sourced facts only.** Industry figures come from web research, are logged with publisher, year and URL, and appear on slides with a source line. Anything else is a client-supplied number, a package price, or a labelled "Example" scenario.
- **This agency, this client.** Agency identity (colors, fonts, contact, logo) is collected once and reused. Deck language, currency and tax presentation are asked, never inferred from a city.
- **A neutral fallback** when no identity is given, announced in chat and marked in the HTML.
- **Demo mode** for recordings: an obviously fictional client, `.example` contacts, a visible demo marker, and real research.
- **The automation gate.** Tier logic for AI automation/service offers is the agency's own methodology. Until the user defines it in their own words, the skill stops and asks, in every mode, and never proposes a ladder to pick from.
- **A deck that holds up on screen**: theme tokens on `:root`, WCAG contrast, and slides that fit 1280×720 without scrolling and still read at 390×844 and 844×390.

## Repository layout

| Path | What it is |
|---|---|
| `SKILL.md` | The skill itself. |
| `evals/evals.json` | Eight multi-turn scenarios, each with a simulated-user persona and expectations. |
| `evals/prepare_iteration.py` | Freezes the skill under test and writes the run plan for one iteration. |
| `evals/run_conversation.py` | Runs each scenario as a real conversation: `claude -p` as the executor against a simulated user. |
| `evals/check_deck.py` | Mechanical evidence: language, hex codes, fonts, currency, tax mentions, and whether each deck figure appears in the run's web results. |
| `evals/verify_sources.py` | Fetches every cited page raw, with no summariser in between, and checks the cited figures are on it. |
| `evals/layout_probe.js`, `make_layout_job.py`, `split_layout_results.py` | Playwright layout QA at four viewports: overflow, overlaps, contrast, minimum font size and navigation. |
| `evals/grader_prompt.md` | Brief for the grader agents, on top of skill-creator's `grader.md`. |

## Installing the skill

Package only `SKILL.md`: copy it into a folder named `ai-offer-builder` and run skill-creator's `package_skill.py` on that folder. Upload the resulting `ai-offer-builder.skill` in Claude, then disable `web-offer-builder`, which triggers on the same phrases.

## Running the evals

The runs use your Claude usage. A full iteration is 12 to 22 conversations, most of them with web research.

```powershell
$env:PYTHONUTF8 = "1"   # the scripts read and write UTF-8 (Polish and Bulgarian scenarios)
$ws = "..\ai-offer-builder-workspace"
python evals/prepare_iteration.py --workspace $ws --iteration 1 --new-skill . --old-skill <baseline-skill-dir>
python evals/run_conversation.py --evals evals/evals.json --plan $ws/iteration-1/plan.json --workers 4
python evals/check_deck.py --iteration $ws/iteration-1
python evals/verify_sources.py --iteration $ws/iteration-1
python evals/make_layout_job.py --root $ws --out .playwright-mcp/layout-job.js --result $ws/iteration-1/layout-results.json <run dirs>
```

Run the generated layout job with the Playwright MCP `browser_run_code` tool. Then save `window.__layoutResults` and split it with `split_layout_results.py`. Grading follows `evals/grader_prompt.md`, and `aggregate_benchmark.py` from skill-creator produces the benchmark.

You need:
- the `claude` CLI on PATH
- Python 3.11+
- `pypdf` for PDF sources (optional)
- the Playwright MCP server, for layout QA
