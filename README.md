# ai-offer-builder

A Claude skill for agencies that sell websites or AI automation. Tell it about a prospect and it builds three tiered packages plus a custom option, then a single-file HTML sales deck. Everything is written in the client's language and currency, under your agency's brand.

It works in Claude Code, Claude.ai, the Claude desktop app and the Claude API. MIT licensed.

## How a run goes

The skill works in six steps and waits for your approval where it matters:

0. **Agency identity.** Your name, colors, fonts, tone and contact details, returned as a block you can paste into later runs. Skip it and the deck uses a neutral placeholder look, clearly marked as such.
1. **Client context.** The business, its situation and goals, then deck language, currency, country, tax presentation and the Package 1 budget. Language and currency are asked, never guessed from the city.
2. **Research.** Web research into the client's industry and market, logged with publisher, year and URL.
3. **Packages.** Three tiers plus a custom option, shown next to the research log for your approval.
4. **Deck plan.** A ten-slide outline for your approval.
5. **Build.** One self-contained HTML file, `offer-deck-<client>.html`, with keyboard and on-screen navigation.

## What the skill enforces

- **Sourced facts only.** Industry figures come from web research and appear on slides with a source line. Every other number is client-supplied, a package price, or a labelled "Example" scenario.
- **This agency, this client.** Colors, fonts and contact details are yours, used exactly as given. Language, currency and tax come from the client.
- **Demo mode** for recordings and public showcases: an obviously fictional client, `.example` contact details, a visible demo marker, and real research.
- **The automation gate.** Tiers for AI automation offers are your own methodology, so the skill asks for them and never invents them (see below).
- **A deck that holds up on screen**: theme tokens on `:root`, WCAG contrast, and slides that fit 1280×720 without scrolling and still read on phones in portrait and landscape.

## Install

### Claude Code, as a plugin

```text
/plugin marketplace add dani-aisystems/ai-offer-builder
/plugin install ai-offer-builder@dani-aisystems
```

### Claude Code, by hand

Copy `skills/ai-offer-builder/` into `~/.claude/skills/` for all your projects, or into a project's `.claude/skills/` for that project only.

macOS / Linux:

```bash
git clone https://github.com/dani-aisystems/ai-offer-builder.git
mkdir -p ~/.claude/skills
cp -r ai-offer-builder/skills/ai-offer-builder ~/.claude/skills/
```

Windows (PowerShell):

```powershell
git clone https://github.com/dani-aisystems/ai-offer-builder.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse ai-offer-builder\skills\ai-offer-builder "$HOME\.claude\skills\"
```

### Claude.ai and the desktop app

Download `ai-offer-builder.zip` from the [latest release](https://github.com/dani-aisystems/ai-offer-builder/releases/latest) and upload it in Claude's skill settings. The zip contains `ai-offer-builder/SKILL.md` and nothing else.

### Claude API

Upload the `skills/ai-offer-builder/` folder as a custom skill through the Skills API; see the Agent Skills section of the Claude API documentation.

## Using it

Ask the way you would ask a colleague. For example:

- "Build an offer and a sales deck for a dental clinic in Kraków. They need a new website."
- "I'm recording a demo. Make up a local business and build a website offer and deck for it, prices in USD."
- "Направи оферта с пакети и презентация за автосервиз в Пловдив."

Research needs a web search tool. Without one, the skill says so and builds the deck without industry statistics.

### Website tiers

Website offers use a built-in ladder: a single-page site, a multi-page site (the recommended tier), and a multi-page site plus ads and SEO. Package 2 is priced at about 1.7–1.9× your Package 1 budget and Package 3 at about 3–3.5×, each with a first month of support free and a monthly fee after that. Change any of it in the chat before you approve the packages.

### AI automation offers

What separates the tiers of an automation offer is your own pricing methodology, so the skill doesn't guess. Before it builds anything, it asks you three questions:

1. What separates Package 1 from Package 2 from Package 3?
2. What does the middle tier's "guaranteed result" incentive look like?
3. Which questions configure a custom package?

It continues once you answer them in your own words, and it will not make tiers up for you, even for a demo. If an offer covers both a website and automation, it builds the website part straight away and adds automation once the tiers are defined.

## Repository layout

| Path | What it is |
|---|---|
| `skills/ai-offer-builder/SKILL.md` | The skill itself. This is the only file you need to use it. |
| `.claude-plugin/` | Plugin and marketplace manifests for Claude Code's `/plugin` command. |
| `evals/evals.json` | Eight multi-turn scenarios, each with a simulated-user persona and expectations. |
| `evals/prepare_iteration.py` | Freezes the skill under test and writes the run plan for one iteration. |
| `evals/run_conversation.py` | Runs each scenario as a real conversation: `claude -p` as the executor against a simulated user. |
| `evals/check_deck.py` | Mechanical evidence: language, hex codes, fonts, currency, tax mentions, and whether each deck figure appears in the run's web results. |
| `evals/verify_sources.py` | Fetches every cited page raw, with no summariser in between, and checks the cited figures are on it. |
| `evals/layout_probe.js`, `make_layout_job.py`, `split_layout_results.py` | Playwright layout QA at four viewports: overflow, overlaps, contrast, minimum font size and navigation. |
| `evals/grader_prompt.md` | Brief for the grader agents, on top of skill-creator's `grader.md`. |

## Running the evals

You need the evals only if you're changing the skill. Each run is a real conversation on your Claude usage, and a full iteration is 12 to 22 conversations, most of them with web research.

You need:

- the `claude` CLI on your PATH
- Python 3.11+
- `pypdf` for PDF sources (optional)
- the Playwright MCP server, for layout QA
- Anthropic's [skill-creator](https://github.com/anthropics/skills) skill, for grading and the benchmark

The comparison baseline is the v2 draft kept in this repo's history. Extract it once:

```bash
mkdir baseline
git archive e57b261 SKILL.md | tar -x -C baseline
```

Then run one iteration (macOS / Linux):

```bash
ws=../ai-offer-builder-workspace
python evals/prepare_iteration.py --workspace $ws --iteration 1 --new-skill skills/ai-offer-builder --old-skill baseline
python evals/run_conversation.py --evals evals/evals.json --plan $ws/iteration-1/plan.json --workers 4
python evals/check_deck.py --iteration $ws/iteration-1
python evals/verify_sources.py --iteration $ws/iteration-1
python evals/make_layout_job.py --root $ws --out .playwright-mcp/layout-job.js --result $ws/iteration-1/layout-results.json <run dirs>
```

On Windows, set `$env:PYTHONUTF8 = "1"` first, because the Polish and Bulgarian scenarios need UTF-8 console output. Write the workspace as `$ws = "..\ai-offer-builder-workspace"`; the commands are otherwise the same.

For layout QA, serve the workspace (`python -m http.server 8765 --directory <workspace>`) and run the generated job with the Playwright MCP `browser_run_code` tool. Save `window.__layoutResults` to a file and split it into the run directories with `split_layout_results.py`.

Grade each eval with `evals/grader_prompt.md`, filling `{grader_md}` with the path to skill-creator's `agents/grader.md`. Then run skill-creator's `aggregate_benchmark.py` to produce the benchmark.

## History

The first version was `web-offer-builder`. It wrote only in Bulgarian, priced everything in EUR, used one agency's gold-on-black look, and let the model write "illustrative" statistics. It's kept as the first commit for comparison. If you still have it installed, disable it: both skills trigger on the same phrases.

## License

[MIT](LICENSE)
