# Key numbers used in paper/paper.md

One line per number, with its source file. "Phase 7" = `docs/phase7_verification.md`.

## Regulation and standards
- 1 January 2028 — mandatory IFRS S1/S2 start for public-interest entities (periods beginning on or after) — SEC circular; Phase 7 §4
- 1 January 2030 — SME start — SEC circular; FRC Roadmap pp19–20; Phase 7 §4
- 1 January 2024 to 31 December 2027 — voluntary adoption window — SEC circular; Phase 7 §4
- 23 September 2026 — SEC circular publication date — SEC circular; Phase 7 §4
- 15 October 2026 — Implementation Plan deadline — SEC circular; Phase 7 §4
- 31 December 2023 — end of FRC early-adopter phase — FRC Roadmap pp19–20; Phase 7 §4
- third year of reporting — assurance start — FRC Roadmap p30; Phase 7 §4
- 9 November 2018 — SEC approval of NGX Guidelines — NGX Guidelines p1; Phase 7 §4
- 1 January 2024 — IFRS S2 effective date (para C1) — `data/raw/manual/policy/issb-2026-a-…pdf`; Phase 7 §4
- IFRS S2 paras 3(a)(i), 10(a)–(d), 11, 13(b), 22, B1–B18, 25(a)(i)–(iii), 29(c), B65(b), C1, Appendix A — Phase 7 §4

## Design and amendments
- 7 November 2026 — design freeze date — `docs/design.md`; `docs/amendments.md`
- A1–A26 — amendments — `docs/amendments.md`
- 0.80 — pre-set precision bar — `docs/amendments.md` A20
- 0.25 — readability threshold (share of top-1,000 English words) — `docs/amendments.md` A1
- 40 words — minimum scored paragraph length — `docs/design.md` f3
- 9,999 — bootstrap replications — `docs/design.md` h (OD-14); `docs/amendments.md` A22

## Census, corpus, sites
- 146 — tickers in NGX list of 6 November 2026 — `docs/phase0_audit.md`
- 59 / 18 — main census / robustness stratum firms — `docs/phase0_audit.md`
- 3 — main-census firms failing the document test — `docs/phase2_sites.md` (AUSTINLAZ, PHARMDEKO, PREMPAINTS)
- 56 — main-census firms — `outputs/tables/sample_flow.csv`
- 100 / 99 — main-census firm-years before / after A23 exclusion — `outputs/tables/sample_flow.csv`
- 107 documents, 12,143 pages, 103 firm-years — corpus — `docs/phase4_corpus.md` §9.3
- 15,601 — scored narrative paragraphs — `docs/phase4_corpus.md` §6.5
- 214 — sites in the site dictionary — `docs/phase4_corpus.md` §9.3
- 16 — hazard dictionary terms — `docs/amendments.md` A20
- 403 — candidate sentences for policy coding — `docs/phase6_policy.md` §2b
- 71 (26 grade A, 45 grade B) — main-analysis point sites — `docs/phase3_hazards.md` §1.1
- 22 of 26 — grade-A sites that are town/suburb centroids — `docs/phase3_hazards.md` §6
- 43 / 25 / 18 / 5 — main sites exposed to river flood / heat / water stress / coastal flood — `docs/phase3_hazards.md` §2
- 58.8 days per year — ERA5 heat tercile cut-off — `docs/phase3_hazards.md` §1.4
- 2 km / 500 m / polygon + 250 m — buffers — `docs/phase3_hazards.md` §1.2
- 27 / 29 — main-census firms with / without an exposure score — `outputs/tables/sample_flow.csv`; Phase 7 §5
- 39 of 71 — main buffers containing permanent water — `docs/phase3_hazards.md` §2
- 2 — sites with modelled depth > 10 m — `docs/phase3_hazards.md` §6
- −0.01 (Spearman), 47 of 71 — ERA5 vs NASA POWER heat disagreement — `docs/phase3_hazards.md` §6
- about 0.9 km — coastal layer resolution — `docs/phase3_hazards.md` §1.5
- 42 pages — text lost by forced OCR — `docs/phase2_sites.md` (update 5)

## Precision check
- 46 (planned 100) — snippets checked — `docs/amendments.md` A20
- 30/46 = 0.65 (exact 95% 0.50–0.79) — overall precision — `data/interim/precision_results.csv`; `docs/amendments.md` A21
- 13/14, 1/8, 9/10, 3/3, 4/11, 0/0 — precision by family (flood, storm, drought/water stress, heat, coastal/erosion/sea level, wildfire) — `docs/amendments.md` A21
- storm 1/8, erosion 2/6, coastal 1/4 — weak terms — `docs/amendments.md` A21
- 5 — maximum snippets per firm — `docs/amendments.md` A20

## Verification
- 11 paragraphs in 8 firm-years; 10 false positives, 1 genuine — re-read of site-named hazard paragraphs — Phase 7 §3
- 12 — flagged control values re-checked; 1 corrected (A26) — Phase 7 §2
- 35 hashed outputs, 28 byte-identical — reproducibility — Phase 7 §6
- 38 positive policy codes confirmed; 20 zero-coded sample all correct — Phase 7 §3

## Results
- 97 — main firm-years with narrative text — Phase 7 §8 claim 1; `outputs/tables/robustness_7b_descriptive.csv`
- 68 of 97 — firm-years with no hazard-tagged paragraph — Phase 7 §8 claim 1; `outputs/tables/robustness_7b_descriptive.csv`
- about 0.3% (mean Y3d 0.0031) — average share of hazard-tagged narrative paragraphs — `outputs/tables/robustness_7b_descriptive.csv`
- 51 / 50 / 7 / 0 — exposed main point sites / named anywhere / named in hazard paragraph (mechanical) / genuine (on reading) — `outputs/tables/gap_sites_by_hazard.csv`; Phase 7 §3, §8 claim 2
- 38/37/5, 23/22/1, 16/15/2, 4/4/0 — exposed / named / named in hazard paragraph, by hazard — `outputs/tables/gap_sites_by_hazard.csv`
- 21 / 6 — firms with river-flood-exposed site / using river flood terms — `outputs/tables/gap_firm_hazard.csv`; `docs/phase5_analysis.md` §2 (Phase 7b correction)
- 15 / 2 — firms with heat-exposed site / using heat terms — `outputs/tables/gap_firm_hazard.csv`; Phase 7 §8 claim 3
- 13 / 4 — water stress firms / using terms — `docs/phase5_analysis.md` §2
- 2 / 2 — coastal flood firms / using terms — `docs/phase5_analysis.md` §2
- 1 of 51 (2.0%; exact 95% 0.05%–10.4%) — H4, exposed sites never named — `outputs/tables/h4.csv`; `docs/phase5_analysis.md` §3
- 29 / 0 / 2 / 22 / 5 / 16 — unscored firms: total / office only / dispersed only / generic (C1) / no coordinate (C2) / FS-only — `outputs/tables/unscored_firms_reasons.csv`
- 69 firm-years, 27 firms — H1/H2 sample — `outputs/tables/sample_flow.csv`
- 25 firm-years, 12 firms; 8 non-zero from 4 firms — H1 primary outcome — `outputs/tables/sample_flow.csv`
- 80–86% — fractional logit bootstrap failure rate — `outputs/tables/h1_results.csv`; `docs/phase5_analysis.md` §4
- 0.04 (0.00 to 0.15) / 0.17 (0.11 to 0.43) / −0.13 (−0.37 to −0.06) — H2 R² added by exposure / institutional / difference — `outputs/tables/h2_results.csv`
- 0.02 / 0.23 / −0.21 (−0.43 to −0.11) — H2, refined dictionary — `docs/phase5_analysis.md` §5
- 66 firm-years, 26 firms — H3 sample — `outputs/tables/h3_results.csv`
- +0.013 (−0.113 to +0.141) / +0.052 (−0.015 to +0.120) / −0.039 (−0.147 to +0.071) — H3 main τ(Y3d), τ(Y4r), difference — `outputs/tables/h3_results.csv`
- +0.007 / +0.049 / −0.041 — H3 pre-listing years included — `outputs/tables/h3_results.csv`
- +0.057 / +0.048 / +0.009 — H3 refined dictionary — `outputs/tables/h3_results.csv`
- 46 / 7 / 3 — firms whose latest year held is FY2025 / FY2024 / FY2023 — `docs/phase6_policy.md` §2b
- 4, 4, 2, 5, 4, 2, 4, 2 — firms with P1, P2, P3, P4, P5, P6 voluntary, P6 readiness, P7 (latest year) — `data/processed/policy_codes_firm_year.csv`; `docs/phase6_policy.md` §2b
- 2 of 56 / 6 / 50 — firms with all five P1–P5 / at least one / none — `data/processed/policy_codes_firm_year.csv`; Phase 7 §8 claim 7
- 26 of 56 — latest years that are FS-only filings — `docs/phase6_policy.md` §2b
- 45 firms, 0 with all five — point sites only or none — `outputs/tables/robustness_7b_descriptive.csv`

## Robustness (Phase 7b)
- 57 / 56 / 7 — exposed / named / named in hazard paragraph, 5 km buffer — `outputs/tables/robustness_7b_descriptive.csv`
- 68 / 39; 0.44% — excluding FS-only: firm-years with narrative / no hazard paragraph; mean Y3d — `outputs/tables/robustness_7b_descriptive.csv`
- 49 / 45 / 7 — excluding FS-only: exposed / named / named in hazard paragraph — `outputs/tables/robustness_7b_descriptive.csv`
- 14 / 2 — excluding FS-only: heat firms / using terms — `outputs/tables/robustness_7b_descriptive.csv`
- 2 / 31 (37) — excluding FS-only: all five / none (firms) — `outputs/tables/robustness_7b_descriptive.csv`
- 95 / 66; 2 / 48 (54) — excluding DWL firms — `outputs/tables/robustness_7b_descriptive.csv`
- 3 firm-years, 5 exposed sites, 0 named in hazard paragraph — robustness stratum — `outputs/tables/robustness_7b_descriptive.csv`
- about −0.13 — H2 difference under RP10, RP500, depth ≥ 0.5 m, 5 km — `outputs/tables/robustness_7b_models.csv`
- −0.15 (−0.43 to −0.06) — H2 excluding FS-only — `outputs/tables/robustness_7b_models.csv`
- −0.13 (−0.39 to −0.06) — H2, 20% foreign-parent threshold — `outputs/tables/robustness_7b_models.csv`
- −0.10 (−0.37 to −0.04) — H2, 20% threshold with Seplat FY2025 coded 1 — `outputs/tables/robustness_7b_models.csv`
- −0.06 to −0.19; −0.06 (−0.37 to −0.01) — H2 leave-one-sector-out range; Industrial Goods left out — `outputs/tables/robustness_7b_models.csv`
- 27 — H3 intervals across checks, all including zero — `outputs/tables/robustness_7b_models.csv`; Phase 7 §9
- 2 — DWL-flagged firms — `docs/design.md` c; Phase 7 §9
- 28 — main-census firms with one year only — `docs/phase4_corpus.md` §6.6, §9.3

## Seplat case
- 1 of 548 — hazard-tagged paragraphs, 2020 annual report — `docs/phase6_policy.md` §3
- 12 of 653 (1.8%) — hazard-tagged paragraphs, 2025 integrated report — `docs/phase6_policy.md` §3
- three IPCC scenarios (SSP1-2.6, SSP2-4.5, SSP5-8.5; 2030, 2040, 2050) — Seplat 2025 IAR PDF p153 (read 2026-11-18)
- thirteen hazards analysed for offshore assets — Seplat 2025 IAR PDF p154 (read 2026-11-18)
- OML 40 (p153) — licence area at physical risk — Phase 7 §3
- p112 — IFRS SDS compliance statement — Phase 7 §3
- 3 — Seplat main point sites — `docs/phase6_policy.md` §3

## Added in Phase 8 owner review
- 13 / 2 — NASA POWER heat: firms with a heat-exposed site / using heat terms — `outputs/tables/robustness_8_nasa_heat_silence.csv`; Phase 7 §10
- 9 — firms heat-exposed under both ERA5 and NASA POWER — `src/phase8_nasa_heat_check.py` output; Phase 7 §10
- 11 / 9 / 1 — robustness checks listed in the design / run in Phase 7b / not run (R1–R3 location sets); OLS run in Phase 5 — `docs/design.md` h; Phase 7 §9
- 68 (66) firm-years, 27 (26) firms — H3 sample, with narrative text in brackets — `outputs/tables/sample_flow.csv`; `docs/phase5_analysis.md` §1
- wordfreq 3.1.1 — version used — `requirements.txt`; `docs/data_sources.md`
