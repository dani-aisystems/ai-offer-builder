# ai-offer-builder

A public Claude skill that turns a prospect's context into three tiered packages and a PowerPoint sales deck. The skill is `skills/ai-offer-builder/SKILL.md`. It is used by many agencies, so nothing in the skill or its references may depend on one agency, client or reference deck.

## Before you plan, design or change an offer deck

Read `skills/ai-offer-builder/SKILL.md`, then the references it points to, in this order: `references/offer-principles.md`, `references/deck-design-and-copy.md`, `references/workflow-and-qa.md`. They hold the standing rules; do not rely on memory of a previous deck.

## Non-negotiables

- A reference deck is the template. Analyse it first and write a slide map. Keep its structure and system; change only the content. Nothing from the reference client survives.
- No em dashes in any deck text, notes or properties.
- Consecutive strategy slides answer different questions (why it matters, what is happening, what to build).
- Every package feature is delivered by the site build; tiers differ on real dimensions; names and prices agree everywhere.
- Every figure is sourced, client-supplied, a package figure, or a labelled hypothetical. Never invent facts.
- Render every slide and look at it. Run `skills/ai-offer-builder/scripts/deck_qa.py` and `fit_check.py`. A deck that generated without errors is not finished.
- Check marks, not dots, for included features in comparison tables.

## Working on this repo

- Changes go on a feature branch and into `main` through a pull request.
- After a skill change, re-run the eval cases that failed until they pass before committing. Keep unrelated maintenance in its own commit.
- Generated decks, client folders and eval outputs are gitignored. Do not commit client data or real agency identities; examples use fictional Example-style names.
- When a real deck gets corrections from the user, sort each one into a permanent preference, an offer-system principle, a client-only fact, or a workflow gap. Fix the workflow gap in the skill, keep client-only facts out of it, and add a short entry to `LEARNINGS.md`.
