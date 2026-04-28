# MINDSET Capability Assessment for Bolivia: ENSO/Climate Shocks and Energy Shocks

## Context

A research team has asked whether MINDSET can provide inputs, outputs, or analytical support for two climate-related analysis needs for **Bolivia**:

- **Task #1 (Priority):** ENSO effects — droughts, floods, macroeconomic and distributional impacts
- **Task #2 (Secondary):** Declining hydrocarbon reserves (gas) + hydropower uncertainty — energy shocks, macro-crises, low-carbon pathway investment

This document is a documentation-grounded assessment. Every substantive claim is tied to a specific MINDSET source file.

---

## A. Executive Summary

### Can MINDSET support Task #1 (ENSO / droughts / floods) for Bolivia?

**Yes, with meaningful caveats.** Confidence level: **MODERATE-HIGH.**

MINDSET has explicit, documented support for modeling the economic impacts of climate-induced natural disasters (floods, droughts) through its **supply constraint** and **capital damages** modules. The documentation directly cites "floods, droughts or wildfires" as motivating use cases (`Documentation/Capital damages.md`, line 1). The model can capture:
- Sectoral output losses from capital destruction (supply constraints)
- Supply chain propagation effects (forward/backward linkages via Ghosh and Leontief inverses)
- Macroeconomic effects (GDP, output, employment by sector and country)
- Distributional effects through household income/price channels (differentiated by income group: low/middle/high)
- Employment impacts by sector, skill level (low/high), and gender (female/male)

**However**, MINDSET does not model the physical hazard itself — it requires **externally estimated damage inputs** (e.g., what percentage of capital is destroyed in which sectors). The user must translate ENSO flood/drought scenarios into sector-level supply constraints or capital damage fractions. Additionally, **Bolivia is represented in the GLORIA MRIO database** (1 of 164 countries) and has been set up as a standalone region in the SSP aggregation, with country-specific employment coefficients, labor data, and household parameters.

### Can MINDSET support Task #2 (energy shocks / gas + hydropower) for Bolivia?

**Partially.** Confidence level: **MODERATE-LOW.**

MINDSET has energy sector modeling capabilities — interfuel substitution elasticities, energy cross-price and own-price elasticities, carbon tax incidence — and can model **price shocks** and **supply constraints** on energy sectors. It could model a gas supply shock (reduced output in GLORIA sector 27: "Extraction of natural gas and services") and partial hydropower disruption (within sector 63: "Production and distribution of electricity"). However:
- MINDSET does **not** model resource depletion dynamics or reserve trajectories
- It does **not** endogenously model energy investment pathway optimization
- It does **not** have hydropower-specific generation capacity modeling
- Long-run low-carbon development pathway analysis requires a dedicated energy system model (e.g., TIMES, OSeMOSYS), which MINDSET is not

MINDSET could provide **complementary macro/employment analysis** once energy shock magnitudes are externally determined, but it cannot be the primary tool for Task #2.

---

## B. Task #1 Detailed Assessment: ENSO / Drought / Flood / Macro / Distributional Analysis

### B.1 Does MINDSET explicitly support climate shock scenarios?

**Yes.** The documentation explicitly and extensively addresses this.

**Source: `Documentation/Capital damages.md` (lines 1-2):**
> "Capital damages are generally due to climate change induced extreme weather impacts, such as **floods, droughts or wildfires** that directly destruct capital assets."

This document references the IPCC AR6 WGI report on increased frequency of extreme events, and develops a theoretical framework for translating capital destruction into economic output losses, citing Hallegatte (2008, 2012, 2014a, 2014b, 2019, 2024).

**Source: `Documentation/Supply constraint.md` (lines 1-2):**
> "A supply constraint in the MRIO system can be modeled through a Ghoshian-shock..."

This 320-line document details the full supply constraint modeling framework, including criticality of inputs (Pichler et al. 2022), demand rationing (Hallegatte 2008 ARIO framework), import substitution, and input substitution — all directly applicable to disaster scenarios.

### B.2 What types of shock inputs can MINDSET accept?

The scenario module accepts the following inputs relevant to ENSO analysis:

**Source: `Documentation/MINDSET modules/Scenario module.md` (lines 21-28):**
A policy scenario can include:
1. **Supply constraints** — directly applicable to droughts/floods reducing production capacity
2. **Final demand shocks** — applicable to reduced household/government consumption post-disaster
3. **Investment shocks** — applicable to reconstruction spending
4. **Price changes** — applicable to price spikes from scarcity
5. **Input-output coefficient changes** — applicable to altered supply chain patterns post-disaster

**Source: `SourceCode/scenario.py` (verified by exploration agent):**
The scenario Excel template contains sheets for each of these: "Supply constraint", "Final demand", "Investment by", "Price change", "Input-output coefficients".

### B.3 How would flood/drought shocks be operationalized?

**Step 1: Capital damage → Output loss**

**Source: `Documentation/Capital damages.md` (lines 24-43):**
Following Hallegatte (2014a), output loss from capital destruction is:

$$\Delta Y(t_0) = \frac{1}{\mu} r \Delta K$$

where μ is the capital elasticity parameter, r is the interest rate + depreciation, and ΔK is capital destroyed. With classical values for μ, output reduction is approximately **3 times larger** than market value of damaged assets.

The document also notes (line 50): "Nevertheless, in the exercises Hallegatte (2008) takes a simplified asset loss to output loss relation, basically assuming that productive assets to output loss relation is 1:1."

**Step 2: Output loss → Supply constraint in MINDSET**

**Source: `Documentation/Capital damages.md` (lines 68-69):**
> "Expected output losses are need to be translated into supply constraints in the model. How supply constraints are treated then is described in [[Supply constraint]]."

**Source: `Documentation/Supply constraint.md` (lines 291-302):**
> "The current implementation is mostly based on the process described in Hallegatte (2008) and Pollitt (forthcoming), while also encompasses the criticality aspect described in Pichler et al. (2022)..."

The current code implementation uses Ghoshian-type shocks with a criticality-adjusted B matrix. The "Supply constraint" sheet in scenario files specifies constraints by country ISO code and product/sector.

**Step 3: Supply chain propagation**

The Ghosh inverse (G = (I-B)^{-1}) propagates supply constraints forward through the economy. The Leontief inverse (L = (I-A)^{-1}) captures backward demand-driven effects.

**Source: `SourceCode/InputOutput_SSP.py` (lines 113-131, 133-175):**
Both `load_L_base()` (Leontief) and `load_G_base()` (Ghosh) are implemented. The Ghosh inverse specifically incorporates criticality ratings from `heatmap_pichler_2022_modif.xlsx`.

### B.4 What macroeconomic outputs does MINDSET produce?

**Source: `README.md` (lines 293-316) and source code `SourceCode/results.py` (verified by exploration agent):**

The full results workbook includes 8 sheets:

| Sheet | Contents | Relevance to Task #1 |
|-------|----------|---------------------|
| **output** | Sectoral output changes (dq) by 12 channels | Direct: shows which sectors contract from supply constraint |
| **employment** | Employment changes (dempl) by 12 channels | Direct: job losses by sector, skill, gender |
| **gdp** | GDP changes (dgdp) by channel and region | Direct: macro impact summary |
| **demand** | Final demand changes by type | Shows household/government consumption changes |
| **household** | Household consumption by price and income effect | Distributional: how households are affected |
| **price** | Commodity price changes | Shows inflation/scarcity effects |
| **revenue** | Tax revenue changes | Fiscal impact |
| **emissions** | Emission changes by sector | Environmental co-benefits/costs |

Each output is decomposed by **12 impact channels** (`Documentation/MINDSET modules/Impact channels/Impact channels.md`):
1. tech_eff (technology substitution)
2. trade_eff (trade substitution)
3. hh_price (household price effects)
4. hh_inc (household income effects)
5. gov_recyc (government recycling)
6. inv_recyc (investment recycling)
7. inv_exog (exogenous investment — e.g., reconstruction)
8. hh_exog_fd (exogenous household demand)
9. fcf_exog_fd (exogenous capital formation)
10. gov_exog_fd (exogenous government demand)
11. supply_constraint
12. inv_induced (induced investment)

### B.5 Time horizon

**Source: `Documentation/Dynamic solution.md` (full file):**

MINDSET has both a **static (comparative static)** mode and a **dynamic (year-to-year)** mode:

- **Static mode** (`RunMINDSET.py`): Computes the impact of a shock within a single period, with an iterative convergence loop for household income and tax revenue feedback. This is the primary mode and best suited for **short-run** impact assessment.

- **Dynamic mode** (`RunMINDSET_yearly.py`, `MINDSET.py`): Prototype year-to-year model with equations for household consumption (lagged income/wages), investment (capacity utilization, capital stock), employment (probit model), wages, and potential output. Capital stock depreciates at 10% per year. This extends the model to **medium-run** (5-10 year) horizons.

**Source: `Documentation/Capital damages.md` (line 47), quoting Hallegatte (2008):**
> "market-clearing hypothesis is valid only over longer timescales than the few months we want to consider here"

This confirms the IO approach is designed for **short-to-medium-term** analysis, which aligns with ENSO impact assessment needs.

### B.6 Distributional dimensions

**Source: `Documentation/MINDSET modules/Impact channels/Household income and price.md` (full file):**

Household impacts are differentiated by:
- **Income group**: Low-income, Middle-income, High-income (via USDA classification)
  - Cross-price elasticities differ by income group: `HH_CP_ELAS_LOW`, `HH_CP_ELAS_MID`, `HH_CP_ELAS_HIGH`
  - Source files: `GLORIA_template/Elasticities/USDA_cpe_low.xlsx`, `USDA_cpe_mid.xlsx`, `USDA_cpe_high.xlsx`
- **Consumption sector**: 9 categories (Food/beverages/tobacco, Clothing/footwear, Housing, House furnishing, Medical/health, Transport/communication, Recreation, Education, Other)
  - Source: `GLORIA_template/modelinputdata/Sectors_USDAtoGLORIA.xlsx`

**Source: `README.md` (lines 247-272) — Employment module:**

Employment impacts are disaggregated by:
- **Skill level**: Low-skill, High-skill
- **Gender**: Female, Male
- **Sector**: 120 GLORIA sectors
- Source: `LABOR_BASE` contains `vol_Fem_low`, `vol_Male_low`, `vol_Fem_high`, `vol_Male_high`, and corresponding wages

**Important caveat on distributional depth**: The income group differentiation applies to **household consumption elasticities** (how demand responds to price/income changes). It does **not** represent distinct household agents with separate budget constraints or income distributions within a country. This is an elasticity-based approximation, not a microsimulation. The documentation states (`Documentation/MINDSET modules/Impact channels/Household income and price.md`, line 13):
> "Due to these sources having lower sector / product resolution, the actual elasticity impact calculations are done with an aggregated sectoral structure (rather than the 120 sector structure). *This is expected to be changed.*"

### B.7 Bolivia-specific representation

**Bolivia (BOL) is directly represented** in the MINDSET data infrastructure:

1. **GLORIA MRIO database**: BOL is 1 of 164 countries in `GLORIA_db/v57/2019/parsed_db_original/` (confirmed by exploration agent reading `cid.pkl`)
2. **SSP aggregation**: BOL has been set up as the 9th standalone region in `R_grouping_SSP.xlsx` (confirmed during debugging session — `GLORIA_template/Country_groupings/R_grouping_SSP.xlsx`, aggregates sheet, Lfd_Nr_agg=9)
3. **Employment coefficients**: Bolivia has country-specific employment-to-output ratios in `GLORIA_template/Employment/Empl_coefficient.csv` (column header uses full country name "Bolivia")
4. **Household income classification**: Bolivia is classified as "Middle-income" in `GLORIA_template/Elasticities/Countries_inc_cat.xlsx` (verified by exploration agent — aggregates sheet of R_grouping_SSP.xlsx)
5. **USDA country mapping**: Bolivia is mapped with Employment_country="Bolivia", Investment_country="Bolivia" in `GLORIA_template/modelinputdata/Countries_USDAtoGLORIA.xlsx`
6. **Energy elasticities**: BOL uses `EnergyElas_ROW.xlsx` (Rest of World) cross-price and `OwnPrices.xlsx` (BOL-specific) own-price elasticities (from R_grouping_SSP.xlsx aggregates sheet)
7. **Scenario files**: 67 Bolivia-specific scenario files exist (`Strategy_*_BOL.xlsx`) in the Scenarios folder (confirmed during debugging)

---

## C. Task #2 Detailed Assessment: Energy Shocks (Gas + Hydropower)

### C.1 Energy sectors in MINDSET

**Source: `Documentation/MINDSET modules/Impact channels/Technology substitution.md` (line 4):**
> "the substitution is limited to substitution across energy types (fuels) (these are GLORIA sectors 24,25,26,27,62,63,93,94)"

The relevant GLORIA sectors for Bolivia's energy analysis:
- **Sector 24**: Mining of hard coal
- **Sector 25**: Mining of lignite and peat
- **Sector 26**: Extraction of crude petroleum
- **Sector 27**: Extraction of natural gas and services related to gas extraction
- **Sector 62**: Manufacture of gas; distribution of gaseous fuels through mains
- **Sector 63**: Production and distribution of electricity
- **Sectors 93-96**: Additional energy/utility sectors

Sector 27 (gas extraction) and sector 63 (electricity) are directly relevant to Bolivia's dual energy shock.

### C.2 What MINDSET can do for energy shocks

**a) Gas supply shock:**
A decline in gas reserves could be modeled as a **supply constraint** on sector 27 (gas extraction) for Bolivia. This would propagate through:
- Forward linkages (Ghosh inverse): sectors that use gas as an input see reduced availability
- Backward linkages (Leontief inverse): reduced demand for gas sector inputs
- Price effects: via `Price change` sheet in scenario template
- Household effects: via energy price transmission to consumer prices

**Source: `Documentation/Supply constraint.md` (lines 67-68, "Essential final demand" table):**
Energy sectors (24-27, 63, 93-96) are classified as essential, meaning household/government consumption is prioritized during rationing.

**b) Hydropower uncertainty:**
A reduction in hydropower could be modeled as a **supply constraint** on sector 63 (electricity production) or as a **price change** (electricity becomes more expensive). However, MINDSET does not distinguish between electricity generation technologies — sector 63 aggregates all electricity production (hydro, thermal, solar, wind, nuclear) into a single sector.

**c) Interfuel substitution:**
The energy elasticity module (`SourceCode/ener_elas.py`) calculates substitution between energy types based on cross-price elasticities. If gas prices rise, the model can estimate shifts toward other fuels.

**Source: `Documentation/MINDSET modules/Impact channels/Technology substitution.md` (lines 8-18):**
Own-price effect: $\Delta\beta_{i,o} = (1 + \Delta p_i)^{-\eta_{i,o}}$
Cross-price effect: $\Delta\beta_{i,c} = \frac{\sum_{k \neq i}(1 + \Delta p_k)^{\eta_{i,k}}}{n-1}$

### C.3 What MINDSET cannot do for energy shocks

1. **Resource depletion modeling**: MINDSET is a static/comparative-static IO model. It does not model reserve depletion curves, extraction costs as a function of remaining reserves, or resource exhaustion dynamics. These require geological/resource economics models.

2. **Energy system optimization**: MINDSET does not optimize energy investment pathways, generation capacity mix, or least-cost electricity system expansion. Tools like TIMES, OSeMOSYS, or MESSAGE are designed for this.

3. **Hydropower-specific variability**: MINDSET cannot model hydrological variability, reservoir storage dynamics, or climate impacts on water availability for power generation. Sector 63 is a single aggregate.

4. **Long-run low-carbon pathway feasibility**: The dynamic module (`Documentation/Dynamic solution.md`) extends to medium-run, but does not include technological learning curves, renewable energy cost declines, or long-run structural transformation.

5. **Dual shock interaction**: While MINDSET can model simultaneous supply constraints on sectors 27 and 63, the interaction is through IO linkages only — it does not capture the specific compounding dynamics of losing both gas and hydropower simultaneously as energy system substitutes.

### C.4 Where MINDSET adds value for Task #2

Despite limitations, MINDSET could contribute:
- **Macroeconomic impact assessment**: Given externally determined shock magnitudes (e.g., "gas output declines 30%, electricity output declines 15%"), MINDSET can estimate GDP, employment, and sectoral output effects
- **Employment and distributional effects**: Who loses jobs, in which sectors, at what skill levels
- **Supply chain propagation**: Which non-energy sectors are most affected through input-output linkages
- **Household welfare**: How energy price increases affect different income groups differently

---

## D. Data Sources and Model Foundations

### D.1 Core database

| Data | Source | File | Base Year |
|------|--------|------|-----------|
| MRIO tables | GLORIA v57 | `GLORIA_db/v57/2019/parsed_db_original/IND_sparse.pkl` | 2019 |
| Household demand | GLORIA v57 | `HH.pkl`, `GOV.pkl`, `FCF.pkl`, `NPISH.pkl`, `INV.pkl` | 2019 |
| Value added | GLORIA v57 | `VA.pkl` | 2019 |
| Employment | GLORIA v57 | `empl_data.pkl`, `labor_data.pkl` | 2019 |
| Country/sector lists | GLORIA v57 | `cid.pkl`, `cou.pkl`, `sid.pkl`, `sec.pkl` | 2019 |

**Source: `README.md` (lines 336-356)**

**GLORIA v60 also available** (latest version): `GLORIA_db/v60/` contains zipped data with release notes (`GLORIA_ReadMe_060.xlsx`, `GLORIA_ReleaseNotes_060.pdf`), but the current working version uses v57/2019.

### D.2 Elasticity parameters

| Parameter | Source | File |
|-----------|--------|------|
| Energy own-price elasticities | Country-specific | `GLORIA_template/Elasticities/OwnPrices.xlsx` |
| Energy cross-price elasticities | Regional (ROA/ROE/ROW) + country-specific | `EnergyElas_*.xlsx` |
| Household income elasticities | USDA | `USDA_Table1.xlsx` |
| Household own-price elasticities | USDA | `USDA_Table2.xlsx` |
| Household cross-price elasticities | USDA, by income group | `USDA_cpe_low/mid/high.xlsx` |
| Trade elasticities | Default | `TradeElas_default.xlsx` |
| Investment-output elasticities | Country-specific | `Investment/Inv_output.csv` |
| Employment coefficients | Country-specific | `Employment/Empl_coefficient.csv` |

**Source: `README.md` (lines 362-400)**

### D.3 Scenario inputs required

To run a disaster scenario for Bolivia, the user needs to create a scenario Excel workbook with these sheets (all optional — include only what applies):

| Sheet | Purpose | Required for Task #1? |
|-------|---------|----------------------|
| Supply constraint | Sector-level output reduction (% or absolute) | **Yes** — primary shock input |
| Final demand | Changes to household/govt/investment demand | Useful — demand reduction from disaster |
| Investment by | Reconstruction/recovery investment by sector | Useful — reconstruction spending |
| Price change | Non-tax price shocks | Optional — scarcity-driven price spikes |
| Input-output coefficients | Changes to production recipes | Optional — supply chain disruption |
| Carbon tax | Tax rates by fuel/sector | Not needed for Task #1 |
| CBAM | Border adjustment | Not needed for Task #1 |
| Investment converter | Adjust investment composition | Optional |

**Source: `Documentation/MINDSET modules/Scenario module.md` (lines 21-28)**

### D.4 Model outputs

Full results are saved to `FullResults_[scenario].xlsx` with 8 sheets as detailed in Section B.4 above.

**Source: `README.md` (lines 318-327)**

---

## E. Distributional and Sectoral Capabilities

### E.1 Sectoral detail

**120 GLORIA sectors** covering:
- Agriculture (sectors 1-23): 23 agricultural subsectors including specific crops and livestock
- Mining/extraction (24-29): Including coal, lignite, petroleum, gas, ores
- Manufacturing (30-107): Detailed manufacturing subsectors
- Energy/utilities (within 62-63, 93-96)
- Services (107-120): Construction, transport, finance, education, health, government

**Source: `GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx`, P sheet (120 rows)**

### E.2 Distributional disaggregation

**Employment:**
- 2 skill levels x 2 genders = 4 labor categories per sector per country
- Variables: `vol_Fem_low`, `vol_Male_low`, `vol_Fem_high`, `vol_Male_high` (volumes) and corresponding wages
- **Source: `README.md` (line 28): "LABOR_BASE: Employment and wage"**; `SourceCode/exog_vars.py` (exploration agent confirmed column structure)

**Household consumption:**
- 3 income groups (Low/Middle/High) with differentiated elasticities
- 9 consumption categories mapped to GLORIA sectors
- **Source: `Documentation/MINDSET modules/Impact channels/Household income and price.md` (lines 6-12)**

**Important limitation**: The model does **not** have distinct household agents or microsimulation. Distributional effects are approximated through:
1. Different elasticities by income group (how much consumption changes for price/income shifts)
2. Employment effects by skill level and gender (who gains/loses jobs)
3. Sectoral employment composition (which sectors are affected)

For Bolivia specifically: classified as **Middle-income**, meaning `USDA_cpe_mid.xlsx` cross-price elasticities apply.

### E.3 What distributional analysis is feasible for Bolivia?

Given a flood/drought shock, MINDSET can estimate for Bolivia:
- Which of the 120 sectors experience output/employment losses
- How many low-skill vs. high-skill, female vs. male jobs are affected
- How commodity prices change for different consumption categories
- How household consumption changes for a middle-income country profile
- GDP impact by channel (supply constraint, household demand, investment, etc.)

What it **cannot** estimate:
- Income distribution changes within Bolivia (Gini, poverty headcount, etc.)
- Subnational impacts (e.g., flood-prone vs. highland regions)
- Informal sector impacts (GLORIA is based on formal national accounts)
- Indigenous/rural population-specific effects

---

## F. Limitations / Gaps / Caveats

### F.1 General model limitations

1. **No physical hazard modeling**: MINDSET does not model climate/weather itself. Flood/drought magnitudes and spatial footprints must be externally determined.

2. **National aggregation only**: No subnational resolution. Cannot differentiate between flood-prone lowlands and highland regions of Bolivia. Source: `Documentation/Supply constraint.md` (line 34): "Unfortunately, for clustering to be represented we would need to go below the national level in spatial terms."

3. **Fixed coefficients**: The IO structure (A matrix) is fixed at base year (2019). Source: `Documentation/Supply constraint.md` (line 180): discusses the "joint stability problem" where both A and B matrices are calculated on base data and not recalculated.

4. **No inventories**: Source: `Documentation/Supply constraint.md` (lines 154-157): "we do not represent inventories in MINDSET."

5. **No firm heterogeneity**: All firms within a sector-country pair are treated identically. Source: `Documentation/Supply constraint.md` (lines 22-33).

6. **Not a CGE**: Prices do not clear markets. This is intentional for short-run disaster analysis but limits long-run applicability. Source: `Documentation/Capital damages.md` (line 47), quoting Hallegatte: "market-clearing hypothesis is valid only over longer timescales."

7. **Dynamic module is prototype**: The year-to-year module (`RunMINDSET_yearly.py`) is described in `README.md` line 8 as a "prototype" and `Documentation/Dynamic solution.md` has incomplete variable source tables (many blank entries).

### F.2 Bolivia-specific limitations

1. **Energy elasticities**: Bolivia uses "Rest of World" cross-price energy elasticities (`EnergyElas_ROW.xlsx`), not Bolivia-specific estimates. Own-price elasticities use BOL-specific values from `OwnPrices.xlsx`.

2. **Household elasticities**: Classified as middle-income, using USDA data originally for "Bolivia" — but the underlying USDA data quality for Bolivia specifically has not been independently verified in the MINDSET documentation.

3. **Employment coefficients**: Country-specific for Bolivia in `Empl_coefficient.csv`, but these are derived from GLORIA base data (2019) and may not capture recent structural changes.

4. **No informal economy**: Bolivia has a large informal sector that is not captured in MRIO-based analysis.

5. **Agricultural detail**: While 23 agricultural subsectors exist, the mapping of ENSO-specific crop vulnerability (which crops are drought-sensitive, which are flood-sensitive) must be done externally.

### F.3 Gaps relative to the research team's needs

| Need | MINDSET capability | Gap |
|------|-------------------|-----|
| ENSO physical hazard characterization | None — requires external climate/hydrology model | Full gap |
| Sector-level damage estimates | None — requires external damage assessment | Full gap |
| Macroeconomic impact propagation | **Full support** | None |
| Employment impacts by sector/skill/gender | **Full support** | None |
| Household distributional effects | Partial — elasticity-based, 3 income groups | No within-country inequality, no poverty line |
| Subnational spatial impacts | None | Full gap |
| Short/medium-term time horizon | **Supported** (static + prototype dynamic) | Dynamic module is prototype |
| Gas reserve depletion dynamics | None | Full gap — needs resource economics model |
| Hydropower variability | None | Full gap — needs energy/hydrology model |
| Energy system optimization | None | Full gap — needs TIMES/OSeMOSYS |
| Low-carbon pathway investment | Very limited — exogenous investment only | Mostly gap |

---

## G. Source Reference Log

### Documentation files (read in full)

| # | File | Key content |
|---|------|-------------|
| 1 | `Documentation/Capital damages.md` | Climate disaster economic framework; floods/droughts explicitly cited; Hallegatte methodology |
| 2 | `Documentation/Climate damages.md` | One-line pointer to Capital damages |
| 3 | `Documentation/Supply constraint.md` | 320-line detailed supply constraint framework; Ghosh inverse; criticality; ARIO; Pichler/Hallegatte/Pollitt |
| 4 | `Documentation/Dynamic solution.md` | Year-to-year equations: consumption, investment, employment, wages, capital, potential output |
| 5 | `Documentation/Documentation.md` | Documentation workflow (Obsidian/Github) |
| 6 | `Documentation/MINDSET modules/Impact channels/Impact channels.md` | 12 impact channels overview |
| 7 | `Documentation/MINDSET modules/Impact channels/Household income and price.md` | Income/price elasticity methodology; distributional approach |
| 8 | `Documentation/MINDSET modules/Impact channels/Exogenous impacts.md` | Exogenous investment and final demand channels |
| 9 | `Documentation/MINDSET modules/Impact channels/Technology substitution.md` | Energy interfuel substitution; elasticity formulas; relevant sectors |
| 10 | `Documentation/MINDSET modules/Scenario module.md` | Scenario types; flow diagrams; parameter descriptions |
| 11 | `Documentation/MINDSET modules/Exogenous inputs module.md` | Data loading and variable descriptions |
| 12 | `README.md` | Full module documentation; inputs/outputs for every source file |

### Source code files (read/explored)

| # | File | Key content verified |
|---|------|---------------------|
| 13 | `SourceCode/scenario.py` | Shock types: supply constraint, final demand, investment, price change, IO coefficients |
| 14 | `SourceCode/employment.py` | Employment coefficients; skill/gender disaggregation |
| 15 | `SourceCode/exog_vars.py` | Full data loading; all variable structures |
| 16 | `SourceCode/exog_vars_SSP.py` | SSP aggregation variant |
| 17 | `SourceCode/InputOutput_SSP.py` | Leontief and Ghosh inverse; supply constraint channel |
| 18 | `SourceCode/investment.py` | Investment converter; induced/recycled/exogenous investment |
| 19 | `SourceCode/results.py` | 8-sheet output workbook structure |
| 20 | `RunMINDSET.py` | Full model pipeline (referenced but not read line-by-line in this session) |

### Data/template files (verified existence and structure)

| # | File | Key content verified |
|---|------|---------------------|
| 21 | `GLORIA_template/Country_groupings/R_grouping_SSP.xlsx` | Bolivia = region 9; middle-income; elasticity mappings |
| 22 | `GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx` | R sheet (9 regions incl BOL); P sheet (120 sectors) |
| 23 | `GLORIA_template/Employment/Empl_coefficient.csv` | Bolivia employment coefficients exist |
| 24 | `GLORIA_template/Scenarios/Strategy_*_BOL.xlsx` | 67 Bolivia scenario files exist |
| 25 | `GLORIA_db/v57/2019/parsed_db_original/cid.pkl` | BOL is 1 of 164 countries |
| 26 | `GLORIA_db/v57/2019/SSP/labor_data.pkl` | BOL labor data with skill/gender breakdown |
| 27 | `GLORIA_template/Supply_constraints/heatmap_pichler_2022_modif.xlsx` | Criticality ratings matrix |
| 28 | `GLORIA_template/Supply_constraints/full_gloria_criticality.csv` | Full sector criticality scores |

### Academic references cited in MINDSET documentation

- Hallegatte (2008) — ARIO model, Katrina economic cost
- Hallegatte (2012) — Heterogeneity, substitution, inventories in disaster cost
- Hallegatte (2014a) — Economic resilience definition
- Hallegatte (2014b) — Inventories and heterogeneity
- Hallegatte & Vogt-Schilb (2019) — Are losses more than asset losses?
- Hallegatte, Jooste & McIsaac (2024) — Macro consequences of natural disasters
- Pichler et al. (2022) — Pandemic shock propagation, criticality, PBL production function
- Henriet, Hallegatte & Tabourier (2012) — Firm-network robustness
- Diem et al. (2022) — Firm-level systemic risk
- Miller & Blair (2009) — IO Analysis foundations
- Pollitt (forthcoming) — Input substitution and efficiency
- IPCC AR6 WGI (2021) — Extreme event frequency
