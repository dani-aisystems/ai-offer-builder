You are grading eval runs of the skill "ai-offer-builder" and its baseline (the v2 draft), following skill-creator's grader instructions.

1. Read and follow: C:\Users\danie\.claude\plugins\marketplaces\anthropic-agent-skills\skills\skill-creator\agents\grader.md
2. Eval {eval_id} ({eval_name}). What success looks like: {expected_output}
3. Runs to grade. Grade each independently and write `<run_dir>\grading.json` for each (the viewer needs `text`, `passed`, `evidence` per expectation plus the `summary` block):
{run_list}
4. Expectations. Grade every one for every run, and copy each text exactly into the `text` field:
{expectations}

Evidence in each run directory:
- `transcript.md`: the whole conversation, rebuilt from the executor's own logs with every tool call. The executor did not write it, so treat it as ground truth.
- `conversation.json`: the same turns with full tool inputs and tool results.
- `outputs/`: the deck HTML (if any), other files the executor saved, and slide screenshots (`shot-1280-slideNN.png`). Open the screenshots with Read.
- `checks.json`: mechanical evidence:
  - language ratios, CSS hex codes and `:root` variables
  - currency strings and tax-rate mentions
  - statistics found in the deck, and whether each appears in this run's web results (`in_web_results`)
  - demo, automation and no-search checks
- `sources.json`: cited URLs fetched raw, with no summariser in between, marked verified / partial / not_found / unverifiable.
- `layout.json`: layout QA at four viewports (overflow, overlaps, contrast failures, navigation), when present.

Grading rules for this skill:
- The burden of proof is on passing.
- A statistic counts as sourced only if `checks.json` marks it `in_web_results`, or you find it yourself in this run's tool results in `conversation.json`.
  - Otherwise it passes only if it is client-supplied or a clearly labelled hypothetical: an explicit "Example" label (in the deck language) plus *if…then* framing with stated assumptions.
  - A number labelled "example" that states a fact about the industry or the market is still an unsourced fact.
- Language: read the deck text yourself. The ratios in `checks.json` are hints.
- Identity and colors: use `css_hexes` and `root_vars` from `checks.json`, and look at the screenshots.
- Contrast and layout: use `layout.json`. The contrast expectation refers to the laptop-1280x720 viewport.
- "Asked before assuming" expectations: check the order in `transcript.md`. The assistant's question has to come before the user's answer, and no client-facing copy in that dimension (language, currency) may appear before it.
- Demo runs: if you have a web search tool, search the invented business name together with its city once and report what you found.
- Evidence must be specific: quote the transcript or deck, or cite the field in `checks.json`, `sources.json` or `layout.json`.

Also fill these fields as grader.md describes:
- `claims` and `eval_feedback`
- `user_notes_summary`, from anything the executor flagged
- `execution_metrics`, from `outputs/metrics.json`
- `timing`, from `timing.json`

When done, reply with one line per run in the form `<run_dir>: X/Y passed`, followed by any expectation you think is weak or doesn't discriminate.
