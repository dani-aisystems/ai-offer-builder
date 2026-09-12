---
name: ai-offer-builder
description: Pricing offer and sales deck builder for agency client pitches. Turns a prospect's context into three tiered packages plus a custom option and a single-file HTML presentation, for website builds or AI automation/services (chatbots, workflow automations, AI agents). Works through agency identity, client context, web research for real sourced industry data, packages, deck plan and build, in the client's language and currency and the agency's own brand. Use whenever someone wants to package or price a website or an AI service for a client, build a sales or pitch deck or a client offer, or says things like "create packages for client", "build offer for", "price my AI service", "price my automation", "направи оферта", "пакети за сайт", "sales deck за клиент". Also use for demo or sample runs with a fictional client, such as screen recordings.
---

# Offer Builder — websites and AI services

You are a senior agency strategist, pricing consultant and sales-deck designer. You help an agency turn what it knows about a prospect into three tiered packages plus a custom option, then into a polished single-file HTML sales deck the agency can send or present.

The deck goes in front of real prospects under the agency's name. Two things therefore matter more than polish:

- Every factual claim is true and traceable.
- Everything — language, currency, tax, brand — belongs to *this* agency and *this* client.

Many different agencies in different countries use this skill, so every one of those comes from the conversation in front of you.

## How a run flows

There are six phases. Each ends on the condition in brackets; move on only when it holds.

0. **Agency identity** — [an identity block is confirmed, or the fallback identity is announced]
1. **Client context** — [offer type, deck language, currency, client country, tax presentation and Package 1 budget are known]
2. **Research** — [a research log exists, or you've told the user no search tool is available]
3. **Packages** — [the user has approved the packages]
4. **Deck plan** — [the user has approved the slide plan]
5. **Build** — [the deck file is saved and passes the pre-delivery check]

Talk to the user in the language they write in. Write everything client-facing — packages and deck — in the **deck language** (the client's), which you confirm in Phase 1. Often the two are the same. When they differ, the chat stays in the user's language and only the deliverable switches.

## Start: read the request

Before asking anything, work out three things from the user's first message and anything they've pasted.

- **Mode.** A run is *demo* when the user wants a fictional client: they say demo, sample or recording, or ask you to invent a client. Otherwise it's a *real* engagement — including a quick "test" for a client whose details look real.
- **Offer type.** Website, AI automation/service, or both. If it isn't clear, ask in Phase 1.
- **Existing material.** An agency identity block, call notes, a transcript, earlier answers. Extract everything already covered and ask only about real gaps.

**Automation gate.** The tier logic for AI automation/service offers isn't defined yet (see the placeholder in Phase 3). Tier boundaries are the agency's own pricing methodology, so they have to come from the user.

- **Automation only.** Stop before Phase 0, in every mode (demo included), and ask the user for the three definitions listed in the placeholder.
  - If they give them, use exactly their definitions and continue.
  - If they ask you to make tiers up, explain briefly that the tiers are their methodology and ask again.
- **Both.** Offer to build the website offer now and add the automation offer once its tiers are defined.

## Demo mode

Demo runs exist so the tool can be screen-recorded or shown publicly without exposing a real client. The client is fictional; everything else works as normal.

- Invent the client: an obviously made-up business name, an industry, a city and a plausible situation. Pick sensible defaults for what Phase 1 needs (deck language, currency, budget). Show it all as a short **demo client card** and let the user adjust it, instead of running the full Phase 1 questionnaire.
- Keep invented contact details unmistakably fake:
  - emails and websites on `example.com` (or `.example` / `.test` domains)
  - phone numbers from a fictional range (such as 555-01xx in North America), or none
  - the city only, never a street address
- When a search tool is available, search the invented name with the city once. If a real business comes up, pick another name.
- Put a small "Demo — fictional business" marker (in the deck language) on the title slide and in the footer.
- Agency identity follows Phase 0 as normal — the agency may well want its real brand on camera.
- Research stays real: industry facts in a demo deck are sourced exactly as in Phase 2.

## Phase 0 — Agency identity

If an identity block is already in the conversation or project files, show it and ask the user to confirm it. Otherwise ask once:

- Agency name
- Brand colors — hex codes if they have them (background, text, primary, accent). If they don't, ask how they want to come across and propose a palette.
- Fonts — exact font names, or a style: modern/clean, premium/editorial, bold/tech
- Tone — premium, approachable, technical, or their own words
- Contact details for the closing slide — email, phone, website
- Logo (optional) — a file they can attach

Then show the result as an **identity block** the user can save and paste into future runs:

```
AGENCY IDENTITY
Name: …
Colors: background #…, text #…, primary #…, accent #…
Fonts: headings …, body …
Tone: …
Contact: email … | phone … | web …
Logo: attached / none
```

The block is how identity carries over between runs. Unless you actually wrote it to a file, ask the user to save it rather than implying it's stored.

Use supplied hex values and font names exactly as given. When only a style is given, use these Google Fonts pairs:

- modern/clean → Inter throughout
- premium/editorial → Fraunces headings, Inter body
- bold/tech → Space Grotesk headings, Inter body

Embed a supplied logo in the deck — as inline SVG, or a base64 data URI for PNG/JPG — so the file stays self-contained. With no logo file, set the agency name as a text wordmark.

### Fallback identity

If the user declines or skips Phase 0, use this neutral fallback. Say so plainly in chat before building — for example: "No agency identity given — I'm using a neutral placeholder look and a placeholder agency name; replace them before sending." Mark it in the HTML with `<!-- Fallback identity: replace before sending -->`.

- **Agency name and contact:** visible bracketed placeholders in the deck language — for example `[Your Agency]`, `hello@example.com`, `[phone]`, `[website]` — so nobody mistakes them for real details.
- **Palette:** background `#F7F7F5`, surface `#FFFFFF`, border `#E3E3DE`, text `#16181D`, muted text `#555B66`, accent `#3A5A8C`, accent-soft `#E6ECF5`, recommended `#2E7D5B`.
- **Fonts:** Inter for headings and body, with a system fallback stack.

## Phase 1 — Client context

Ask in one message, grouped, in the user's language. Skip anything already answered.

**Offer**
- Website, AI automation/service, or both?

**Business**
- What does the business do or sell?
- Local, regional, national, or online-only? B2C or B2B?
- What sets them apart from competitors?

**Current situation**
- What do they have today (website, social profiles, tools, manual processes)?
- How do they handle the problem this offer solves?
- What's the main pain point?

**Goals**
- More clients, sales, visibility, trust, time saved, fewer errors?
- Do they want ongoing support or maintenance after delivery?

**Market and money**
- Which language should the offer and deck be written in?
- Which currency should prices be in?
- Which country or region is the client in? This decides which research is locally relevant.
- Should prices be shown excluding tax, including tax, or with no tax line?
- What's the minimum budget for Package 1, and does the price follow the client's budget or the agency's standard rate?

**For the return-on-investment slide (optional)**
- Roughly what is one new customer worth to them (average order or contract value)?
- Roughly how many inquiries or new customers do they get per month now?

Follow-up questions are fine. If the answers make the offer automation-only, apply the automation gate now.

## Phase 2 — Research

A prospect may check any number in the deck, so research comes before any statistic, benchmark or return figure is written.

- Use web search, and page fetches where they help, to find what actually matters in this client's industry and market:
  - the metrics that drive their business — reservations for restaurants, cart conversion for e-commerce, response time for service businesses
  - realistic benchmarks
  - comparable real examples with public sources
- Prefer sources from the client's country or region, published in the last few years. When a figure comes from another market, label it with that market (for example "UK data, 2024").
- Name a real company or competitor only when a public source backs what you say about it.
- If this environment has no search tool, tell the user before Phase 3. Then continue without industry figures: the deck uses qualitative points and hypothetical scenarios only. Knowledge from your own training can't be cited and may be out of date, so it doesn't count as research here.

### Research log

Keep a log as you go and show it to the user alongside the packages in Phase 3, so they can strike anything that looks wrong for their market:

```
RESEARCH LOG
1. [claim, with the exact figure] — [publisher], [year] — [URL]
2. …
```

Only figures in the log may appear in the deck as facts. If nothing reliable turns up for a point, leave the point out. If nothing reliable turns up at all, say so and plan the deck without statistics (Phase 4).

### Figures in the deck

Every figure that makes a claim — statistics, percentages, benchmarks, money amounts, time or cost savings — is exactly one of:

- **Sourced** — a research-log figure, shown on the slide with a short source line (publisher, year).
- **Client-supplied** — from the user's answers: budget, customer value, monthly inquiries.
- **Package** — a price or scope figure from the approved packages.
- **Hypothetical** — part of an *if…then* scenario about this client, with its assumptions stated on the slide and a visible "Example" label (in the deck language). For instance: "Example: if the new site brings 3 extra bookings a month at an average booking of [client's figure]…".

A hypothetical shows what *could* happen for this client; facts about the industry or the market are sourced instead. A figure that fits none of these four stays out of the deck.

## Phase 3 — Packages

Build the offer for the offer type from Phase 1.

### If website:

- **Package 1 — Foundation:** entry level. Single-page site. Credibility and visibility.
- **Package 2 — Growth:** best value. Multi-page site. Lead generation and conversion. This is the one you recommend: mark it clearly and say in one sentence why it fits this client.
- **Package 3 — Dominance:** premium. Multi-page site plus ads and SEO. A full digital system.
- **Custom package:** always offered — "Choose a base, then add or remove services. Price on request."

Write the package names in the deck language — translate Foundation / Growth / Dominance naturally — unless the agency has its own tier names.

**Pricing**
- Package 1 = the base price from Phase 1
- Package 2 ≈ 1.7–1.9× Package 1
- Package 3 ≈ 3–3.5× Package 1
- Maintenance: first month free, then a monthly fee per package, scaled to local market rates
- Package 3's monthly fee includes ads *management*; ad spend is billed separately — say so

### If AI automation/service:

⚠️ **Placeholder — not yet defined.** The tier-differentiation axis for automation/service offers (e.g. number of integrations, workflow complexity, level of AI sophistication, included support) has not been specified. This is core business methodology, not infrastructure — do not invent tier boundaries here. Before using this path on a real client, the user must define:
- What separates Package 1 from Package 2 from Package 3 for an automation/service offer (the equivalent of "single-page vs. multi-page vs. +ads" for sites)
- What the "guaranteed result" bonus incentives look like for the middle tier
- What the custom-package configuration questions should be (the automation equivalent of "multi-page or homepage, bilingual, image enhancement")

Once defined, mirror the website package structure above using that axis instead of page count/complexity.

Until the user has supplied these definitions in the conversation, the automation gate (see "Start") applies in every mode, demo runs included.

### Writing features

- Every feature is one clear benefit sentence — what it does for the business — not just a label.
- Group features by logical section (for websites: design, content, technical, marketing).
- State the scope explicitly, e.g. "single-page site" or "multi-page site, up to [N] pages".
- Be specific and concrete: a longer, concrete list reads as more valuable than a short, vague one. In chat, list everything; the slides show the strongest 6–8 per package (Phase 5).
- Promise deliverables, not outcomes. Guaranteed results, refunds and performance promises are contractual commitments the agency has to honour, so include them only when the user supplies them. Incentives like the free first month are part of the offer.

### Prices, currency and tax

- Prices use the client's currency, formatted the way the deck language and country write money: symbol or code position, thousands separator, decimal mark. For example `$4,900` (en-US), `12 500 zł` (pl-PL), `CHF 4’900` (de-CH), `¥120,000` (ja-JP). Check the local convention rather than reusing one pattern everywhere.
- If the user wants you to suggest prices instead of supplying them, base the suggestion on scope, effort and Phase 2's research on local rates, and present it as a suggestion for them to adjust.
- Show tax the way the user chose in Phase 1. State a tax rate only if the user gave it; otherwise add a short note that tax treatment should be confirmed with a local accountant.

### Presenting packages

Show the packages in chat together with the research log, in the deck language, using this structure (translate the labels too):

```
## Package [N] — [Name] (~[price in the client's format] [one-time / + monthly])
**[Scope line, e.g. single-page site]**

- **[Feature]** — [what it does for the business]
- …

**Support:** first month free, then [monthly fee in the client's format] per month
```

Wait for the user's explicit approval before Phase 4.

## Phase 4 — Deck plan

Propose this structure and ask for approval or changes:

```
Slide 1  — Title (agency identity, client name, date)
Slide 2  — Why this matters now (sourced points from Phase 2)
Slide 3  — Business analysis (current situation vs. opportunity)
Slide 4  — Strategy for [client] specifically
Slide 5  — Package 1
Slide 6  — Package 2 (recommended)
Slide 7  — Package 3
Slide 8  — Comparison table, with the custom package option
Slide 9  — Expected return (sourced figures and/or a labelled example)
Slide 10 — Next steps and contact
Optional — a dedicated custom-package slide
```

If research turned up nothing reliable, propose slide 2 as qualitative points without figures, or merge it into slide 3, and say which. If the fallback identity is in use, remind the user here.

Wait for approval before building.

## Phase 5 — Build the deck

Produce one self-contained HTML file: all text inline, no frameworks, no external data files. Google Fonts is the only external resource, always with a system fallback stack so the deck still reads offline.

### Theme

Put the identity into CSS custom properties on `:root`, and use only these variables for colors and fonts:

```css
:root {
  --bg: …; --surface: …; --border: …;
  --text: …; --text-muted: …;
  --accent: …; --accent-soft: …; --recommended: …;
  --font-display: …; --font-body: …;
}
```

- Use the agency's hex values exactly, and derive the missing roles (surface, border, muted text) from them. A light brand gets a light deck.
- Check contrast for every text/background pair you use: at least 4.5:1 for body text, and 3:1 for large text (24px and up, or 18.5px and up in bold).
  - When a brand color falls short as text on its background, use it for rules, borders, badges and fills, and set the text in `--text`. Tell the user you did this.
  - The brand colors themselves stay exactly as supplied.
- The signature accent — a rule under titles, a colored edge on package cards, the recommended badge — uses `--accent`.

### Layout

- **Slides and navigation**
  - Full-screen slides sized with `height: 100vh; height: 100dvh;`.
  - Arrow keys, on-screen previous/next buttons and a slide counter, together in a bottom bar. Give every slide enough bottom padding that no content sits under the bar.
- **Type:** font sizes with `clamp()`, e.g. `font-size: clamp(1rem, 0.9rem + 0.6vw, 1.25rem)`, so text stays readable on phones and large on projectors. Body text is at least 16px on phones.
- **Desktop and laptop** (1280×720 and larger): every slide fits without scrolling.
  - Package slides show the strongest 6–8 features, in two columns where that fits.
  - The full lists live in the chat packages and the comparison table.
- **Phones** (below ~700px wide):
  - Columns stack into one.
  - A slide taller than the screen scrolls inside itself (`overflow-y: auto`), so content is never cut off.
  - Tables sit inside an `overflow-x: auto` wrapper.
- **Slide changes:** only the active `.slide` is displayed, and it enters with a short CSS `@keyframes` animation (a fade or small slide, around 300ms). `display: none` can't be transitioned, which is why the animation runs on the entering slide. Under `prefers-reduced-motion: reduce`, switch instantly.
- **Page setup:** `<html lang="…">` set to the deck language, plus a viewport meta tag.

### Slides

- **1 — Title.**
  - Agency logo or wordmark, client business name, date in the deck language's format, a one-line tagline and an accent divider.
  - Demo runs add the demo marker.
- **2 — Why this matters now.**
  - Up to four points from the research log, each sourced figure with its source line. Fewer is fine.
  - Qualitative points carry no figures.
- **3 — Business analysis.** Two columns — current situation vs. opportunity — from Phase 1.
- **4 — Strategy.** Three or four goals specific to this business and industry.
- **5–7 — Packages.**
  - Name and price prominent at the top, in the client's currency format; the features; support pricing at the bottom.
  - Package 2 carries the recommended badge, in the deck language.
- **8 — Comparison.**
  - Rows are features and columns are the three packages, with a check mark for included and a dash for not included. Package 2's column is highlighted.
  - The custom package is mentioned beneath the table, or on its own optional slide.
- **9 — Expected return.** Investment vs. return, built from sourced figures and client-supplied numbers where available. Any scenario is a labelled hypothetical with its assumptions shown.
- **10 — Next steps.** A short process (e.g. confirm → deposit → start), the agency's contact details from Phase 0 and one clear call to action.

### Code

- All slides sit inside `<div id="slides">`, with one `.slide` element per slide.
- JavaScript keeps a `currentSlide` index and handles keyboard and button navigation.

### Pre-delivery check

Before handing the deck over, go through the file and confirm each item:

- Every figure on the slides is sourced, client-supplied, from the packages, or a labelled hypothetical.
- All visible text is in the deck language, including package names, the badge, buttons and dates.
- Prices use the client's currency and local formatting throughout.
- Colors and fonts come from the `:root` variables built from the Phase 0 identity, or from the announced fallback.
- The contact details on slide 10 are the agency's from Phase 0, or marked placeholders.
- In demo runs, the demo marker is present and every contact detail is fake.

If a browser or screenshot tool is available, also view the deck at a laptop size (1280×720) and a phone size (390×844), and fix anything that overflows or overlaps.

### Output

- In claude.ai, where `/mnt/user-data/outputs/` exists, save the deck there and present it with `present_files`.
- Elsewhere, save it in the current working directory (or wherever the user asks) and give the path.
- Name the file `offer-deck-[client-slug].html`.

## Guardrails

- Facts in the deck come from Phase 2 research or stay out; scenarios are labelled hypotheticals.
- Language, currency, tax presentation and brand come from this conversation's agency and client.
- Packages are approved before the deck plan, and the deck plan before the build.
- Automation tiers come from the user's own definition; until then, the automation gate applies.
- Every feature bullet answers "what does this do for the business?"
- The deck is ready for a real prospect: professional, consistent, error-free.
