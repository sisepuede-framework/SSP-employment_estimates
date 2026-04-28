# Paper 3 — Session Memory

## Paper Identity

- **Working title:** "When Do Climate Investments Create Jobs? The Conditions Behind Employment Creation"
- **Research question:** Under what cost-structure conditions do climate mitigation investments generate positive job demand, and how do these conditions vary across country contexts?
- **Core novelty:** RDM/scenario discovery applied to employment effects of climate mitigation — unexplored territory. Treats cost-structure parameters as uncertainties rather than fixed inputs.
- **Framework pipeline:** SISEPUEDE (emissions pathways) -> Cost estimation (with learning curves) -> MINDSET (MRIO/IO employment) -> Scenario discovery (PRIM/classification trees)
- **Country cases:** Mexico, Belize, Uganda, Egypt, Morocco, Libya, Bulgaria (7 World Bank CCDR engagements)
- **Target journals (ranked):** Global Environmental Change, Climate Policy, Energy Policy, Environmental Science & Policy

## Three Gaps the Paper Fills

1. **No transformation-level traceability** — existing work connects sectors to employment, not specific mitigation actions at specific intensities
2. **Cost structures treated as fixed** — nobody systematically explores how capital intensity, import dependence, learning dynamics, and technology costs shape employment outcomes
3. **No conditional findings** — point estimates rather than conditions under which employment co-benefits hold or break down

## Key Methodological Choices

- I-O (not CGE) framework — justified because the question is about conditions for positive job *demand*, not equilibrium employment levels
- RDM framing turns the I-O static limitation into a feature by treating structural parameters as uncertainties
- Five uncertainty dimensions: capital intensity, import shares, learning rates, technology costs, labor productivity
- Explicit exclusions: job quality, distributional effects, transition costs for displaced workers, O&M employment

## Literature Review Structure (Section 2)

- 2.1 Employment effects of climate mitigation (I-O tradition, CGE tradition, sector-specific, LAC/developing country evidence)
- 2.2 The three gaps (traceability, cost structures as fixed, no conditional findings)
- 2.3 DMDU and scenario discovery (methodological motivation)

## Key Literature Clusters Identified

### A. Green Employment Multipliers (I-O and CGE)
- Garrett-Peltier (2017) Economic Modelling — benchmark comparative study
- Wei, Patadia & Kammen (2010) Energy Policy — early systematic comparison
- ILO (2018) World Employment/Social Outlook — global CGE, 24M net jobs claim
- Montt et al. (2018) International Labour Review — CGE, small net positive
- Saget, Vogt-Schilb & Luu (2020) IDB/ILO — LAC net-zero jobs
- E3ME model (Mercure et al. 2018, Pollitt et al.) — macro-econometric, allows unemployment

### B. Cost Structures / Learning Curves
- Arrow (1962) Review of Economic Studies — foundational learning by doing
- Way et al. (2022) Joule — probabilistic cost forecasts outperform experts; key support for treating costs as uncertainty
- Rubin et al. (2015) Energy Policy — learning rate review for electricity technologies
- Kavlak, McNerney & Trancik (2018) Energy Policy — decomposing PV cost reduction causes

### C. DMDU / Scenario Discovery
- Lempert, Popper & Bankes (2003) RAND — RDM founding text
- Lempert (2002) PNAS — new decision sciences
- Bryant & Lempert (2010) TFSC — PRIM application to scenario discovery
- Marchau et al. (2019) eds. Springer — definitive DMDU collection
- Kwakkel (2017) EMS — Exploratory Modeling Workbench

### D. Just Transition / Developing Country Climate Employment
- Vona et al. (2018, 2019) — green jobs empirics
- Curtis & Marinescu (2023) — green energy jobs US
- Bowen et al. (2018) — characterizing green employment
- World Bank CCDRs — institutional context

## Advisor Discussions

- Initial outline and structure discussed and drafted (see Paper - Outline (Brainstorm).docx)
- Immediate priority: rigorous literature review positioned within economics, open to climate literature inputs

## Resolved / Partially Resolved Questions

1. **Uncertainty dimension ranges** — PARKED. Coauthors lead this. Tentative approach: cross-country variation first, literature parameters to fill gaps. Revisit before writing Section 3.6.
2. **Counterfactual (RESOLVED)** — Baseline is no-investment scenario. Paper is Version A: "under what conditions do climate investments generate *substantial* employment?" NOT Version B (winners/losers from reallocation — would require modeling displacement/contraction side, which the pipeline doesn't do). Scenario discovery classifies HIGH vs. LOW job creation (or above/below a policy-relevant threshold), not positive vs. negative in absolute terms. The outline language "positive vs. negative" needs revision — I-O demand shocks are mechanically positive; the real variation is in magnitude and sectoral concentration.
3. **Country heterogeneity mapping** — NOT YET DONE. Practical justification (CCDR funder engagements) is honest but insufficient for a journal paper. Need to map each country on: income level, manufacturing share, energy import dependence, labor intensity. To-do before writing Section 4.2.
4. **Transformation-level traceability** — IN PROGRESS. First paper established the transformation → cost structure → sectoral employment mapping. This paper extends that by exploring how cost-structure assumptions affect outcomes. Need to review first paper file to assess granularity.
5. **Defense of labor demand without job quality** — UNRESOLVED. Occupational analysis may be partially included. Need a one-paragraph argument for why quantity of labor demand is a useful first-order metric. Literature review will surface the debate (Bowen et al. 2018, Vona et al. 2018/2019).

## Key Framing Decision: Version A vs. Version B (Session 2)

We identified two possible framings for the paper. **The paper is Version A.**

### Version A — "Conditions for substantial job creation" (CHOSEN)
- **Question:** Under what cost-structure conditions do climate mitigation investments generate substantial employment?
- **Counterfactual:** No investment. The pipeline injects mitigation expenditure into the I-O model and measures the employment generated.
- **What it can show:** Magnitude of job creation varies by cost-structure assumptions (capital intensity, import shares, learning rates, etc.) and by country context. Sectoral decomposition shows *where* jobs concentrate. Scenario discovery identifies the conditions that make the employment dividend large vs. negligible.
- **What it cannot show:** Which sectors *lose* jobs in the transition. Because no demand is removed — only added — results are mechanically positive. The variation is in magnitude, not sign.
- **Scenario discovery classifies:** High vs. low job creation (above/below a policy-relevant threshold), NOT positive vs. negative.

### Version B — "Winners and losers from the net-zero transition" (NOT THIS PAPER)
- **Question:** Which sectors gain and which lose when investment shifts from BAU patterns to mitigation portfolios?
- **Counterfactual:** BAU investment/spending patterns. Would require: (1) defining a credible BAU demand vector, (2) computing employment sustained by BAU demand, (3) computing employment under mitigation demand, (4) taking the difference.
- **What it would show:** Net employment effect = green jobs created minus brown jobs lost. Could identify genuinely negative sectoral outcomes and transition vulnerabilities.
- **Why we're not doing it:** Constructing a credible BAU demand vector is a separate analytical challenge. The pipeline currently only models incremental employment from demand shocks, not displacement of existing demand. Bolting this on would distract from the core contribution.
- **Where to mention it:** Limitations (Section 6.4) — name displacement explicitly as something not modeled and why. Future directions (Section 7) — flag as extension.

### Displacement: What It Would Require (for future reference)
- Mechanically simple in I-O: same Leontief equation run twice (BAU demand vector vs. mitigation demand vector), then subtract. Math is trivial.
- The hard part: constructing a credible BAU demand vector — what *would* have been spent absent the climate investment. This is a counterfactual assumption, not a modeling problem.
- Could be a natural extension paper or a robustness check if coauthors want to pursue it later.

## Timeline and Constraints (from Dissertation/Planning/)

- **Deadline:** August 1, 2026 (16 weeks from Apr 13)
- **Two papers simultaneously:** Paper 2 (Central Asia heat/labor) + Paper 3 (this one)
- **PhD hours/week:** 22.75 BAU, currently ~40 (no RAND projects — temporary acceleration window)
- **Paper 3 lit review window:** Weeks 1-3 (Apr 13 – May 2). By end of Week 3, Section 2 must be drafted.
- **Monday = Paper 3 day** (3 hrs deep work + 8 PM research group meeting)
- **Paper 2 seminar:** April 23 — dominates Week 2
- **Week 6 checkpoint:** May 25 — assess if on track
- **Realistic reading budget for lit review:** ~20-25 hrs total → 9-10 careful reads + 7-8 skims
- **Full reading schedule:** see READING_LIST.md
- **Full planning docs:** see Dissertation/Planning/ folder (00_Plan_Overview, 01_Weekly_Schedule, 02_Milestones_Timeline)

## Key Research Group (not coauthors)

- **Mealy, Bucker, Senra de Moura, Knudsen** (+ del Rio-Chanona, Farmer) — World Bank / Oxford cluster
- Authored: "Five Frictions" (WP 11224), "Beyond Green Jobs" (WP 11262), Bucker et al. (2025) Joule, occupational skill space paper
- They laid out the conceptual agenda this paper operationalizes empirically
- Positioning: they argue for conditional analysis; you implement it with scenario discovery across 7 countries

## First Paper Reference

- **File:** `C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\Sisepuede - Economic Module\Employment_Multiplier_LAC_paper_published.pdf`
- **Published in:** Frontiers in Climate (2024)
- **Title:** Employment effects of climate mitigation investment in Latin America (approximate)
- **What it established:** Pipeline from SISEPUEDE transformations → cost structures → I-O sectoral mapping → employment multipliers. Applied to LAC countries. This paper (Paper 3) extends it by: (1) adding learning curves, (2) parameterizing cost-structure uncertainty, (3) applying scenario discovery, (4) expanding to 7 countries across different regions.

---
*Last updated: 2026-04-13*
