# Coding guide: climate disclosure paragraphs

> **NOT USED (2026-11-17).** Human validation (design g) was dropped by owner decision (amendment A20). This guide was never used for coding and is kept as a record only. Its frozen SHA-256 before this notice was `4935305284b4a9e916ddbc3d6ea7ff394fdff7c0f85a185b61d0442edd93a2f7`.

**Version:** frozen 2026-11-17, before any coding. The SHA-256 of this file is recorded in `docs/amendments.md`. Any change after that needs an amendment.

**For:** the external coder who codes the validation sample (design section g; amendment A18).

**Source of the questions:** `docs/design.md`, section g, items (i) to (v). The definitions below put those items into plain English. Where the design gives the definition (item ii), its wording is kept.

---

## 1. What you will do

You will read about 200 short passages ("paragraphs") taken from the annual and sustainability reports of companies listed on the Nigerian Exchange. Each one comes from the narrative part of a report, not the financial statements. For each paragraph you answer five questions.

- **Code each paragraph on its own.** Do not guess from the company, the year or what you know about the firm. Use only the words in the paragraph.
- **You will code the same paragraphs twice.** The second pass uses a new random order, and comes **at least 7 days after** you finish the first pass. Do not look at your first-pass answers during the second pass. Do not keep notes about individual paragraphs between passes.
- **You will not see any computer scores.** No model output or keyword tag is shown to you, and you should not try to work them out.
- **Paragraphs may start or end mid-sentence.** They were cut from PDF layouts. Code what is there.
- **Time:** about 1 minute per paragraph is normal. If a paragraph is hard, give your best answer and write a short note.

## 2. How to record your answers

Use the coding sheet you are given, with one row per paragraph id. Use exactly these answers:

| Column | Allowed answers | When to answer |
|---|---|---|
| `climate` | yes / no | always |
| `specific` | yes / no / na | `yes` or `no` only if `climate` = yes; otherwise `na` |
| `physical_risk` | yes / no / na | `yes` or `no` only if `climate` = yes; otherwise `na` |
| `tcfd` | governance / strategy / risk management / metrics and targets / na | one category only if `climate` = yes; otherwise `na` |
| `names_site` | yes / no | always, whatever the answer to `climate` |
| `note` | free text | optional: anything unclear |

**Order of work:** answer question 1 first. If the answer is "no", questions 2–4 are `na` and you go straight to question 5.

---

## 3. The questions

### Question 1 (item i). Is the paragraph climate-related? (`climate`: yes / no)

**Definition.** A paragraph is climate-related if it discusses climate change, its causes, its effects, or what the company or others do about it.

**Include (answer yes)** if the paragraph discusses any of these:
- Greenhouse-gas or carbon emissions, carbon intensity, net zero, decarbonisation.
- Energy use or fuel switching **when presented as cutting emissions or carbon**: renewable energy, alternative fuels or energy efficiency described as climate or emissions measures.
- Climate risks and opportunities, climate scenarios, climate targets, or climate governance (board or management oversight of climate matters).
- Physical climate hazards and their effects: floods, storms, heatwaves, drought, water stress or water scarcity, sea-level rise, coastal erosion, desertification, wildfire, changing rainfall or temperatures.
- Adaptation or resilience to climate change.
- Climate policy, climate disclosure standards (for example IFRS S2, TCFD, CDP climate), the Paris Agreement, NDCs, carbon pricing.

**Exclude (answer no):**
- **General environmental topics** with no link to climate in the paragraph: waste, recycling, plastics, air pollution or dust, biodiversity, tree planting for beautification. If the paragraph itself ties the topic to climate ("planting trees to sequester carbon"), answer yes.
- **General "sustainability" or "ESG"** wording with no climate content ("we are committed to sustainability and ESG best practice").
- **Energy costs or supply** discussed only as a business cost or reliability matter ("diesel prices rose", "the grid was unreliable"), with no emissions or climate angle.
- **The word "climate" in a non-climate sense:** "business climate", "economic climate", "investment climate".
- **"Heat" in an industrial sense** only: furnace heat, heat treatment. Waste heat recovery counts only if it is presented as an emissions or decarbonisation measure, as in example 3-B.
- **Water management** about efficiency or treatment only, with no reference to drought, scarcity, water stress or climate.

**Worked examples** (from the Dangote Cement 2025 sustainability extract, the Phase 0 test document; not part of your sample):

> **1-A.** "[passage from a company report removed in the public copy]"
>
> **Answer: yes.** It is about emissions targets and a climate transition plan.

> **1-B.** "[passage from a company report removed in the public copy]"
>
> **Answer: no.** It is about a customer finance scheme. Trucks are mentioned, but not emissions or climate.

### Question 2 (item ii). Is the climate content specific? (`specific`: yes / no; `na` if not climate-related)

**Definition (design g).** Specific means the paragraph contains **a quantity, a date, a named location, a named asset or a named action**.

**Include (answer yes)** if at least one of these is part of the climate-related content:
- **A quantity:** a number with a unit or a percentage (tonnes of CO2, %, megawatts, hectares, money spent).
- **A date:** a year or deadline ("by 2030", "in 2025", "relative to 2021").
- **A named location:** a town, site, state or country where the climate action or risk applies ("at the Ibese plant", "in Zambia").
- **A named asset:** a particular plant, facility, project or piece of equipment identified by name.
- **A named action:** a programme, initiative, policy or plan with its own name ("Tree-to-Forest Initiative", "Climate Adaptation and Resilience Plan", "GCCA Net Zero Roadmap").

**Exclude (answer no):**
- Only general statements of intent or commitment ("we are committed to reducing our carbon footprint"), however long.
- Numbers that are not part of the climate content: page numbers, section numbers, GRI index numbers, or a figure about something unrelated in the same paragraph.
- The company's own name, or "Nigeria" / "Africa" used only as the company's general setting, does not by itself make a paragraph specific.

**Worked examples:**

> **2-A.** The paragraph in 1-A. **Answer: yes.** It has a quantity (20%, 95%), dates (2030, 2021) and a named action (GCCA Net Zero Roadmap).

> **2-B.** "[passage from a company report removed in the public copy]"
>
> **Answer: climate yes, specific no.** It is about climate governance, but has no number, date, place, named asset or named action.

### Question 3 (item iii). Is it about physical climate risk? (`physical_risk`: yes / no; `na` if not climate-related)

**Definition.** Physical climate risk is harm, or possible harm, from the weather and climate itself, as opposed to harm from climate policy or markets. It comes in two forms:
- **Acute:** events such as floods, storms, heatwaves and wildfires.
- **Chronic:** long-term shifts such as rising temperatures, drought, water stress or scarcity, sea-level rise, coastal erosion, desertification and changing rainfall.

**Include (answer yes)** if the paragraph does either of these:
- **Names a physical climate hazard** as a risk, impact or exposure for the company, its sites, supply chain, workers or communities. A past event counts ("flooding disrupted deliveries").
- **Refers explicitly to physical climate risk,** for example "physical risks", "acute and chronic physical impacts", or adaptation or resilience to a named hazard.

**Exclude (answer no):**
- **Transition risk only:** carbon taxes, regulation, market shifts, technology change, reputation.
- **Mitigation only:** cutting emissions, renewable energy or alternative fuels, with no hazard or physical risk mentioned.
- **"Adaptation" or "resilience" in general terms,** with no hazard and no mention of physical risk ("climate mitigation and adaptation are part of our strategy").
- **Hazard words in a non-climate sense:** "heat" in a production process, "a flood of imports", "storm" as a figure of speech, soil "erosion" of margins, "coastal" used only as part of a name or address.
- **Water efficiency only,** with no drought, scarcity or water-stress angle.

**Worked examples:**

> **3-A.** "[passage from a company report removed in the public copy]"
>
> **Answer: climate yes, physical_risk yes.** It names heatwaves, droughts, flooding and water stress as exposures, and discusses physical risk assessment.

> **3-B.** "[passage from a company report removed in the public copy]"
>
> **Answer: climate yes, physical_risk no.** It is about cutting emissions (decarbonisation). "Heat" here is process heat, not a heatwave.

### Question 4 (item iv). Which TCFD category fits best? (`tcfd`: one category; `na` if not climate-related)

The four categories come from the Task Force on Climate-related Financial Disclosures (TCFD). **Choose the one that is the main point of the paragraph.** If two fit, choose the one that takes up more of the paragraph.

| Category | The paragraph is mainly about … |
|---|---|
| **governance** | who oversees climate matters: the board, board committees or management; their roles, meetings, skills, reporting lines, or pay linked to climate |
| **strategy** | climate risks and opportunities and what they mean for the business, strategy or finances: transition plans, scenario analysis, investment in low-carbon products or energy, decarbonisation strategy, adaptation plans |
| **risk management** | the processes used to identify, assess and manage climate risks: risk registers, enterprise risk management, risk classification, how risks are monitored |
| **metrics and targets** | the measures used and the targets set: emissions figures, intensity figures, energy or water data, progress against a target |

**Worked examples:**

> **4-A (governance).** "[passage from a company report removed in the public copy]"
>
> **Answer: governance.** It is about board oversight and meetings.

> **4-B (risk management).** "[passage from a company report removed in the public copy]"
>
> **Answer: risk management.** It is about how climate risks are identified and classified. (Also: specific yes, because of "10% of EBITDA"; physical_risk yes, because of the explicit reference to physical risks.)

> **4-C (metrics and targets).** "[passage from a company report removed in the public copy]"
>
> **Answer: metrics and targets.** It reports emissions figures against targets.

> **4-D (strategy).** "[passage from a company report removed in the public copy]"
>
> **Answer: strategy.** The board is mentioned, but most of the paragraph is about how climate shapes strategy and investment.

### Question 5 (item v). Does the paragraph name a company site? (`names_site`: yes / no; answer for every paragraph)

**Definition.** A company site is a place where the reporting company has a physical facility: a plant, factory, brewery, mill, refinery, depot, terminal, warehouse, estate or plantation, farm, mine or quarry, power station, oil field or licence area, or office. The paragraph **names a site** if it identifies such a facility by its town, district, estate or own name, and makes clear that a facility is meant.

**Include (answer yes):**
- **A named facility** ("the Obajana plant", "our Ikeja factory", "the Agbara manufacturing site", "Okomu estate", "OML 40", "MTN Plaza").
- **A named town or estate together with the company's facility there,** even in a list ("our breweries in Aba, Ibadan and Lagos").
- **Any context counts:** an address in a corporate-information paragraph, a production update, a community project at a named plant.

**Exclude (answer no):**
- **Only generic references:** "our plants", "all production sites", "across our operations".
- **Only a country, region or continent:** "Nigeria", "West Africa", "across Africa".
- **A named place that is not given as the company's facility:** a city named as a market, an event venue, a community or school the company supported, a government body's location, or another company's facility.

You do not need a list of the company's sites. Judge from the paragraph whether it names a place as the company's own facility.

**Worked examples:**

> **5-A.** "[passage from a company report removed in the public copy]"
>
> **Answer: names_site yes.** "Okpella … plant" names a company plant. (Climate yes; specific yes, for the named action and location; physical_risk no; tcfd strategy.)

> **5-B.** "[passage from a company report removed in the public copy]"
>
> **Answer: names_site no.** "All production sites" is generic. (Also: climate no, so questions 2–4 are na. The paragraph presents energy intensity as an efficiency measure and never mentions emissions, carbon or climate. Under question 1, energy efficiency with no emissions or climate angle is **no**.)

---

## 4. Practice paragraphs (with answers)

Code these five paragraphs before you start, then check your answers below. They come from the same test document and are **not** in your sample.

**P1.**
> "[text from a company report removed in the public copy]"

**P2.**
> "[text from a company report removed in the public copy]"

**P3.**
> "[text from a company report removed in the public copy]"

**P4.**
> "[text from a company report removed in the public copy]"

**P5.**
> "[text from a company report removed in the public copy]"

### Answers

| | climate | specific | physical_risk | tcfd | names_site | Why |
|---|---|---|---|---|---|---|
| P1 | yes | yes | yes | metrics and targets | no | Water stress is a climate hazard, and the paragraph targets operations in water-stressed regions. It has quantities and dates (20%, 2030, 5,231 megalitres). It is mainly a target and its progress. "Plants" and "operational locations" are generic. |
| P2 | yes | yes | no | strategy | no | It ties tree planting to carbon sequestration and decarbonisation. A named action (Tree-to-Forest Initiative) and quantities (23 hectares, 2025) make it specific. "Adaptation" appears only in general terms, with no hazard named. "Mined-out limestone areas" names no place. |
| P3 | no | na | na | na | no | "Environmental concerns" and "environmental risk management" are not about climate. No site is named. |
| P4 | yes | no | no | strategy | no | Clean energy and alternative fuels are presented as decarbonisation measures. There is no number, date, place, named asset or named action. CNG is a fuel type, not a named action. |
| P5 | no | na | na | na | yes | It is about community and social investment; "Sustainability Week" alone is not climate content. "Ibese Plant", "Obajana and Gboko plants" name company plants. |

---

## 5. If you are unsure

- Re-read the definition and the include/exclude lists for that question.
- If it is still unclear, choose the answer that fits the words of the paragraph best, and write a short note.
- Do not discuss individual paragraphs with anyone involved in the project until both passes are finished.
