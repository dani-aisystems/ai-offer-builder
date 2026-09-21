# Project scope document: after the client says yes

Use this after a client has accepted an offer, usually one this skill built, sometimes one the user pastes. The user then wants the document both sides will work from during the build. The offer sold the project; this document manages it. It answers the same questions for the client and for the agency:

- what we are building
- what is included and what isn't
- what the client provides
- when the build period starts
- the milestones
- how revisions and scope changes work
- how payment works
- what counts as done
- where communication happens
- what happens after launch

It is an operational reference, not a contract, and it doesn't replace one. It never presents itself as one.

## What it is

- **Title.** In Bulgarian, **Обхват и план на проекта**. In another language, use the natural equivalent, for example "Project Scope and Plan". Use a different clear title only when the client's context strongly suggests better wording. The document never calls itself a договор, споразумение, contract or legal agreement, in the title or the body.
- **Tone.**
  - Write the way a professional small agency writes to a client with no technical knowledge: plain words and short paragraphs.
  - No legalese, no English business jargon in a non-English document, no filler and no exaggerated promises. In Bulgarian, write "начална среща", not "kickoff", and "обратна връзка", not "feedback".
  - Clients reread this document during revision discussions, and defensive wording turns a shared reference into an argument.
- **Length.** About 2–4 pages when rendered.
  - Use headings, short paragraphs, bullet lists and compact tables, with no walls of text.
  - Don't pad the document to make it look formal.
- **Not a sales document.**
  - Leave out sales arguments, competitor research, ROI claims and any case for why the client needs the website.
  - Research only appears where it became an agreed deliverable.

## 1. Gather the accepted offer

Don't make the user re-enter what is already known. Look in this order and stop once you have enough:

1. **This conversation.** Look for:
   - the approved packages
   - the Phase 1 answers, identity block and research log
   - anything agreed since, such as a discount, a removed feature or an extra page
   - whatever the user wrote with this request
2. **The offer record.** Look for `Offer record (internal).md` in the client's folder under `Offer decks/`. The folder is named `[Client name] - [Offer type] Offer - [date]`, sometimes with ` v2` or ` v3`.
   - If there are several versions, use the one that contains the chosen package.
   - If that is still ambiguous, ask which offer the client accepted.
3. **The deck.** Read the `.pptx` in the same folder: slide text, tables and speaker notes (with python-pptx or a pptx skill), and the theme's fonts and colors.
   - A deck carries only the strongest features of each package and usually no payment terms, so a scope built from the deck alone is incomplete.
   - Say so under the open points, and offer to add the full feature list if the user pastes it.
4. **The user.** Ask only for what is still missing *and* needed, all in one message.
   - The minimum is the client, the chosen package and the final price.
   - The agency identity is also needed. If it is nowhere in the conversation, record or deck, ask for it in the same message; the user may have the saved identity block to paste. If they skip it, use the fallback.
   - If the user names the package and a record or deck exists, ask nothing and write.

When sources disagree, the newer agreement wins:

- The user's latest instruction overrides the offer record.
- The offer record overrides the deck.
- Anything the offer agreed overrides this file's defaults.

For an accepted AI automation offer, take the scope from the offer exactly as you would for a website. Its tiers were settled when the offer was made.

## 2. Sort before drafting

Before writing, sort every fact you would put in the document into one of three groups:

- **Confirmed.** Stated in the accepted package or agreed with the user since. Safe to state as a commitment.
- **Derived.** Follows directly from the accepted package. Safe to state as a commitment. For example:
  - "everything in Package 1, plus…"
  - the support fee shown on the deck
  - publishing on the client's domain when the package delivers a live site
- **Unknown.** Anything you would have to invent. For example:
  - a page count the offer never gave
  - who owns the domain
  - a support period nobody promised
  - a feature that research suggested but no package included

  Handle each unknown in one of three ways: leave it out, mark it "за потвърждение" / "to be confirmed" in the document, or ask the user. Whichever you choose, list it under the open points in the chat summary so the user can settle it before sending.

Only Confirmed and Derived items become commitments. The client will hold the agency to this document, and the client knows exactly what was agreed.

## 3. Language, prices and tax

- Write the document in the accepted offer's deck language. For a Bulgarian business with Bulgarian-speaking contacts, that is Bulgarian. The chat stays in the user's language.
- Prices keep the offer's currency and local formatting.
- Keep the offer's tax wording exactly as it was shown, for example "без ДДС" or "before HST, plus applicable tax". Never add a tax rate or tax wording the offer didn't have.

## 4. Defaults

Use these only where the accepted offer says nothing; the offer's own terms always replace them. Mark every default you use as "(default)" in the chat summary. They are this skill's working terms, not something the client agreed to, and the agency may work differently.

| Topic | Default |
|---|---|
| Client materials and access | Delivered within 5 business days of the kickoff |
| Build period | 10–14 business days after all essential materials and access are received |
| Payment | 25% at project start; 75% after final approval, before the site is published |
| Communication | A kickoff call, then one shared Viber or WhatsApp group as the main project channel |
| Revisions | Reasonable revisions within the agreed scope, with no fixed number |

Ongoing services from the offer keep their own monthly fee and schedule: maintenance, hosting, ads management, monthly SEO and content. They go under recurring costs, never into the one-time price or the build period.

## 5. The document

Follow this structure. Adjust it only slightly, and only when the project calls for it, for example by merging two sections that would each be a single line. Headings are in the document language; the Bulgarian ones are given here.

The top of the document carries:

- the title
- the client's business name
- the agency's name
- the date
- one line naming the accepted offer (package name and offer date)

### 1. Обобщение на проекта

A few lines covering:

- the client and the project type
- the selected package
- the main goal
- the total price
- the expected duration

Take the goal from what this client actually needs, for example "a site that presents the menu, the location and table reservations". Never write a generic "modern, professional website".

### 2. Договорен обхват

Turn the package's deliverables into concrete scope and group them in whatever way fits: design, pages, content, technical, marketing. Include only what is Confirmed or Derived.

For pages:

- Group them logically; don't invent a rigid, high page count.
- Keep the offer's limit if it gave one ("up to 10 pages"), and list the core pages you know (Начало, За нас, Услуги / Меню, Галерия, Контакти…).
- If the structure may shift during the build, add: "Точната вътрешна структура може да бъде оптимизирана по време на изграждането, без промяна на договорения общ обхват."

### 3. Какво не е включено

Take exclusions from two places:

- **The offer's own exclusions**, listed first.
- **Exclusions at the edges of this scope.** Candidates:
  - features of higher packages the client didn't choose
  - professional photography or video
  - brand identity work
  - copywriting beyond what the package covers
  - ad spend
  - paid third-party licences
  - extra languages
  - e-commerce
  - new features requested after the scope is approved
  - unlimited revisions

Include only exclusions that fit this project, and never one that contradicts the offer. State them plainly, without sounding defensive.

### 4. Необходими материали и достъпи

A practical checklist, grouped. Include only what this project needs:

- **Brand:** logo files; colours and fonts, if they exist
- **Content:** services, menu or products; prices; descriptions; contact details; opening hours; any required policies
- **Visuals:** photos, gallery material, product or service images
- **Access:** the domain registrar; hosting, if any; Google Business Profile; analytics; booking or delivery platforms; any other agreed tool

Also cover:

- Ask for account invitations or delegated access rather than passwords.
- Separate the materials essential to start from those that can follow later.
- State that the client confirms that the prices, descriptions, opening hours, contact details, photos and product or service information they supply are accurate and approved for use.
- State the deadline: all essential materials and access within 5 business days of the kickoff, or the offer's own deadline. Add one neutral sentence on why: most project delays come from missing content or access.

### 5. Начало на срока за изработка

This rule protects the timeline, so set it apart visually in a shaded box. The build period starts only once all essential materials, information, approvals and access have been received. Neither the kickoff call nor the acceptance of the offer starts it. In Bulgarian:

> **Начало на срока за изработка:** Срокът за реална изработка започва след получаване на всички основни материали и достъпи, необходими за започване на проекта.

### 6. Етапи и срокове

State the build period: 10–14 business days after the essential materials are received, or the offer's own timeline. Then show six simple stages as a compact table or list. If the offer has its own workflow, adapt the stages to it.

1. **Старт на проекта.** The project is confirmed, the project channel is created and the materials checklist is shared. The deposit is due here if the payment terms put it here.
2. **Материалите са получени.** All essential materials and access have arrived, and the build period starts.
3. **Изработка.** Design, development, content and integrations.
4. **Преглед от клиента.** The full preview is shown and consolidated feedback is collected.
5. **Корекции.** Reasonable revisions within the scope.
6. **Одобрение и публикуване.** Final review, the remaining payment, and publishing on the live domain.

Then add the note on delays, matter-of-factly:

> При забавяне на необходими материали, достъпи или обратна връзка от страна на клиента, крайната дата може да бъде изместена спрямо периода на забавянето.

Don't promise an exact delivery date while the client still owes materials. Without a kickoff date, give durations, not calendar dates.

### 7. Комуникация

- The main channel is a kickoff call followed by one shared Viber or WhatsApp group, or whatever the offer agreed. Name the app if it is known.
- Requests, feedback, approvals, scope changes and the launch confirmation go in that channel.
- Anything settled by phone or elsewhere is summed up there afterwards.
- Explain the reason in one line: one clear record, and no conflicting instructions. Keep it free of legal tone.

### 8. Обратна връзка и корекции

- Reasonable revisions within the agreed scope are included. They refine and finish the agreed site; they don't redefine it.
- Ask for each review round's feedback collected into one message, not many fragments.
- Normal revisions include text corrections, swapped images, spacing and layout refinements, small visual changes and implementation fixes.
- Larger new requests may be a scope change (section 9).
- State a number of revision rounds only if the offer had one.

### 9. Промени извън договорения обхват

Examples of requests outside the scope:

- entirely new pages
- major new functionality
- another language version
- e-commerce
- new integrations
- a substantial redesign after approval
- systems that were never discussed

Such requests are discussed and confirmed first. They may add cost, extend the timeline and require this document to be updated. Give no price for them unless one was already agreed.

### 10. Цена и плащане

State the exact accepted price with the offer's tax wording. Take the payment terms from the offer; if it has none, use the default:

- **25% авансово плащане при стартиране на проекта.**
- **75% след финално одобрение и преди публикуване на сайта.**

Show the amount of each part in the offer's currency format, calculated exactly, and check that the parts add up to the total.

Then add a compact table that keeps one-time and recurring costs apart:

- the build price on one side
- on the other, each monthly service in the offer (maintenance, hosting, ads management, subscriptions), with its fee in the offer's own wording (for example "first month free, then CA$89/month")
- ad spend and third-party licences as billed separately, where the offer says so

Never fold a recurring cost into the one-time price.

### 11. Финализиране и публикуване

The site is ready for launch when:

- the agreed scope is implemented
- the client has reviewed the final version
- reasonable revisions are complete
- the client has given final approval
- the payment due before launch has been made

It is then published on the agreed domain. If the package has its own launch process, follow that instead.

### 12. След публикуването

Take this section from the offer only, in three parts:

- **Included support.** What the offer includes, such as bug fixes, technical corrections or a stabilisation period. Give a duration only if the offer gave one.
- **Ongoing maintenance.** Only if it was bought: what the monthly fee covers, as the offer described it.
- **New work.** New pages, features, campaigns, content, integrations and redesigns are separate unless the offer includes them.

Never invent a support period. If the offer set none, state only what is known.

### 13. Потвърждение на проекта

Keep it light, along these lines:

> Този документ служи като обща референция за обхвата, сроковете, отговорностите и начина на работа по проекта.
>
> Всички последващи съществени промени по обхвата се обсъждат и потвърждават писмено в основния комуникационен канал на проекта.
>
> **Потвърждение от клиента:** Кратък отговор „Потвърждавам“ в общата Viber/WhatsApp група е достатъчен за потвърждение, че описаният обхват и начин на работа са разбрани.

Add no signature lines unless the user asks for them.

## 6. Build the file

The deliverable is a Word document (`.docx`) plus a PDF copy: the agency keeps editing the `.docx`, and the client receives the PDF.

- **Script.** Generate the `.docx` with a script, using the `docx` package in Node or python-docx in Python, whichever the environment has; install one if neither is available. If a docx skill is installed, follow it for the mechanics. The script is a working file, so keep it outside `Offer decks/`.
- **Identity.** Take fonts and colors from the identity block, in the conversation or the offer record. Failing that, take them from the deck's theme.
  - Use hex values and font names exactly as given.
  - A document is read on paper and on a phone. Keep pages white or the brand's light background. A dark brand puts its accent on headings, rules, table headers and the shaded box.
  - The deck's contrast rules apply: 4.5:1 for body text, including text on the shaded box and table headers.
  - With no identity, use the fallback identity from SKILL.md, with the agency name and contact details as bracketed placeholders, and say so in chat.
- **Layout.**
  - A4, or US Letter for the US and Canada.
  - Use real heading styles, real bullet lists and native tables, so the agency can edit everything.
  - Put the start-condition rule in a shaded box.
  - Add a header with the agency name, and a footer with the agency's contact details from the identity (email, phone, website, whichever it has) and page numbers.
  - Set the document language (`w:lang`) to the document language so spell-check works, and set the title and author properties.
  - A `.docx` doesn't carry its fonts, but the PDF does. Tell the user which fonts the `.docx` needs.
- **Saving.**
  - Save both files in the accepted offer's folder inside `Offer decks/`, next to the deck and the record. Name them `[Client name] - [Document title]`, for example `Автосервиз Пример - Обхват и план на проекта.docx` and the same name with `.pdf`.
  - If there is no such folder, because the offer came from elsewhere, create `Offer decks/[Client name] - Project Scope - [YYYY-MM-DD]/`.
  - Never overwrite anything. If a file with that name exists, add ` v2` or ` v3`.
  - In claude.ai, where `/mnt/user-data/outputs/` exists, save there and present both files with `present_files`.
- **PDF and visual check.**
  - Convert with `soffice --headless --convert-to pdf`, render the pages with `pdftoppm -png -r 80`, and look at every page.
  - Check that it runs 2–4 pages, nothing is clipped or overlapping, tables stay inside the margins and the shaded box is readable. Fix and render again.
  - Without a renderer, deliver the `.docx` alone and say the layout wasn't viewed.

## 7. What goes in the chat

The document is the deliverable, so keep the chat short. Write it in the user's language; for a Bulgarian-speaking user, use these labels:

```
**Използвани данни**
- Клиент: …
- Избран пакет: …
- Цена: …
- Срок: …
- Основни особености: …

**Стандартни условия (по подразбиране):** each default used
**За уточняване:** the open points, or "няма"
```

Then give the file paths (or present the files) and the fonts the `.docx` needs. Add no long explanation before or after, and don't repeat the document's text.

## 8. Final check

Before handing the files over, confirm each item:

- **Offer and price.** The package is the one the client chose. The price is exact and the tax wording matches the offer.
- **Scope.** Every scope item is in the accepted package or was agreed since; none comes from research alone. The exclusions are clear, and none contradicts the offer.
- **Materials.** The materials deadline is stated: 5 business days, or the offer's own.
- **Build start.** The rule "all essential materials and access received = the build period starts" is explicit and set apart, and a kickoff call doesn't start the period.
- **Build period.** It is the offer's own, or 10–14 business days only if the offer set none.
- **Revisions and changes.**
  - Reasonable revisions within scope are included, with a count only if the offer had one.
  - Out-of-scope requests are tied to possible extra cost and time, with no invented price.
- **Payment.** It follows the offer's terms, or 25% / 75% only if the offer had none, and the parts add up. Recurring costs are separate from the one-time price.
- **Working arrangements.** The communication channel, the client's responsibilities and what counts as done are clear.
- **After launch.** Post-launch support states only what the offer established.
- **Tone.** The confirmation is a short reply in the group, not a signature. The document never calls itself a contract or an agreement in any language.
- **Chat summary.** Every default used is flagged, and every unknown is either marked in the document or listed as an open point.
- **Files.** The `.docx` opens, the PDF runs 2–4 pages, and both sit in the client's folder with nothing overwritten.
