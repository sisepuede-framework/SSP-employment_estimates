# Paper 3 — Literature Summaries for Section 2

Summaries of all 16 papers in the Tier 1/2/3 reading folders. Each summary covers the paper's main contributions and why it matters for *"When Do Climate Investments Create Jobs?"*

**Note on sourcing:** Summaries were extracted directly from the PDFs where possible. Garrett-Peltier (2017) and Mercure et al. (2018) could not be extracted from PDF due to environment limitations; those summaries draw on well-established knowledge of these widely-cited papers. All citations should still be verified against the actual text before inclusion in the dissertation.

---

## TIER 1 — Full Reads (4 papers)

---

### #3 Hanna, Heptonstall & Gross (2024) — "Job creation in a low carbon transition to renewables and energy efficiency: a review of international evidence" — *Sustainability Science*

**What it is:** Systematic literature review of 121 publications on employment from low-carbon energy transitions, following PRISMA 2020.

**Key findings:**
- Renewables consistently generate more jobs per MW, per MWh, and per $M invested than fossil fuels — across virtually all metrics and lifecycle stages
- Employment factors by technology (job-years/MW): Solar PV highest (C&I: 6-25+), onshore wind moderate (C&I: 2.5-8), offshore wind higher than onshore, gas/coal lowest
- Employment factors are **declining over time** as technologies mature
- 18 national-level studies find modest net positive employment from decarbonization, but with severe regional/sectoral/skills mismatches
- Cross-country variation is substantial but understudied; evidence base heavily skewed toward OECD

**Identified gaps:**
1. No standardization in methods/metrics (FTE vs headcount, system boundaries, normalization)
2. Very limited evidence on job *quality*
3. Geographic distribution understudied
4. Developing countries underrepresented
5. Dynamic/temporal aspects rarely modeled
6. No studies treating cost-structure parameters as uncertain

**Methodological critique of the field:**
- Employment factor studies lack clarity on gross vs net, FTEs vs headcount, direct vs indirect/induced
- Jobs-per-investment metric conflates labor intensity, wages, capital costs, import shares, and maturity
- I-O models' fixed-coefficient assumption is problematic for transitions where production structure is changing
- CGE models sensitive to closure assumptions and elasticity parameters

**Why it matters for your paper:**
- Provides the empirical ranges for employment factors across technologies and countries
- The explicit caution that jobs-per-investment "may be indicative of various factors including relative technological maturity, share of spending on local content or imports, share of spending on labour (versus capital), and average salary levels" is essentially a call for your analysis
- Documents the fragility of point estimates that your scenario discovery interrogates
- Confirms the developing-country evidence gap your 7-country analysis helps fill

**Key quote for citing:** The caution about jobs-per-investment reflecting "relative technological maturity, share of spending on local content or imports, share of spending on labour (versus capital), and average salary levels"

---

### #5 Bucker, del Rio-Chanona, Pichler, Ives & Farmer (2025) — "Employment dynamics in a rapid decarbonization of the US power sector" — *Joule*

**What it is:** State-of-the-art I-O employment study with a 4-step pipeline for the US power sector.

**The 4-step framework:**
1. **Energy-system cost scenarios** → NREL Cambium/Standard Scenarios provide capacity additions/retirements + ATB cost curves
2. **I-O translation** → Disaggregate BEA I-O tables into 11 energy sub-industries; cost vectors distribute spending across sectors; Leontief inverse propagates indirect effects
3. **Occupational demand** → BLS occupation-by-industry matrix (539 occupations) converts industry labor demand to occupational demand
4. **Friction/reallocation network** → O*NET relatedness network assesses transition feasibility for displaced workers

**Key findings:**
- 95% decarbonization by 2035 generates ~600,000 additional jobs at peak (2034), declining to ~100-150K steady state by 2040s
- "Boom and partial bust" temporal pattern — massive construction surge followed by permanent but smaller O&M workforce
- Three occupation types: **consistent growth** (3 occupations — Solar PV Installers, Wind Turbine Techs, Power-Line Installers), **temporary growth** (~100 occupations — construction trades, manufacturing), **consistent decline** (~14 fossil-fuel occupations)
- Network assortativity during scale-down (0.23-0.26, p<0.001) shows real reallocation friction — declining occupations cluster together

**How they handle cost structures:**
- Cost vectors (K) treated as **FIXED** throughout — Hicks-neutral technical change assumption
- Quote: "we assume cost-factor neutral technical change, meaning that we allow for unit cost per technology to change, but not how each dollar is spent"
- Sensitivity analysis: one-at-a-time perturbation across 8 dimensions (Table S18), random noise on cost vectors (30 runs, sigma=0.5)
- T&D costs and ATB technology cost curves are the largest uncertainty sources at peak; imports matter most at steady state

**Critical acknowledgment:** "The cost breakdown of energy technologies, i.e. how much of every dollar spent on a technology goes to each sector of the economy, affects labor demand estimates directly."

**What they do NOT do (= your contribution):**
1. No systematic exploration of cost-structure parameter space (only random noise perturbation)
2. No identification of tipping points / qualitative regime shifts
3. One-at-a-time sensitivity only — no interaction effects
4. No decision-relevant framing (robustness check, not decision support)
5. No exploration of structurally different cost scenarios (e.g., IRA domestic content shifts)
6. Predict-then-act framing, not explore-then-adapt

**Positioning:** Your primary competitor. They built the state-of-the-art pipeline but left the cost-structure parameter space unexplored. Your scenario discovery fills exactly this gap.

---

### #12 Mealy, Bucker, Senra de Moura & Knudsen (2025) — "Beyond Green Jobs: Advancing Metrics and Modeling Approaches for a Changing Labor Market" — WB WP 11262

**What it is:** Conceptual framework paper arguing the field should move beyond static "green job" counts toward conditional, scenario-based analysis.

**Core critique:**
- No universally accepted definition of "green job" — competing approaches (output-based, process-based, occupation/task-based) yield wildly different estimates
- O*NET identified ~12% of US occupations as green; BLS counted 3.1M; UK ONS estimated 2.2%-7.7% depending on definition
- Static counts are useless for forward-looking policy

**What "Beyond Green Jobs" means — the proposed shift:**
- From "how many green jobs?" to "which jobs will be in demand / at risk under different scenarios?"
- Three-pillar framework: (1) Estimating jobs-in-demand, (2) Estimating jobs-at-risk, (3) Assessing labor mobility/transition feasibility
- Scenario-conditionality over point estimates
- Occupational granularity (4-6 digit ISCO/SOC, not sector-level)
- Explicit labor market frictions

**Key quotes for your framing:**
- "Rather than focus on static definitions of green jobs, we advocate for a more flexible, scenario-based framework centered on identifying 'jobs-in-demand' and 'jobs-at-risk' under different green transition pathways."
- "Estimates of net employment change from the green transition range from significant net gains of 8 million (ILO, 2018) to net losses of 80 million (Malerba & Wiebe, 2024)." — This +8M to -80M spread is exactly the deep uncertainty scenario discovery characterizes.

**View on modeling approaches:**
- I-O: useful for first-order estimates, no price/substitution effects, no supply constraints
- CGE: captures feedbacks but typically assumes perfect labor mobility (unrealistic)
- Hybrid macro-micro: most promising — link CGE/I-O with microsimulation for heterogeneous worker outcomes
- No single approach sufficient

**Developing-country focus:** Strong. Data scarcity in LMICs, borrowing O*NET as proxy, informality, Uzbekistan worked example in appendix

**Why it matters:** This is your conceptual anchor. They call for scenario-based conditional analysis; you deliver it empirically with scenario discovery across 7 countries. Your paper is the operationalization of their research agenda.

---

### #15 Knudsen, Senra de Moura, Bucker & Mealy (2025) — "Five Frictions: Key Labor Market Barriers to Unlocking Job Growth in the Green Transition" — WB WP 11224

**What it is:** Framework classifying labor market frictions that prevent green investments from translating into realized employment.

**The five frictions:**
1. **SKILL mismatches** (What workers do) — e.g., Namibia: only 6/63 green hydrogen occupations overlap with unemployed workers' skills
2. **SPATIAL mismatches** (Where workers are) — e.g., Brazil: 88% of job switches within same state; Pakistan: RE training concentrated away from highest solar/wind potential
3. **TEMPORAL mismatches** (When workers are available) — Bucker et al.'s three phases (scale-up, scale-down, steady-state); Tajikistan: 65K workers needed temporarily for rooftop solar, then demand drops
4. **NORM mismatches** (Who workers are) — Gender segregation: Georgia 54% of occupations are 85%+ single-gender; green occupations tend male-dominated
5. **PREFERENCE mismatches** (Why people work) — Malaysia: oil-to-electronics transition faces 20-70% wage cuts; Poland: ZE PAK mine retrained 50 workers but only 14 accepted (commute + age)

**Why point estimates are insufficient:**
- ILO's 24M jobs estimate "operate under the assumption that labor markets are highly efficient and that workers can transition from declining sectors to those experiencing growth"
- Each friction can independently prevent potential jobs from becoming realized jobs
- Frictions "rarely exist in isolation" — they interact and compound

**Deep uncertainty framing:**
- Not their language, but the structure is inherently about deep uncertainty: outcome depends on five categories of uncertain conditions that vary by country, sector, and time
- Calls for incorporating frictions into macroeconomic modeling but does NOT itself do so
- "Existing tools typically cannot quantify how long or costly these frictions will be"

**Frictions mappable to scenario discovery parameters:**
- Skill: transferability scores, retraining rates, education responsiveness
- Spatial: geographic co-location, relocation willingness, transport infrastructure
- Temporal: transition speed, learning-curve slopes, investment continuity
- Norm: workforce exclusion rates, effectiveness of inclusion policies
- Preference: wage gaps, non-monetary job attributes, subsidy effectiveness

**Developing-country evidence:** Extensive — Namibia, Brazil, Tajikistan, Pakistan, Georgia, Poland, India, Bhutan, South Africa, Malaysia, Djibouti. All from World Bank CCDRs.

**Why it matters:** Provides the conceptual scaffolding for *why* scenario discovery is needed. Logic chain: aggregate estimates assume frictionless markets → five frictions prevent realization → severity is deeply uncertain and context-dependent → existing tools can't quantify this → scenario discovery fills the gap.

---

## TIER 2 — Targeted Reads (7 papers)

---

### #1 Garrett-Peltier (2017) — "Green versus brown: Comparing the employment impacts of energy efficiency, renewable energy, and fossil fuels using an input-output model" — *Economic Modelling*

**What it is:** The benchmark comparative I-O study of green vs brown employment multipliers for the US.

**Method:**
- US BEA I-O tables, standard Leontief framework
- Compares employment multipliers (jobs per $1M spending) across energy efficiency, renewable energy, and fossil fuel sectors
- Uses "synthetic industry" approach: constructs spending profiles for clean energy as weighted averages of existing BEA sectors (construction, manufacturing, professional services, etc.)
- Captures direct + indirect + induced employment (Type II multipliers with household sector endogenized)

**Key results:**
- Clean energy and energy efficiency consistently produce **more jobs per dollar** than fossil fuels
- Energy efficiency ~7.7 jobs/$M, renewables ~7.5 jobs/$M, fossil fuels ~5.3 jobs/$M (approximate — verify against paper)
- The gap is driven by: (1) higher labor intensity, (2) lower capital-equipment share, (3) more domestic content (less import leakage) in clean energy sectors

**What she treats as fixed (= your uncertainties):**
- Cost vectors (spending profiles) for each technology
- Import fractions
- Labor productivity / technical coefficients
- Wage levels embedded in the I-O table
- All multipliers computed for a single year's I-O structure

**Limitations:**
- Static, single-year snapshot (no dynamics, no learning curves)
- US-only
- Point estimates with no sensitivity analysis
- Treats all parameters as known and fixed

**Why it matters:** The benchmark your paper extends. She estimates multipliers as fixed; you ask under what conditions they change. Her "synthetic industry" cost-vector approach is the same basic method used by Bucker et al. and likely in your pipeline — but she never asked how sensitive her results are to those cost vectors.

---

### NEW: Perrier & Quirion (2018) — "How Shifting Investment Towards Low-Carbon Sectors Impacts Employment: Three Determinants Under Scrutiny" — *Energy Economics* 75, 464-483

**What it is:** Theoretical + empirical decomposition of *why* green investment creates more jobs, comparing I-O and CGE side-by-side for France.

**The three channels:**
1. **Labour intensity** — green sectors have higher labor/capital ratios
2. **Wage levels** — green sectors have lower average wages (so same $ buys more workers)
3. **Import rates** — green sectors have lower import shares (more domestic content)

**Key findings (for 1B euro shift from fossil to clean):**
- Solar PV: +4,670 jobs (CGE), +5,010 (I-O) — I-O overshoots by 7%
- Weatherization: +5,331 (CGE), +8,050 (I-O) — I-O overshoots by 51%
- **Wage curve elasticity is the key source of I-O vs CGE divergence** — when green sectors have lower wages, I-O overstates job gains because it misses the wage-adjustment feedback
- Using Cobb-Douglas (sigma=1) **underestimates employment gains by 17-40%** vs empirically estimated CES (sigma=0.2-0.6)
- Import channel is **nil in CGE** (trade balance closure washes it out) unless receiving sector has zero exports

**Why it matters for your paper:**
- Provides the **theoretical micro-foundations** for your scenario factors: labor share, wage differential, import leakage map directly to your uncertainty parameters
- Disciplines your I-O choice: I-O is a reasonable approximation for solar but overshoots for weatherization-type investments
- The wage curve elasticity finding is crucial for developing countries with large informal sectors
- Capital-labor substitution elasticity should be an uncertain parameter in your RDM runs
- Production function specification (Cobb-Douglas vs CES) materially affects results — another source of deep uncertainty

---

### #10 Saget, Vogt-Schilb & Luu (2020) — "Jobs in a Net-Zero Emissions Future in Latin America and the Caribbean" — IDB/ILO

**What it is:** The canonical LAC green employment estimate using MRIO (EXIOBASE 3).

**Methodology:** Compares net-zero vs BAU scenarios for 2030 using fixed employment coefficients from I-O tables. Not CGE. No price feedbacks, no endogenous wages.

**Headline result:** +15 million net jobs in LAC by 2030 (22.5M created, 7.5M lost)
- Agriculture dominates: livestock→crop shift creates ~19M jobs (crops are far more labor-intensive)
- Energy: net +100K from fossil→renewable shift
- Construction: +540K from green building/retrofitting
- Losses concentrated in fossil fuel extraction and livestock

**Mexico/Belize coverage:** Mexico receives moderate qualitative treatment (geothermal, solar potential, Metrobus BRT); construction multiplier of 2.4 cited. **Belize not mentioned at all.** Quantitative model treats all LAC as a single aggregate — no country-level projections.

**Limitations:** Regional aggregation (no country breakdown), static I-O, no transition dynamics, no informality modeling, no skills/retraining, no uncertainty quantification, strong agriculture assumptions

**Why it matters:** The "canonical estimate" to stress-test. Your paper asks: under what combinations of assumptions does this 15M figure hold, and when does it fail? The absence of country disaggregation, the fixed employment coefficients, and the zero uncertainty analysis are precisely what your scenario discovery addresses.

---

### #6 Ravillard, Chueca, Weiss & Hallack (2021) — "Implications of the Energy Transition on Employment" — IDB Report

**What it is:** Firm-level survey data on energy transition workforce in Chile, Bolivia, and Uruguay.

**Methodology:** Primary data collection through firm surveys (79 firms in Chile, 18 in Bolivia, 81 in Uruguay). NOT econometric or modeling — descriptive empirical snapshot.

**Key findings:**
- Energy transition workforce dominated by **non-qualified workers** (often 60-80% have only basic/secondary education)
- Construction is the largest job category across all firm types and countries
- STEM workers are a minority (18-20% in Bolivia/Uruguay, up to 63% in Chile's emerging firms)
- Female participation extremely low (0-5% in electromobility, higher in niche areas like hydrogen)
- Firms report significant difficulty recruiting qualified workers; many provide their own training
- State dominance of energy sector varies dramatically (Bolivia: 80% of generation is state-owned)

**Mexico/Belize:** Not covered in primary data. Mexico appears in secondary data (low public RE investment relative to GDP). Belize shows moderate hydroelectric investment.

**Why it matters:** Provides ground-truth LAC workforce data that contrasts with theoretical models. The dominance of non-qualified workers and the skill gaps support your argument that employment outcomes are deeply uncertain and context-dependent. Useful for contextualizing the LAC landscape, but cite with caveats (policy report, small samples, not peer-reviewed).

---

### #14 Bryant & Lempert (2010) — "Thinking inside the box: A participatory, computer-assisted approach to scenario discovery" — *TFSC*

**What it is:** The canonical operational description of scenario discovery with PRIM.

**How scenario discovery works (4 steps):**
1. **Generate data** — Latin Hypercube Sample over uncertain parameters → run simulation model → binary classification (cases of interest vs rest)
2. **PRIM identifies candidate scenarios** — iterative "peeling" finds multi-dimensional boxes (e.g., "param A > X AND param B < Y") that predict cases of interest. Produces coverage-density tradeoff curve
3. **Diagnostics** — resampling tests + quasi-p-values validate statistical significance of each parameter constraint
4. **Users select scenarios** — choose box(es) balancing coverage, density, and interpretability

**Application:** US "25x25" renewable energy policy. 9 uncertain parameters, 1000 LHS runs. PRIM found: high costs occur when transportation demand elasticity is high AND biomass backstop price exceeds $148/ton AND biofuel production cost > $72.65 AND low-cost biomass supply < 769 megatons. 79% coverage, 73% density, 4 parameters. Oil supply elasticity proved unimportant despite expectations.

**How it differs from traditional scenario analysis:**
- Reverses direction: starts with "when does policy fail?" not "what does the future look like?"
- Algorithm-driven, not intuition-driven selection of key driving forces
- Scenarios are *regions* of input space (can assign probabilities), not single points
- Handles stakeholder disagreement because the ensemble includes diverse worldviews

**Coverage-density-interpretability trade-offs:**
- Coverage (sensitivity/recall): fraction of all failures captured
- Density (precision/PPV): fraction of cases in box that are failures
- Interpretability: fewer boxes, fewer constrained parameters
- These are in tension; PRIM presents the frontier for user selection

**Why it matters:** Primary methods citation for your Section 2.3. Provides the operational description of what you're doing: LHS experimental design → binary outcome classification → PRIM bump-hunting → interpretable conditions for employment outcomes.

---

### #8 Mercure et al. (2018) — "Macroeconomic impact of stranded fossil fuel assets" — *Nature Climate Change*

**What it is:** E3ME macro-econometric model analysis of stranded assets under low-carbon transition.

**E3ME vs I-O vs CGE:**
- Demand-driven, Keynesian (not equilibrium-based like CGE)
- Econometrically estimated parameters from time series (not calibrated like CGE or fixed like I-O)
- Allows persistent unemployment and underutilized capacity
- Endogenous technology cost dynamics (learning curves via FTT diffusion model)
- 59 regions, 43 sectors

**Key findings:**
- Net positive GDP for most countries; losers are fossil fuel exporters
- $1-4 trillion in potentially stranded fossil fuel assets
- Employment effects follow GDP: mildly positive globally because transition redirects spending toward more labor-intensive activities
- Early, gradual transition less disruptive than delayed, abrupt

**Limitations:** Simplified financial contagion, no explicit skill mismatch/retraining, limited sectoral granularity for employment (43 vs hundreds in I-O), backward-looking parameters, coarse geographic resolution

**E3ME captures what I-O misses:** Macro feedbacks, endogenous technology costs, dynamic adjustment, unemployment as outcome, wealth/financial effects, induced substitution

**I-O offers what E3ME doesn't:** Transparency/decomposability (every result traceable to inter-industry transactions), fine sectoral resolution (hundreds of sectors), reproducibility, occupational extensions, policy transparency (legible causal chains)

**Why it matters:** Provides the one-paragraph positioning for Section 2.1 on why you use I-O rather than macro-econometric models. The two approaches are complementary, not competing.

---

### #9 Montt et al. (2018) — "Does climate action destroy jobs? An assessment of the employment implications of the 2-degree goal" — *International Labour Review*

**What it is:** The archetype "Version B" analysis — net employment effects including displacement, using EXIOBASE 3 MRIO.

**Methodology:** Comparative-static I-O (not CGE despite the paper's framing). Compares IEA 6DS (BAU) vs 2DS (2-degree) scenarios for 2030. 163 industries, 43 countries.

**Headline result:** +18 million net jobs globally (~0.3% of total employment), but **~1% of total employment must be reallocated between sectors**

**Key findings:**
- Most economies show net positives; losers are Middle East, Russia, resource-dependent economies
- Job destruction in fossil fuel extraction; creation in construction, manufacturing, renewables-based electricity
- Supply chain linkages matter more than direct effects — construction/manufacturing are more labor-intensive than fossil fuels
- Government effectiveness associated with smoother transition management
- "Excess job reallocation" metric quantifies displacement: millions must change sectors even in net-positive scenario

**Cost/technology assumptions:** All fixed — relative prices constant, no factor substitution, no learning curves, no new products/technologies, static 2030 snapshot

**Why it matters:** Cite to show awareness of Version B and displacement. Their headline (+0.3% net) is why Version B framing is insufficient for policymakers wanting to maximize job creation. Your Version A asks: under what conditions is gross creation much larger, and what drives the magnitude?

---

## TIER 3 — Quick Reads (5 papers)

---

### #4 Cerny et al. (2022) — "Employment effects of the renewable energy transition in the electricity sector" — *SSRN Working Paper*

**What it is:** Multi-country MRIO (EXIOBASE 3.6) study of electricity transition employment for EU27+UK, 2015-2050.

**Method:** Static Leontief MRIO, 163 sectors, 44 countries + 5 rest-of-world. Two scenarios: EU Reference (moderate) and Stanford WWS (aggressive 100% renewables). Cost structures for each technology from literature, allocated to EXIOBASE sectors.

**Key results:** Both scenarios show net positive EU-aggregate employment; WWS produces massive front-loaded wave peaking ~2025-2030 then declining. Huge country-level heterogeneity (Romania, Greece, Denmark gain most; some countries see declines under Reference).

**Cost structures: FIXED.** Technical coefficients constant throughout 2015-2050. Authors acknowledge: "we work with the assumption of fixed production technologies since this is an uncertain factor in the long run."

**Why it matters:** Closest existing multi-country I-O study. Produces point estimates with zero uncertainty analysis, holds cost structures constant over 35 years. Your paper fills exactly these gaps.

---

### #18 Way, Ives, Mealy & Farmer (2022) — "Empirically grounded technology forecasts and the energy transition" — *Joule*

**What it is:** The definitive empirical case for treating technology cost trajectories as deep uncertainties.

**Headline finding:** Simple statistical models (stochastic Wright's Law) produce more accurate and better-calibrated cost forecasts than expert agencies (IEA, EIA). Expert forecasts have **systematically underestimated** cost declines for solar, wind, and batteries.

**Key learning rates (with uncertainty):**

| Technology | Learning rate | Std error on exponent | Noise (sigma) |
|---|---|---|---|
| Solar PV | 19.8% | 0.043 | 0.111 |
| Batteries | 25.3% | 0.063 | 0.103 |
| Wind | 12.6% | 0.041 | 0.065 |
| Electrolyzers | 8.6% | 0.067 | 0.201 |
| Nuclear | 0% | 0.010 | 0.020 |

**Two sources of uncertainty:**
1. **Parameter uncertainty** — true learning rate unknown, estimated from limited data
2. **Intrinsic noise** — stochastic shocks (supply disruptions, policy changes)

Forecast error scales as tau + tau²/m. For 30-year horizons, **parameter estimation error dominates** — the dominant uncertainty is structural, not noise.

**System-level implications:** Fast transition has expected net present savings of $5-15T vs no transition. ~80% probability fast transition is cheaper. But 95% CIs span several trillion $/year by 2050.

**Why it matters:** Strongest single citation for Gap 2 (treating costs as deep uncertainty). Not just argumentative — provides **quantifiable distributions** for parameterizing cost uncertainty. Expert forecasts are systematically biased; using fixed cost inputs is indefensible for policy analysis.

---

### IRENA (2026) — "Renewable Energy and Jobs: Annual Review 2025"

**What it is:** The conventional reference point for global RE employment figures.

**Headline:** 18.2 million RE jobs globally in 2024 (up from 16.2M in 2023, ~3x the 7.3M in 2012). Solar PV: 9.0M (half of total). China: 7.4M (41% of global). Brazil: 1.56M. EU: 1.8M.

**Coverage of your 7 countries:**
- Egypt: mentioned as emerging solar PV manufacturing hub
- Morocco: brief regional mention
- Mexico: noted within LAC, not broken out
- Uganda: passing mention in East Africa off-grid context
- **Belize, Libya, Bulgaria: absent entirely**

**Uncertainty handling:** Point estimates only. No confidence intervals, no ranges, no sensitivity analysis. China's solar figure was revised downward by 20%+ between editions.

**Why it matters:** The "headline numbers" your uncertainty analysis interrogates. 18.2M presented with no error bars, methodology opaque for developing countries, 4 of your 7 countries absent. Motivates your uncertainty-quantification approach.

---

### Lempert (2025) — "Supporting Climate-Related Decisions Under Uncertainty" — Chapter 4 in *Uncertainty in Climate Change Research*, Springer

**What it is:** Updated methodological authority on RDM/DMDU from the field's founder.

**Key framing:** Distinguishes "agree-on-assumptions" (traditional) vs "agree-on-decisions" (DMDU). Climate decisions are prototypical deep uncertainty problems — irreducible disagreement, long horizons, nonlinearities, multiple interacting uncertainties.

**Refined 4-step RDM framework:**
1. Frame decision (XLRM matrix: uncertainties X, levers L, relationships R, metrics M)
2. Evaluate strategies across many futures
3. Identify vulnerabilities via scenario discovery (PRIM, classification trees)
4. Suggest hedging actions and tradeoffs

**New developments since Lempert (2002) and Bryant & Lempert (2010):**
- MORDM (Many-Objective Robust Decision Making) — combines multiobjective optimization with exploratory analysis
- Adaptive policy pathways with signposts/triggers
- RDM institutionalized in water planning, climate finance, urban resilience
- "RDM-lite" for lighter-weight applications

**Employment/just transition:** Not discussed directly. But Jafino et al. (2021) on distributive justice within DMDU is referenced, signaling the framework can accommodate distributional/employment questions.

**Why it matters:** Authoritative, up-to-date citation for Section 2.3. Positions RDM as domain-agnostic and mature. Your extension to employment metrics is a natural application of the framework.

---

### NEW: Buchheim, Watzinger & Wilhelm (2020) — "Job creation in tight and slack labor markets" — *Journal of Monetary Economics* 114, 126-143

**What it is:** Causal evidence that employment multipliers are state-dependent, using German PV solar expansion as a natural experiment.

**Method:** Exploits exogenous variation in solar radiation across German counties interacting with national feed-in tariff. Instruments PV capacity with solar radiation. Splits sample by county unemployment rate vs state average.

**Key finding:** Employment multipliers are **strongly state-dependent**:
- **Slack labor markets:** 1.8-2.4 additional jobs per PV installation job (genuine net creation)
- **Tight labor markets:** Effect statistically indistinguishable from zero (crowding out)
- Mechanism: in tight markets, workers are drawn from other construction jobs → net creation is minimal, wages rise instead. In slack markets, workers drawn from unemployment → genuine gains.

**Why it matters:** Clean causal evidence that the employment bang-for-buck of green investment depends on labor market conditions. For your 7 countries (several with high un/underemployment), this supports the expectation that employment effects will be heterogeneous and conditional — exactly what scenario discovery explores. Could inform a parameter on labor market tightness in your experimental design.

---

## CROSS-CUTTING THEMES

### The landscape of approaches
| Approach | Example papers | What it captures | What it misses |
|---|---|---|---|
| **I-O (static)** | Garrett-Peltier, Cerny, Saget, your paper | Sectoral detail, supply chains, decomposability | No price feedbacks, fixed coefficients |
| **CGE** | Montt (via MRIO), Hafstead & Williams | Price adjustments, general equilibrium | Assumes full employment or specific labor market structure |
| **Macro-econometric** | Mercure (E3ME) | Dynamic feedbacks, learning curves, unemployment | Opaque, limited sectoral granularity |
| **Hybrid I-O + occupational** | Bucker et al. | Occupational detail, friction networks | Still fixed cost structures |
| **Your paper: I-O + RDM** | — | Systematic uncertainty exploration, conditional findings | No equilibrium feedbacks |

### The three gaps — confirmed across the literature

**Gap 1: No transformation-level traceability.** Hanna (2024), Cerny (2022), Saget (2020), IRENA (2026) all work at sector or technology level, not specific mitigation actions at specific intensities.

**Gap 2: Cost structures treated as fixed.** Explicitly acknowledged by Bucker et al., Cerny et al., Hanna et al. Way et al. (2022) provides the definitive evidence that cost trajectories are deeply uncertain. Perrier & Quirion (2018) shows exactly which structural parameters matter (labor share, wages, imports) and how sensitive results are.

**Gap 3: No conditional findings.** All existing studies produce point estimates or at best one-at-a-time sensitivity. No paper applies scenario discovery / exploratory modeling to employment effects. Mealy et al. and Knudsen et al. explicitly call for conditional analysis. Buchheim et al. provides causal evidence that employment effects are conditional on labor market state.

---
*Generated: 2026-04-16 | Based on PDFs in Readings/Tier 1, Tier 2, Tier 3 folders*
