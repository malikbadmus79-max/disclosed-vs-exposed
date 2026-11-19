# Phase 6: Interpretation and policy

**Date:** 2026-11-18. **Status: draft for Phase 7 verification.**
- **Inputs:** the Phase 5 results as reported in `docs/phase5_analysis.md` (descriptive only, A20/A21), IFRS S2 (A24), the regulatory sources already read in Phase 0 (`docs/data_sources.md`), and the Seplat documents named below.
- **No new outcome** is computed and no confirmatory or causal claim is made.

**Conventions:**
- **[V7]** marks a claim that Phase 7 must verify against its source.
- **Not verified** marks a claim that rests on a source not read for this project.
- **IFRS S2** is cited by paragraph number only, and its requirements are paraphrased (personal non-commercial licence; edition ISSB-2026-A, effective for annual periods beginning on or after 1 January 2024, para C1).

---

## 1. What Phase 5 found, mapped to IFRS S2

The four Phase 5 findings, as reported (all descriptive, for the documents held, 2020–2025):

| # | Finding (Phase 5) | Where |
|---|---|---|
| F1 | **Hazard silence:** 68 of 97 main firm-years with narrative text (Phase 7 correction from "68 of 98", A23) have no paragraph using any hazard term. Of 15 firms with heat-exposed sites, 2 ever use heat terms; for river flood, 6 of 21 (Phase 7b correction from "7 of 21", which still counted NNFM FY2020, A23) | phase5 §2 |
| F2 | **The site gap:** of 51 exposed main sites, 50 are named somewhere in their firm's reports, but **7** are named in a hazard-tagged paragraph (post-hoc descriptive; H4 as designed is near-mechanical). **Phase 7 re-read: none of the 7 is a genuine physical-risk statement about the site; 0 of 51 on reading.** | phase5 §2–3 |
| F3 | **Firm characteristics over exposure (H2):** firm characteristics (size, ownership, sector) add more explained variation in hazard language than measured site exposure does: 0.17 against 0.04 in R²; difference −0.13 (−0.37 to −0.06). Caveat: the institutional block has more parameters | phase5 §5 |
| F4 | **No clear trend (H3):** within firms, no clear 2020–2025 trend in hazard language or in site-named hazard language; all intervals include zero | phase5 §6 |

What IFRS S2 asks for, and what a compliant disclosure would contain:

| Finding | IFRS S2 paragraphs | What a compliant disclosure would contain | Policy code |
|---|---|---|---|
| F1 | **3(a)(i)** (scope covers physical risks); **10(a)–(d)** (describe the risks that could reasonably be expected to affect prospects, classify each as physical or transition, and give its time horizon); **Appendix A** (acute and chronic physical risks, e.g. floods, heatwaves, drought) | A list of the physical hazards the entity judges material (e.g. flood, extreme heat, water stress), each labelled physical, with short-, medium- or long-term horizons and the entity's definitions of those horizons. If a hazard is judged immaterial, the materiality judgement behind that (IFRS S1, **not read**) | P1 |
| F2 | **13(b)** (where risks are concentrated: geographical areas, facilities, types of assets); **29(c)** (amount and percentage of assets or business activities vulnerable to physical risk); **B65(b)** (link those metrics to where risks are concentrated) | A table of the entity's facilities or asset types with the physical hazards each is exposed to, and the amount or percentage of assets vulnerable to physical risk | P5, P3 |
| F3 | **11** (use all reasonable and supportable information available without undue cost or effort, including past events, current conditions and forecasts); **22** (climate resilience assessed with scenario analysis commensurate with the entity's circumstances; B1–B18); **25(a)(i)–(iii)** (risk processes: data sources and scope of operations, scenario use, how likelihood and magnitude are assessed) | The method behind the risk list: which hazard data and which sites were assessed, which scenarios were used, and how risks were ranked. Under full application one would expect physical-risk content to follow the entity's own assessed exposure. Phase 5 found that in 2020–2025, before mandatory reporting, it followed firm characteristics more than measured site exposure (descriptive; measurement limits in §5) | P1, P2, P4 |
| F4 | **C1** (S2 effective from periods beginning 1 January 2024); Nigeria: mandatory from periods beginning 1 January 2028 (§2) | Nothing in 2020–2025 required this content in Nigeria. The absence of a trend is consistent with a voluntary period. It sets a baseline for checking change after 2028 | P6 |

**What Phase 5 cannot tell us about compliance:**
- **Not an assessment of IFRS S2 compliance:** most firm-years predate both the standard's effective date (2024) and Nigeria's mandatory date (2028), and the dictionary measures hazard words, not S2 compliance.
- **Firm-year policy coding:** P1–P7 have since been coded for each firm-year (A25, §2b). The coding is analyst-coded and descriptive, with no human validation. **[V7]**

---

## 2. Nigeria context (P6)

From sources read in Phase 0 (`docs/phase0_audit.md`; links in `docs/data_sources.md`):

| Instrument | Content (as read) | Status |
|---|---|---|
| **SEC circular** "Implementation of the IFRS Sustainability Disclosure Standards in Nigeria", published 23 September 2026 | Implementation Plans due by 15 October 2026. Mandatory IFRS S1/S2 for accounting periods beginning on or after 1 January 2028 (SMEs from 1 January 2030). Voluntary adoption from 1 January 2024 to periods ending by 31 December 2027 | Read **[V7: re-check the live page before publication]** |
| **FRC Roadmap (Amended 2026)** and SRG 1 2026 | Phase 1: early adopters, periods ending on or before 31 December 2023. Phase 2: voluntary adopters, 2024–2027. Phase 3: mandatory for public-interest entities from periods beginning 1 January 2028; SMEs from 1 January 2030. Readiness test compulsory before the first sustainability report. Assurance from the third reporting year (PDF pp19, 30). The readiness test collects documents including a climate-risk materiality assessment and a description of scenario-analysis models (PDF pp20–21) | Read **[V7]** |
| **NGX Sustainability Disclosure Guidelines** (approved by the SEC 9 November 2018) | Risk management "begins with detecting key risks of operational disruptions from climate change …" (p8) | Read **[V7]** |

**Not verified:**
- **Timing mismatch:** secondary coverage reports a possible mismatch between the SEC circular's timing and the FRC phase documents. The SEC text read does not refer to the FRC phases.
- **The figure "41":** the FRC press release and the Roadmap may mean different things by it.

**Where the study period sits:**
- **2020–2023** fall in or before Phase 1 (early adopters).
- **2024–2025** fall in Phase 2 (voluntary).
- **None** of the study's firm-years falls under mandatory reporting.

**P6 for individual firm-years** is coded in §2b.

---

## 2b. Firm-year policy coding (P1–P7) and "2028 readiness" (A25)

**Status:** the codes are **descriptive and analyst-coded** (the coder is the analyst, Claude, applying the A25 rules). **No human validation is claimed** and no reliability statistic exists. They describe the documents held. They are not outcomes, they enter no hypothesis, and no Phase 5 outcome changed.

**Method (A25, logged before coding):**
- **Search:** keyword patterns per code over every text row of each firm-year's documents (403 candidate sentences).
- **Reading:** every candidate was read by the analyst.
- **Coding:** a code is 1 only with page evidence. Doubtful cases are 0, with a note.

**Files:**
- `data/processed/policy_codes_firm_year.csv` (99 main-census firm-years; NNFM FY2020 excluded under A23);
- `data/processed/policy_codes_evidence.csv` (38 evidence rows: document, page, paragraph id, passage);
- `data/interim/policy_candidates.csv` and `policy_decisions.csv` (all candidates and the analyst's decisions, including the zeros with notes);
- code: `src/phase6_policy_codes.py`.

**2028 readiness:** each main-census firm's **latest** firm-year held (56 firms: 46 in FY2025, 7 in FY2024, 3 in FY2023), against what IFRS S2 will require from periods beginning 1 January 2028.

| Code | Element (IFRS S2 anchor) | Firms, latest year (of 56) | Firm-years (of 99) | Which firms (latest year) |
|---|---|---|---|---|
| P1 | Resilience of strategy to physical risks (22) | 4 | 4 | Airtel Africa, Dangote Cement, MTN Nigeria, Seplat |
| P2 | Climate scenario analysis used (22, B1–B18) | 4 | 5 | Airtel Africa, Dangote Cement, MTN Nigeria, Seplat (also Seplat FY2020) |
| P3 | Physical-risk metric reported (29(c)) | 2 | 2 | MTN Nigeria, Seplat |
| P4 | Physical/climate risk in the risk-management process (25) | 5 | 7 | Airtel Africa, Dangote Cement, Guinness, MTN Nigeria, Seplat (also Dangote FY2020, Seplat FY2020) |
| P5 | Locations or assets at physical risk identified (13(b), 29(c), B65(b)) | 4 | 4 | Airtel Africa, MTN Nigeria, Seplat, Unilever |
| P6 | Adoption status: voluntary (reports in accordance with IFRS S1/S2) | 2 | 2 | MTN Nigeria FY2025, Seplat FY2025 |
| P6 | Readiness, plans or partial alignment only | 4 | 7 | BUA Cement, Dangote Cement, Guinness, Unilever (latest year); Aradel FY2024 is not its latest year |
| P7 | Refers to the NGX/NSE Sustainability Disclosure Guidelines | 2 | 7 | MTN Nigeria, Unilever (Dangote FY2020–2024 also) |

**Summary for 2028 readiness:**
- **Full set:** in their latest year held, **2 of 56** main-census firms (MTN Nigeria and Seplat) show all five physical-risk elements, P1 to P5.
- **At least one element:** 6 firms.
- **None:** 50 firms show none of the five.
- **FS-only filings:** 26 of the 56 latest years are financial-statement-only filings, so a zero there also reflects the document type held (f1).
- **Voluntary IFRS S1/S2 reporting:** only MTN Nigeria and Seplat state that their FY2025 disclosures are prepared in accordance with IFRS S1/S2. Seplat also says it adopted early in 2023; that report is not in the corpus.
- **Guinness FY2025:** presents a first partial alignment note, explicitly not a comprehensive application, so it is coded readiness only.

**Notes on borderline codes** (the full notes are in `policy_decisions.csv`):
- **MTN P3** is realised damage (₦91.8m across nine sites in eight states), counted as a physical-risk metric.
- **Dangote FY2025 P5 = 0:** it says physical risks are evaluated "at the plant level" but names no plant or result.
- **Seplat FY2020 P1 = 0:** physical risks are recognised, but strategy resilience is discussed for the energy transition only.
- **Okomu FY2023/24 P5 = 0:** its "diversified in two plantations" statement does not identify assets at risk.
- **Guinness FY2025 P2 = 0:** scenario outputs were omitted under a transition relief.

**How this links to Phase 5:**
- **The same pattern, by a different method:** the policy codes and the dictionary outcomes are separate measures. Both show that physical-risk content at the asset or site level is concentrated in very few firms.
- **Different denominators:** the codes count firms with *any* qualifying passage. The dictionary outcomes count the *share* of paragraphs.

---

## 3. Seplat case (descriptive)

**Why Seplat:** it is the census firm with the most developed sustainability reporting held. Two of its documents (2020 annual report, 2025 integrated report) are in the corpus, and the owner supplied two more for this phase (2023 sustainability report, 2025 social performance report). The latter two are **not** in the corpus and change no outcome.

| Document | What it says about physical risk (as read) | Compared with the census |
|---|---|---|
| 2020 annual report (corpus) | 1 hazard-tagged paragraph out of 548 scored | Typical of the census (median firm-year: none) |
| 2023 sustainability report (owner batch 6) | Hazard terms appear mainly in water-stress statements: Seplat says it operates in a region of low water stress and its assets are not identified as high water risk. Flooding appears once, as community road drainage. It points to the 2023 annual report (not held) for its IFRS S2 content, listing climate resilience and risk management pages **[V7]** | Its water-stress statement agrees with Phase 3: none of Seplat's three main sites is water-stress-exposed under Aqueduct |
| **2025 integrated report** (corpus) | 12 hazard-tagged paragraphs out of 653 (1.8%; census mean 0.3%). It describes Niger Delta flood and sea-level risks, and reports an **asset-level physical-risk assessment**: IPCC climate data, 13 hazards, three scenarios, and named licence areas with their exposures (e.g. OML 40 significant for precipitation and pluvial flooding; OMLs 4, 38, 41, 53 moderate for temperature and heavy rainfall). It also states that impacts on operations have so far been limited (pp139–154) **[V7]** | **Closest to IFRS S2 13(b) and 22 in the census.** It names assets by licence area. It does not name the three main point sites (Sapele gas plant, Amukpe flow station, Qua Iboe Terminal) as physically at risk. The only frozen-dictionary "site in hazard text" match for those sites is a "storm water design study" at Amukpe, a likely false positive that the refined dictionary drops |
| 2025 social performance report (owner batch 6) | Flooding appears as a **community** issue: coastal and rainfall flooding in Ibeno (Akwa Ibom), with canal and gutter clearing funded through host-community trusts. It is not framed as a risk to Seplat's assets **[V7]** | The Qua Iboe Terminal is in Akwa Ibom and is river-flood and heat exposed in Phase 3 (not coastal at RP100). That the terminal lies in Ibeno is **not verified** from a project source |

**Plain reading:**
- Seplat moved from near-silence (2020) to a licence-level physical-risk assessment (2025). That is the kind of content IFRS S2 13(b) asks for.
- The assessment is at the level of licence areas, while the point facilities that Phase 3 scores as exposed are not discussed as at risk.
- Flooding near operations appears in community reporting rather than in risk reporting.
- **One firm only:** this case does not generalise to the census, and the changes are not attributed to any cause.

---

## 4. Interpretation: decoupling and institutional theory (careful reading)

**What the pattern is consistent with:**
- **Policy–practice decoupling** (Meyer & Rowan 1977; Bromley & Powell 2012): formal climate language and framework references exist, while site-level physical-risk content is rare (F1, F2).
- **Means–ends decoupling** (Bromley & Powell 2012): disclosure activity that is not linked to the places where hazards occur (F2).
- **Selective disclosure** (Marquis, Toffel & Zhou 2016): F3. Firm characteristics account for more variation in hazard language than exposure does, as institutional accounts of disclosure would lead one to expect.

**What it is not:**
- **Not evidence of intent:** the design states that a mismatch is a descriptive measure of possible decoupling, not evidence of intent or misconduct (design a). Nothing here says any firm hid anything.

**Other explanations the data cannot rule out:**
1. **No mandate:** every firm-year predates mandatory reporting (2028), so silence may reflect the absence of a requirement, not a choice to decouple.
2. **Materiality judgements:** firms may have assessed flood or heat and judged them immaterial. IFRS S2 allows this, but the judgement itself would then be the thing to disclose.
3. **Data costs:** no shared national hazard dataset is cited in the reports read. Site-level assessment may be costly for small firms (see S2 para 11's "without undue cost or effort").
4. **Measurement limits of this study:**
   - dictionary precision 0.65 (storm, erosion and coastal are weak);
   - recall not measured, so hazard talk worded differently ("flooded", "water-stressed") is missed;
   - the site list comes from the same reports;
   - 12–27 firms per analysis, most with one or two years.
5. **Exposure measures:** Phase 3 hazard scores are model-based (JRC, Aqueduct, ERA5) and may differ from firms' own assessments. Seplat's 2025 assessment is an example.

**Plain summary:** in 2020–2025, Nigerian listed firms' reports rarely connect physical climate hazards to the places where those hazards were measured. That is consistent with decoupling as described in institutional theory, and also with a pre-mandate period, materiality choices and data costs. The study cannot separate these.

---

## 5. Recommendations

Each recommendation is linked to a finding. They are proposals for discussion, not conclusions drawn from tests.

| # | For | Recommendation | Linked to | Why feasible |
|---|---|---|---|---|
| R1 | **FRC and SEC** | In implementation guidance for the 2028 mandate, ask for a **site or asset table**: each material facility or asset type, its location (state or coordinates), and the physical hazards assessed. It operationalises S2 13(b) and 29(c) | F2: 0 of 51 on reading (7 raw dictionary matches) | It uses requirements already in IFRS S2; firms already list facilities in their reports (the census site list came from them) |
| R2 | **FRC, with national hazard data holders** | Publish or endorse a **shared national hazard reference** (flood, heat, water stress) that firms can use for screening, as "reasonable and supportable information … without undue cost or effort" (S2 para 11) | F1, F3 | This study scored 125 sites from open global datasets (JRC, Aqueduct, ERA5). A national reference would lower costs, especially for smaller firms. Which agency should host it is **not verified** |
| R3 | **FRC (readiness test)** | Extend the readiness test (Roadmap PDF pp20–21: materiality assessment, scenario models) to check, per hazard and per main site, that physical risk was assessed, even if it is then judged immaterial | F1, F3 | The test already collects these documents; it would add a checklist, not a new filing |
| R4 | **Investors and NGX** | In engagement and in any NGX sustainability guidance update (2018 Guidelines, p8), ask issuers to (a) state which sites were screened for which hazards and (b) report the S2 29(c) metric. Investors can run an open-data screen of disclosed sites, as this study did, to target questions | F1, F2, F4 (a baseline before 2028) | It requires no new regulation; it needs the facility lists issuers already publish |
| R5 | **Firms** | Report physical risk at the level where hazards occur: name the facility, the hazard, the time horizon and the response, and link community flood programmes to asset risk where they share a location. Seplat's 2025 licence-level assessment is a partial model | F2; Seplat case (§3) | Builds on content some firms already produce |

**What is not recommended:**
- **No rankings:** firm-level rankings or claims about individual firms' motives (design h, small-N caveat).
- **No mandate before 2028:** any requirement that would pre-empt the SEC/FRC timeline.

---

## 6. What we can and cannot say (policy)

**We can say:**
- In the documents held, physical-risk language is rare.
- Exposed sites are rarely discussed as physically at risk.
- Firm characteristics account for more of the variation than measured exposure does.
- IFRS S2 (13(b), 29(c), B65(b), 22, 25) asks for exactly the location-specific content that is mostly missing.
- Nigeria's mandate starts with periods beginning 1 January 2028, so 2020–2025 is a pre-mandate baseline.

**We cannot say:**
- That firms breach IFRS S2: it did not apply to them.
- That silence is deliberate.
- That exposure has no relation to disclosure: H1 is not estimable in practice.
- That the Seplat case is typical.
- That any recommendation would change disclosure.

---

## 7. Phase 7 verification list

| # | Claim | Check against |
|---|---|---|
| 1 | All Phase 5 numbers quoted in §1 (68/97; 2 of 15; 6 of 21; 7 of 51; 50 of 51; H2 and H3 figures) | `outputs/tables/*`, `docs/phase5_analysis.md` |
| 2 | Each IFRS S2 paragraph number and its paraphrase (3(a)(i), 10(a)–(d), 11, 13(b), 22, 25(a)(i)–(iii), 29(c), B65(b), B1–B18, C1, Appendix A) | `data/raw/manual/policy/issb-2026-a-…pdf` |
| 3 | SEC circular dates; FRC phases, readiness test and assurance pages; NGX p8 wording | Live pages / PDFs listed in `docs/data_sources.md` |
| 4 | Seplat 2023 SR: water-stress statements, the IFRS S2 index pointing to the 2023 AR | 2023 SR pp21–37, 110–111 |
| 5 | Seplat 2025 IAR: asset-level assessment (13 hazards, three scenarios, IPCC data, OML exposures, "limited impact" statement) | 2025 IAR pp139–154 |
| 6 | Seplat 2025 SPR: Ibeno flooding framed as a community issue; whether the Qua Iboe Terminal lies in Ibeno | 2025 SPR p72; a primary location source |
| 7 | IFRS S1 materiality provisions (referred to, not read) | IFRS S1 (not held) |
| 8 | **Policy codes P1–P7 (A25):** re-check all 38 positive codes against their pages (`policy_codes_evidence.csv`); re-read a sample of zero-coded firm-years that have candidate matches (`policy_decisions.csv` notes, especially Dangote FY2025 P5, Seplat FY2020 P1, Guinness FY2025 P2/P6, Okomu FY2023/24 P5); confirm that P6 "voluntary" (MTN, Seplat FY2025) rests on explicit statements of compliance | Firm documents (pages in the evidence file) |
| 9 | The "2028 readiness" counts in §2b (2 of 56 with P1–P5; 6 with at least one; 26 FS-only latest years) | `policy_codes_firm_year.csv`, `outcomes_firm_year.csv` |

**Code and data used:** none new, apart from read-only text searches of the two Seplat reports outside the corpus. No outcome, measure or file in `data/processed/` was changed.
