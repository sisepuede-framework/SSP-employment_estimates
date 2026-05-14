# MINDSET Employment Impact Model - Detailed Technical Documentation

## Project Goal
Estimate **employment impacts** of infrastructure investments using the **MINDSET framework** and **Multi‑Regional Input–Output (MRIO)** analysis across 7 countries and 67 investment strategies.

**Countries:** Bulgaria (BGR), Belize (BLZ), Egypt (EGY), Libya (LBY), Morocco (MAR), Mexico (MEX), Uganda (UGA)

**Investment Strategies:** 67 different sectoral investment portfolios per country

**Output:** Direct, Indirect, and Total employment impacts by region and by sector

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Understanding MINDSET Investment-to-Employment Flow](#understanding-mindset-investment-to-employment-flow)
3. [Script Documentation](#script-documentation)
4. [Step-by-Step Employment Calculation](#step-by-step-employment-calculation)
5. [Data Structures](#data-structures)
6. [Output Files](#output-files)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For Research Team Members

**To run the batch employment analysis:**

```bash
cd "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main/Claude Code/temp"

python RunMINDSET_EmploymentOnly_BATCH_FINAL.py
```

**Expected runtime:** ~2-4 hours for 469 scenarios (67 strategies × 7 countries)

**Expected outputs:**
- `GLORIA_results/ALL_RESULTS_Employment_by_Region.csv`
- `GLORIA_results/ALL_RESULTS_Employment_by_Sector.csv`
- `GLORIA_results/BATCH_SUMMARY.csv`

---

## Understanding MINDSET Investment-to-Employment Flow

### Overview

MINDSET uses Input-Output (IO) analysis to trace how sectoral investments ripple through the economy, creating both **direct employment** (in sectors producing investment goods) and **indirect employment** (in supply chain sectors).

### The Complete Chain

```
┌─────────────────────────────────────────────────────────────────┐
│                    INVESTMENT SCENARIO                          │
│  "Construction sector in Mexico invests $10 million"            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 1: Read Investment Scenario                  │
│                  (scenario.py: set_exog_inv)                    │
│                                                                 │
│  Input Sheet: "Investment by"                                  │
│  Columns:                                                       │
│    - Country ISO* (MEX)                                        │
│    - Sector investing code* (56 = Construction)               │
│    - Value* ($10,000,000)                                      │
│    - Type* (abs-b)                                             │
│                                                                 │
│  Output: Scenario.inv_exog DataFrame                           │
│    REG_imp | PROD_COMM | dk                                   │
│    MEX     | 56        | 10000000                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          STEP 2: Investment Converter Matrix                    │
│         (investment.py: calc_dy_inv_exog)                      │
│                                                                 │
│  Question: "When construction sector invests $10M,             │
│             what products are demanded?"                        │
│                                                                 │
│  Uses: INV_CONV matrix (120 × 120)                            │
│    REG_imp | PROD_COMM | TRAD_COMM | input_coeff             │
│    MEX     | 56        | 56        | 0.30  ← 30% construction │
│    MEX     | 56        | 45        | 0.20  ← 20% cement       │
│    MEX     | 56        | 68        | 0.15  ← 15% machinery    │
│    ...                                                          │
│                                                                 │
│  Calculation: dk × input_coeff                                 │
│    $10M × 0.30 = $3M for construction goods                   │
│    $10M × 0.20 = $2M for cement                               │
│    $10M × 0.15 = $1.5M for machinery                          │
│    ...                                                          │
│                                                                 │
│  Then: Disaggregate across producing countries                 │
│    (domestic + imports using FCF_share)                        │
│                                                                 │
│  Output: dy_inv_exog (Initial Final Demand)                    │
│    REG_imp | TRAD_COMM | dy                                   │
│    MEX     | 56        | 2400000  ← $2.4M (80% domestic)     │
│    USA     | 56        | 400000   ← $0.4M (imports from USA) │
│    MEX     | 45        | 1800000  ← $1.8M cement (domestic)  │
│    ...                                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│        STEP 3: Leontief Input-Output Model                     │
│          (InputOutput.py: calc_dq_exog)                        │
│                                                                 │
│  Question: "What is the TOTAL output needed across all         │
│             sectors to meet this final demand?"                 │
│                                                                 │
│  Formula: dq = L × dy                                          │
│    where:                                                       │
│      dy = Initial final demand (from Step 2)                  │
│      L = Leontief inverse = (I - A)^(-1)                      │
│      dq = Total output change (direct + indirect)              │
│                                                                 │
│  The Leontief inverse captures supply chain:                   │
│    - To produce $3M construction → need cement, steel, etc.   │
│    - To produce cement → need limestone, energy, etc.         │
│    - To produce steel → need iron ore, coal, etc.             │
│    ... and so on through the entire supply chain              │
│                                                                 │
│  Example Output:                                               │
│    Initial demand: $10M                                        │
│    Total output (with multiplier): $17M                       │
│    Supply chain effect: $7M additional                         │
│                                                                 │
│  Output: dq_total (vector, 19,680 elements)                   │
│    One value per (country, sector) pair                       │
│    162 countries × 120 sectors = 19,440 pairs                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 4: Employment Calculation                         │
│          (employment.py: calc_dempl)                           │
│                                                                 │
│  Question: "How many jobs are created by this output?"        │
│                                                                 │
│  Formula: dE = e × dq                                          │
│    where:                                                       │
│      e = Employment coefficient (jobs per $ output)           │
│      dq = Output change                                        │
│      dE = Employment change (jobs created)                     │
│                                                                 │
│  Calculated separately:                                        │
│                                                                 │
│  A. DIRECT EMPLOYMENT                                          │
│     Jobs from producing the initially demanded goods          │
│     dempl_direct = e × dy                                     │
│                                                                 │
│  B. TOTAL EMPLOYMENT                                           │
│     Jobs from producing all goods (including supply chain)    │
│     dempl_total = e × (L × dy) = e × dq                      │
│                                                                 │
│  C. INDIRECT EMPLOYMENT                                        │
│     Jobs in supply chain sectors                              │
│     dempl_indirect = dempl_total - dempl_direct               │
│                                                                 │
│  Example:                                                       │
│    Direct jobs: 120 (producing investment goods)              │
│    Indirect jobs: 80 (producing supply chain inputs)          │
│    Total jobs: 200                                             │
│    Employment multiplier: 200 jobs / $10M = 20 jobs/$1M       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Script Documentation

### Main Scripts in `Claude Code/temp/`

#### **1. RunMINDSET_EmploymentOnly_BATCH_FINAL.py** ⭐ PRIMARY SCRIPT

**Purpose:** Batch processing for 469 scenarios (67 strategies × 7 countries)

**What it does:**
1. Loads MRIO data once (efficient reuse)
2. For each scenario file:
   - Reads investment data from "Investment by" sheet
   - Applies investment converter
   - Runs Leontief IO model
   - Calculates employment (separating Direct, Indirect, Total)
   - Aggregates by region and by sector
3. Combines all results into 3 CSV files

**Input:**
- Scenario files: `GLORIA_template/Scenarios/Strategy_{strategy_id}_{Country}.xlsx`
- Each file has "Investment by" sheet with investment amounts per sector

**Output:**
- `ALL_RESULTS_Employment_by_Region.csv` - Jobs by geographic region
- `ALL_RESULTS_Employment_by_Sector.csv` - Jobs by economic sector
- `BATCH_SUMMARY.csv` - Summary statistics per scenario

**Runtime:** ~2-4 hours (depends on CPU)

**Key Functions:**
- `run_single_scenario()` - Processes one strategy-country combination
  - Lines 101-304: Complete employment calculation pipeline
  - Returns: Direct jobs, Indirect jobs, Total jobs, Employment multiplier

---

#### **2. RunMINDSET_EmploymentOnly.py**

**Purpose:** Single-scenario employment analysis (for testing)

**What it does:**
- Runs MINDSET employment module for ONE scenario
- Useful for testing and debugging
- Produces detailed Excel output

**Usage:**
```python
# Edit line 104:
scenario_name = "Strategy_1004_MEX"  # Change this

# Then run:
python RunMINDSET_EmploymentOnly.py
```

**Output:**
- `GLORIA_results/Results_{scenario_name}_EmploymentOnly.xlsx`
  - Sheet: Employment_by_Region
  - Sheet: Employment_by_Sector
  - Sheet: Summary

---

#### **3. test_direct_indirect_jobs.py**

**Purpose:** Testing script to verify Direct vs Indirect separation logic

**What it does:**
- Loads one scenario (Strategy_1004_MEX)
- Calculates employment with detailed diagnostics
- Shows breakdown of Direct vs Indirect by region and sector
- Validates that approach matches MINDSET methodology

**Usage:**
```bash
python test_direct_indirect_jobs.py
```

**Output:** Console output showing:
- Investment data structure
- Sectors with direct investment
- Direct jobs calculation
- Indirect jobs calculation
- Validation checks

---

### Supporting Scripts

#### **4. sector_to_product_allocation.Rmd**

**Purpose:** Creates crosswalk between strategies and product distributions

**Input:**
- Cost structure files: `cost_str_{Country}.xlsx` (7 files)
- GLORIA-Eora26 crosswalk

**Output:**
- `sector_to_product_distribution_allcountries.csv`
- Maps 67 strategies to 120 GLORIA products for each country

---

#### **5. MINDSET_INVESTMENT_FLOW_DOCUMENTATION.md**

**Purpose:** Technical documentation of MINDSET investment-to-employment process

**Contents:**
- Detailed explanation of each step
- Code references to original MINDSET source
- Examples with numbers
- Data structure specifications

---

## Step-by-Step Employment Calculation

### Detailed Technical Walkthrough

#### **Step 1: Load Investment Scenario**

**File:** `SourceCode/scenario.py`, method `set_exog_inv()` (lines 321-383)

**Process:**
```python
# Read "Investment by" sheet (skip first 14 header rows)
inv_exog = pd.read_excel(scenario_file, sheet_name='Investment by', skiprows=14)

# Expected columns:
# - Country ISO* (e.g., "MEX", "BGR")
# - Sector investing code* (1-120, GLORIA sector code)
# - Value* (investment amount in USD)
# - Type* ("abs-b" = absolute value, baseline proportional)

# After processing:
inv_exog = DataFrame with columns:
  - REG_imp: Country ISO code
  - PROD_COMM: Sector code (1-120) that is INVESTING
  - dk: Investment amount (USD)
```

**Example Data:**
```
REG_imp | PROD_COMM | dk
--------|-----------|----------
MEX     | 56        | 10000000   ← Construction invests $10M
MEX     | 78        | 5000000    ← Transport invests $5M
MEX     | 23        | 3000000    ← Agriculture invests $3M
```

**Important:** PROD_COMM here is the **investing sector**, not the products being purchased!

---

#### **Step 2: Apply Investment Converter**

**File:** `SourceCode/investment.py`, method `calc_dy_inv_exog()` (lines 217-253)

**Purpose:** Convert "Sector X invests $Y" into "Demand for products A, B, C..."

**Sub-Step 2.1: Load Investment Converter Matrix**

```python
# INV_CONV structure:
# REG_imp | PROD_COMM (investing) | TRAD_COMM (product) | input_coeff
# MEX     | 56                    | 56                  | 0.30
# MEX     | 56                    | 45                  | 0.20
# MEX     | 56                    | 68                  | 0.15
# ...

# For each investing sector, coefficients sum to 1.0:
# Construction (56) invests in:
#   - 30% construction goods (56)
#   - 20% cement (45)
#   - 15% machinery (68)
#   - 10% transport (78)
#   - ... (rest distributed among other products)
```

**Sub-Step 2.2: Merge and Multiply**

```python
# Merge investment amounts with converter
exog_inv = inv_exog.merge(INV_CONV, on=['PROD_COMM', 'REG_imp'])

# Calculate demand for each product
exog_inv['dk'] = exog_inv['dk'] * exog_inv['input_coeff']

# Example: Construction investing $10M
# Becomes:
#   $10M × 0.30 = $3M → construction goods (56)
#   $10M × 0.20 = $2M → cement (45)
#   $10M × 0.15 = $1.5M → machinery (68)
#   ...
```

**Sub-Step 2.3: Disaggregate Across Countries**

```python
# Use FCF_share to allocate across producing countries
# (domestic production + imports)

fcf_share structure:
# REG_exp (producing) | TRAD_COMM | REG_imp (consuming) | FCF_share
# MEX                 | 56        | MEX                 | 0.80  (80% domestic)
# USA                 | 56        | MEX                 | 0.13  (13% from USA)
# CHN                 | 56        | MEX                 | 0.07  (7% from China)

# Merge and allocate:
exog_inv = exog_inv.merge(fcf_share, on=['TRAD_COMM', 'REG_imp'])
exog_inv['dy'] = exog_inv['dk'] * exog_inv['FCF_share']

# Example: MEX demands $3M of construction goods (56)
# Becomes:
#   MEX produces: $3M × 0.80 = $2.4M
#   USA produces: $3M × 0.13 = $0.39M
#   CHN produces: $3M × 0.07 = $0.21M
```

**Sub-Step 2.4: Final Aggregation**

```python
# Group by producing country and product
dy_inv_exog = exog_inv.groupby(['REG_exp', 'TRAD_COMM']).agg({'dy': 'sum'})
dy_inv_exog = dy_inv_exog.rename(columns={'REG_exp': 'REG_imp'})

# Result: dy_inv_exog DataFrame
# REG_imp (producing) | TRAD_COMM (product) | dy (demand)
# MEX                 | 56                  | 2400000
# USA                 | 56                  | 390000
# CHN                 | 56                  | 210000
# MEX                 | 45                  | 1800000
# ...

# This is INITIAL FINAL DEMAND for products
```

---

#### **Step 3: Calculate Total Output (Leontief Model)**

**File:** `SourceCode/InputOutput.py`, method `calc_dq_exog()`

**Purpose:** Calculate total output needed (direct + supply chain)

**Formula:** `dq = L × dy`

Where:
- `dy` = Initial final demand (from Step 2)
- `L` = Leontief inverse matrix = (I - A)^(-1)
- `A` = Technical coefficients matrix (input per unit output)
- `dq` = Total output change

**The Leontief Inverse Explained:**

```
L = (I - A)^(-1)

Interpretation:
- I = Identity matrix (diagonal matrix of 1s)
- A = Direct input requirements
- (I - A)^(-1) = Total requirements (direct + indirect + indirect^2 + ...)

Example:
To produce $1 of construction:
- Direct inputs: $0.30 cement, $0.20 steel, $0.10 transport
- Indirect inputs: To produce cement → need limestone, energy
                    To produce steel → need iron ore, coal
                    To produce limestone → need extraction, transport
                    ... and so on

The Leontief inverse calculates the infinite series:
L = I + A + A² + A³ + ... = (I - A)^(-1)
```

**Calculation:**

```python
# Convert dy_inv_exog DataFrame to vector (19,680 elements)
# 162 countries × 120 sectors = 19,440 sector-regions
dy_vector = MRIO_df_to_vec(dy_inv_exog, ...)

# Load pre-computed Leontief inverse
L = MRIO_BASE.L_BASE  # 19,680 × 19,680 matrix

# Matrix multiplication: dq = L × dy
dq_total = L @ dy_vector  # @ is matrix multiplication in Python

# Result: dq_total is vector of 19,680 elements
# Each element = output change in that (country, sector) pair
```

**Output Multiplier:**

```python
output_multiplier = dq_total.sum() / dy_vector.sum()

# Example:
# Initial demand: $10M
# Total output: $17M
# Multiplier: 1.7x
# Interpretation: For every $1 of final demand,
#                 $1.70 of total output is needed (includes supply chain)
```

---

#### **Step 4: Calculate Employment**

**File:** `SourceCode/employment.py`, method `calc_dempl()`

**Purpose:** Convert output changes to employment changes

**Formula:** `dE = e × dq`

Where:
- `e` = Employment coefficient (jobs per $ output)
- `dq` = Output change
- `dE` = Employment change (jobs)

**Employment Coefficients:**

```python
# Loaded from: GLORIA_template/Employment/Empl_coefficient.csv
# Structure: Country × Sector matrix
# Values: Jobs per $1,000 of output

# Example coefficients:
# MEX, Construction (56): 0.015 jobs/$1k = 15 jobs/$1M
# MEX, Agriculture (23): 0.025 jobs/$1k = 25 jobs/$1M
# USA, Construction (56): 0.012 jobs/$1k = 12 jobs/$1M
```

**Sub-Step 4.1: Calculate Total Employment**

```python
# Total employment (direct + indirect)
dempl_total = empl_coef × dq_total

# Element-wise multiplication:
# For each (country, sector) pair:
#   jobs = coefficient × output_change

# Example:
# MEX Construction: 0.015 × $2,400,000 = 36 jobs
# MEX Cement: 0.020 × $1,800,000 = 36 jobs
# ...
# Total: Sum across all sectors = 200 jobs
```

**Sub-Step 4.2: Calculate Direct Employment**

```python
# Direct employment (from initial demand only)
dempl_direct = empl_coef × dy_vector

# Uses same coefficients, but applied to initial demand (dy)
# not total output (dq)

# Example:
# MEX Construction: 0.015 × $2,400,000 = 36 jobs (direct)
# Supply chain: 0 (not counted in direct)
```

**Sub-Step 4.3: Calculate Indirect Employment**

```python
# Indirect employment (supply chain jobs)
dempl_indirect = dempl_total - dempl_direct

# Example:
# Total: 200 jobs
# Direct: 120 jobs
# Indirect: 80 jobs (supply chain)
```

**Employment Multiplier:**

```python
employment_multiplier = dempl_total.sum() / total_investment * 1e6

# Example:
# Total jobs: 200
# Total investment: $10M
# Multiplier: 200 / 10 = 20 jobs per $1M invested
```

---

#### **Step 5: Aggregate Results**

**Two Aggregations:**

**A. Employment by Region**

```python
# Group by region (Reg_ID)
empl_by_region = results.groupby('Reg_ID').agg({
    'Direct_Jobs': 'sum',
    'Indirect_Jobs': 'sum',
    'Total_Jobs': 'sum'
})

# Add region names
empl_by_region = empl_by_region.merge(
    MRIO_BASE.R[['Region_acronyms', 'Region_names']],
    on region ID
)

# Example output:
# Region      | Region_Name | Direct | Indirect | Total
# MEX         | Mexico      | 100    | 60       | 160
# USA         | United States| 10    | 10       | 20
# CHN         | China       | 5      | 5        | 10
# ...
```

**B. Employment by Sector**

```python
# Group by sector (Sec_ID)
empl_by_sector = results.groupby('Sec_ID').agg({
    'Direct_Jobs': 'sum',
    'Indirect_Jobs': 'sum',
    'Total_Jobs': 'sum'
})

# Add sector names
empl_by_sector = empl_by_sector.merge(
    MRIO_BASE.P[['Lfd_Nr', 'Sector_names']],
    on sector ID
)

# Example output:
# Sector | Sector_Name  | Direct | Indirect | Total
# 56     | Construction | 36     | 15       | 51
# 45     | Cement       | 36     | 10       | 46
# 23     | Agriculture  | 20     | 25       | 45
# ...
```

---

## Data Structures

### Key DataFrames

#### **1. Scenario.inv_exog**
Investment amounts by sector

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| REG_imp | str | Country investing | "MEX" |
| PROD_COMM | int | Sector investing (1-120) | 56 |
| dk | float | Investment amount (USD) | 10000000 |

**Shape:** Variable rows (depends on scenario), 3 columns

---

#### **2. dy_inv_exog**
Initial final demand for products (after investment converter)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| REG_imp | str | Producing country | "MEX" |
| TRAD_COMM | int | Product code (1-120) | 56 |
| dy | float | Demand amount (USD) | 2400000 |

**Shape:** Variable rows (depends on scenario), 3 columns

---

#### **3. dq_total**
Total output changes (vector)

**Format:** NumPy array of 19,680 elements (or 19,440 depending on version)

**Structure:**
- Elements 0-119: Country 1, Sectors 1-120
- Elements 120-239: Country 2, Sectors 1-120
- ...
- Elements 19,560-19,679: Country 164, Sectors 1-120

**Units:** USD

---

#### **4. dempl_total, dempl_direct, dempl_indirect**
Employment changes (vectors)

**Format:** NumPy arrays of 19,680 elements each

**Structure:** Same as dq_total

**Units:** Jobs (number of workers)

---

#### **5. Employment Results DataFrames**

**A. Employment by Region**

| Column | Type | Description |
|--------|------|-------------|
| Strategy | int | Strategy ID (1004-4007) |
| Investing_Country | str | Country ISO code |
| Investing_Country_Name | str | Full country name |
| Region_acronyms | str | Region code |
| Region_names | str | Full region name |
| Direct_Jobs | float | Direct employment |
| Indirect_Jobs | float | Indirect employment |
| Total_Jobs | float | Total employment |

**Shape:** ~469 scenarios × 162 regions = ~76,000 rows, 8 columns

**B. Employment by Sector**

| Column | Type | Description |
|--------|------|-------------|
| Strategy | int | Strategy ID |
| Investing_Country | str | Country ISO code |
| Investing_Country_Name | str | Full country name |
| Lfd_Nr | int | Sector code (1-120) |
| Sector_names | str | Sector name |
| Direct_Jobs | float | Direct employment |
| Indirect_Jobs | float | Indirect employment |
| Total_Jobs | float | Total employment |

**Shape:** ~469 scenarios × 120 sectors = ~56,000 rows, 8 columns

**C. Batch Summary**

| Column | Type | Description |
|--------|------|-------------|
| Scenario_Number | int | Sequential number |
| Strategy | int | Strategy ID |
| Country | str | Country ISO code |
| Country_Name | str | Full country name |
| Status | str | SUCCESS/FAILED/SKIPPED |
| Total_Investment | float | Total investment (USD) |
| Direct_Jobs | float | Total direct jobs |
| Indirect_Jobs | float | Total indirect jobs |
| Total_Jobs | float | Total jobs |
| Employment_Multiplier | float | Jobs per $1M |
| Output_Multiplier | float | Output multiplier |
| Runtime_Seconds | float | Processing time |

**Shape:** 469 rows, 12 columns

---

## Output Files

### Location
All output files saved to: `GLORIA_results/`

### File Descriptions

#### **1. ALL_RESULTS_Employment_by_Region.csv**

**Content:** Employment impacts by geographic region for all scenarios

**Use cases:**
- Map which regions benefit most from each investment strategy
- Identify spillover effects (employment in regions other than investing country)
- Compare regional multipliers across countries

**Example analysis in R:**
```r
library(dplyr)
library(ggplot2)

empl_region <- read.csv("GLORIA_results/ALL_RESULTS_Employment_by_Region.csv")

# Which regions benefit most from MEX investments?
empl_region %>%
  filter(Investing_Country == "MEX") %>%
  group_by(Region_names) %>%
  summarize(Total_Jobs = sum(Total_Jobs)) %>%
  arrange(desc(Total_Jobs)) %>%
  head(10)

# Domestic vs spillover employment
empl_region %>%
  mutate(Domestic = Investing_Country == Region_acronyms) %>%
  group_by(Investing_Country, Domestic) %>%
  summarize(
    Direct = sum(Direct_Jobs),
    Indirect = sum(Indirect_Jobs),
    Total = sum(Total_Jobs)
  )
```

---

#### **2. ALL_RESULTS_Employment_by_Sector.csv**

**Content:** Employment impacts by economic sector for all scenarios

**Use cases:**
- Identify which sectors create most jobs
- Compare direct vs indirect employment by sector
- Analyze sector-specific multipliers

**Example analysis in R:**
```r
empl_sector <- read.csv("GLORIA_results/ALL_RESULTS_Employment_by_Sector.csv")

# Which sectors create most jobs in MEX?
empl_sector %>%
  filter(Investing_Country == "MEX") %>%
  group_by(Sector_names) %>%
  summarize(
    Direct = sum(Direct_Jobs),
    Indirect = sum(Indirect_Jobs),
    Total = sum(Total_Jobs),
    Indirect_Ratio = Indirect / Direct
  ) %>%
  arrange(desc(Total))

# Compare sectoral multipliers across countries
empl_sector %>%
  filter(Sector_names %in% c("Construction", "Transport", "Agriculture")) %>%
  group_by(Investing_Country, Sector_names) %>%
  summarize(
    Total_Jobs = sum(Total_Jobs),
    Avg_Strategy = Total_Jobs / n_distinct(Strategy)
  ) %>%
  ggplot(aes(x = Investing_Country, y = Total_Jobs, fill = Sector_names)) +
  geom_col(position = "dodge")
```

---

#### **3. BATCH_SUMMARY.csv**

**Content:** Summary statistics for each scenario

**Use cases:**
- Quick overview of all scenarios
- Compare employment multipliers across countries and strategies
- Identify failed or problematic scenarios
- Track processing times

**Example analysis in R:**
```r
summary <- read.csv("GLORIA_results/BATCH_SUMMARY.csv")

# Compare employment multipliers by country
summary %>%
  filter(Status == "SUCCESS") %>%
  group_by(Country_Name) %>%
  summarize(
    Avg_Multiplier = mean(Employment_Multiplier),
    Min_Multiplier = min(Employment_Multiplier),
    Max_Multiplier = max(Employment_Multiplier),
    Avg_Total_Jobs = mean(Total_Jobs),
    Direct_Share = mean(Direct_Jobs / Total_Jobs)
  ) %>%
  arrange(desc(Avg_Multiplier))

# Find strategies with highest employment creation
summary %>%
  filter(Status == "SUCCESS") %>%
  arrange(desc(Total_Jobs)) %>%
  select(Strategy, Country_Name, Total_Investment, Total_Jobs, Employment_Multiplier) %>%
  head(20)

# Check processing status
summary %>%
  count(Status)
```

---

## Troubleshooting

### Common Issues

#### **1. "ModuleNotFoundError: No module named 'SourceCode'"**

**Cause:** Python can't find MINDSET modules

**Solution:**
```python
# The script automatically fixes this (lines 33-44)
# But if it fails, manually check:
import sys
print(sys.path)

# Should include:
# C:/Users/festeves/.../MINDSET_module-main/MINDSET_module-main
```

---

#### **2. "FileNotFoundError: Scenario file not found"**

**Cause:** Missing scenario files

**Solution:**
```bash
# Check scenario files exist:
ls "GLORIA_template/Scenarios/Strategy_*"

# Verify naming convention:
# Strategy_{strategy_id}_{Country}.xlsx
# Example: Strategy_1004_MEX.xlsx
```

---

#### **3. "No investment data in scenario"**

**Cause:** Scenario file missing "Investment by" sheet or has no data

**Solution:**
```python
# Check Excel file structure:
import pandas as pd
xl = pd.ExcelFile("GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx")
print(xl.sheet_names)  # Should include "Investment by"

# Check data:
df = pd.read_excel(file, sheet_name='Investment by', skiprows=14)
print(df.head())
```

---

#### **4. "Memory Error" or script crashes**

**Cause:** MRIO matrices are large (~400MB in memory per scenario)

**Solution:**
- Close other applications
- Increase Python memory limit
- Process in smaller batches:
  ```python
  # Edit strategy_id list to process fewer at a time
  strategy_id = [1004, 1005, 1006]  # Process just 3 strategies
  ```

---

#### **5. Employment multipliers seem too high/low**

**Cause:** May indicate data issue or misunderstanding

**Check:**
```python
# Verify employment coefficients loaded correctly:
print(MRIO_BASE.EMPL_COEF.describe())

# Check investment amounts:
print(Scenario.inv_exog['dk'].sum())  # Should be reasonable ($M range)

# Verify Leontief inverse:
print(IO_model.L_BASE.shape)  # Should be (19680, 19680) or similar
```

**Typical multipliers:**
- Construction: 15-25 jobs/$1M
- Manufacturing: 10-20 jobs/$1M
- Services: 20-35 jobs/$1M
- Agriculture: 25-40 jobs/$1M (labor intensive)

If multipliers are >100 or <1, investigate data.

---

#### **6. Direct + Indirect ≠ Total**

**Cause:** Rounding errors or calculation mistake

**Check:**
```python
# Should be equal within floating point precision:
import numpy as np
diff = abs(dempl_total - (dempl_direct + dempl_indirect))
print(f"Max difference: {diff.max()}")
# Should be < 1e-10
```

---

### Getting Help

**For technical issues:**
1. Check this documentation first
2. Review `MINDSET_INVESTMENT_FLOW_DOCUMENTATION.md`
3. Examine log files in `GLORIA_results/`
4. Check original MINDSET documentation in `SourceCode/`

**For methodological questions:**
1. Review original MINDSET source code
2. Check Input-Output economics textbooks (Miller & Blair)
3. Consult with econometrician

---

## Appendix: Technical References

### Original MINDSET Source Code

All methodology based on:

1. **`SourceCode/scenario.py`**
   - Lines 321-383: `set_exog_inv()` method
   - Reads investment scenarios from Excel

2. **`SourceCode/investment.py`**
   - Lines 12-65: Investment class definition
   - Lines 217-253: `calc_dy_inv_exog()` method
   - Investment converter implementation

3. **`SourceCode/InputOutput.py`**
   - Leontief model implementation
   - `calc_dq_exog()` method

4. **`SourceCode/employment.py`**
   - Lines 10-56: Employment class
   - Lines 45-54: `calc_dempl()` method

5. **`SourceCode/results.py`**
   - Lines 17-99: Results output formatting
   - Original MINDSET output structure

6. **`RunMINDSET.py`**
   - Lines 498-520: Employment module initialization
   - Lines 718-730: Employment results assembly
   - Complete MINDSET workflow

### Input-Output Economics References

- **Miller, R.E. and Blair, P.D. (2009).** *Input-Output Analysis: Foundations and Extensions*. Cambridge University Press.
  - Chapter 2: Foundations of Input-Output Analysis
  - Chapter 6: Linkages, Key Sectors, and Employment Multipliers

- **Leontief, W. (1986).** *Input-Output Economics*. 2nd Edition. Oxford University Press.

---

## Version History

- **2026-03-20:** Detailed technical documentation created
  - Added complete investment-to-employment flow explanation
  - Documented all data structures
  - Added step-by-step calculation walkthrough
  - Included troubleshooting guide

- **2026-03-18:** Initial batch script created
  - `RunMINDSET_EmploymentOnly_BATCH.py`

- **2026-03-09:** Employment-only mode developed
  - `RunMINDSET_EmploymentOnly.py`

---

*Last updated: 2026-03-20*

*For questions, contact the research team*
