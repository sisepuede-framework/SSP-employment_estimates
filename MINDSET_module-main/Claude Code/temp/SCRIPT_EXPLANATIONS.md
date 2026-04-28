# Script Explanations and Logic
## Understanding the MINDSET Employment Analysis Code

**Purpose:** Explain each script's logic, purpose, and contribution to the final employment estimates in intuitive, accessible language.

---

## Table of Contents

1. [Overview](#overview)
2. [Core MINDSET Modules](#core-mindset-modules)
3. [Custom Scripts Created](#custom-scripts-created)
4. [Script Logic Deep Dive](#script-logic-deep-dive)
5. [Key Functions Explained](#key-functions-explained)
6. [Common Patterns](#common-patterns)

---

## Overview

### The Big Picture

Think of the employment analysis as a pipeline with several stages:

```
[Investment Data] → [Demand] → [Output] → [Employment] → [ISIC Sectors] → [Results]
```

Each script handles one part of this pipeline. Here's what happens:

1. **Load investment strategy** (scenario.py): "Country X invests $1M in products Y and Z"
2. **Convert to demand** (investment.py): "This creates demand for capital goods"
3. **Calculate output changes** (InputOutput_SSP.py): "To meet this demand, supply chains activate"
4. **Calculate employment** (employment.py): "Production requires workers"
5. **Aggregate to sectors** (batch script): "Group products into policy-relevant sectors"
6. **Save results** (batch script): "Export for analysis"

---

## Core MINDSET Modules

### These scripts are part of the MINDSET framework (we use them, didn't create them)

---

### 1. exog_vars_SSP.py

**What it does:**
Loads all the baseline data about the economy: how big each sector is, how many people work there, what the trade flows are, etc.

**Think of it as:** Reading the economic census before analyzing policy changes

**Key outputs:**
- `LABOR_BASE`: Employment data (960 rows = 8 countries × 120 products)
- `R`: Region information (8 SSP regions)
- `P`: Product information (120 GLORIA products)
- Various economic indicators (trade, emissions, etc.)

**Logic:**
```python
class exog_vars:
    def __init__(self):
        # Read configuration file
        variable_list = pd.read_excel('Variable_list_MINDSET_SSP.xlsx')

        # For each variable in the list
        for var in variable_list:
            # Load the data file
            data = load_file(var['path'])
            # Store it as an attribute
            setattr(self, var['name'], data)
```

**Why needed:** MINDSET needs to know the baseline state of the economy before calculating changes. It's like needing a "before" photo to show what changed.

**Intuition:** If Egypt currently has 133,518 workers in Product 90, and investment increases output by 10%, we need that baseline number to calculate the 10% increase in jobs.

---

### 2. scenario.py

**What it does:**
Reads an investment strategy file (Excel) and extracts how much is invested in which sectors.

**Think of it as:** Reading a government's infrastructure budget plan

**Key function:**
```python
class scenario:
    def set_exog_inv(self):
        # Read the Strategy Excel file
        inv_data = pd.read_excel(self.scenario_file)

        # Extract investment amounts
        # Column 'dk' = investment in thousands USD
        # Column 'REG_imp' = investing country
        # Column 'PROD_COMM' = product code
        self.inv_exog = inv_data[['REG_imp', 'PROD_COMM', 'dk']]
```

**Example:**
```
Strategy_1004_EGY.xlsx contains:
REG_imp  PROD_COMM  dk
EGY      86         200    ($200k in Product 86)
EGY      89         400    ($400k in Product 89)
EGY      90         400    ($400k in Product 90)
```

**Why needed:** Each strategy file is a different policy scenario. This script reads "what if we invest this way?"

**Intuition:** You can't calculate employment impacts without knowing what's being invested where.

---

### 3. investment.py

**What it does:**
Converts investment amounts into final demand for products.

**Think of it as:** Translating "build 100 schools" into "need X tons of cement, Y tons of steel, Z units of labor"

**Key function:**
```python
class invest:
    def calc_dy_inv_exog(self, inv_exog):
        # Investment creates demand
        # Use INV_CONV matrix to allocate investment across products
        # For our analysis: INV_CONV = Identity (code 90 → product 90 directly)

        dy_inv = INV_CONV @ inv_exog

        # Apply fcf_share to distribute across trading partners
        self.dy_inv_exog = dy_inv * fcf_share
```

**Our simplification:**
We use an **identity INV_CONV matrix**, meaning:
- Investment in "code 90" = demand for "product 90" directly
- No complex reallocation needed
- Makes interpretation straightforward

**Why needed:** Investment doesn't directly equal demand. For example, investing in "building construction" creates demand for cement, steel, glass, etc. This step figures out the shopping list.

**Intuition:** If you're building a road, you don't buy "road" - you buy concrete, asphalt, steel, machinery, etc. This script breaks investment into actual products demanded.

---

### 4. InputOutput_SSP.py

**What it does:**
Calculates how much each sector needs to produce to meet the new demand, accounting for all supply chain effects.

**Think of it as:** The domino effect calculator - shows how demand ripples through the economy

**Key functions:**

#### a. Initialize (one-time setup)
```python
def initialize(self):
    # Load Leontief inverse matrix
    self.L_BASE = load_mat('SSP/GLORIA_L_Base_2019.mat')

    # Load final demand baseline
    y_base_data = load_mat('SSP/GLORIA_Y_Base_2019.mat')
    self.y_base = y_base_data['y0']

    # Calculate baseline output
    self.q_base = self.L_BASE @ self.y_base
    # q_base = how much each sector currently produces
```

#### b. Calculate output changes
```python
def calc_dq_exog(self, dy_inv_exog):
    # Output change = Leontief inverse × demand change
    dq = self.L_BASE @ dy_inv_exog

    return dq
```

**The Magic of the Leontief Inverse:**

The Leontief inverse (`L`) contains all supply chain relationships. When demand increases by $1 in Construction:
- Construction produces $1 (direct)
- Steel produces $0.20 (supplies Construction)
- Mining produces $0.05 (supplies Steel)
- Transportation produces $0.10 (moves everything)
- ... and so on

`L` does all these calculations automatically in one matrix multiplication.

**Why needed:** The whole point of I-O analysis is capturing supply chain effects. Without this, we'd only count direct effects and miss most of the story.

**Intuition:** When you buy a car, you're not just supporting the car factory. You're also supporting:
- Steel mills (supply factory)
- Iron mines (supply steel mills)
- Coal mines (power steel mills)
- Transportation companies (move everything)
- Parts manufacturers (supply factory)
- ... dozens of other industries

The Leontief model calculates all of this automatically.

---

### 5. employment.py

**What it does:**
Converts output changes (dollars) into employment changes (people).

**Think of it as:** The "dollars to jobs" converter

**Key functions:**

#### a. Build employment coefficients (one-time)
```python
def build_empl_coef(self):
    # Load employment-output elasticities from GLORIA
    # These are empirically estimated for each country-product
    self.EMPL_COEF = load_csv('Employment/Empl_coefficient.csv')

    # EMPL_COEF tells us: "If output increases 1%, employment increases X%"
```

#### b. Calculate employment multipliers (one-time)
```python
def calc_empl_multiplier(self, empl_base, q_base):
    # Employment intensity = workers per dollar of output
    intensity = empl_base / q_base

    # Employment multiplier = elasticity × intensity
    self.empl_multiplier = EMPL_COEF * intensity

    # Result: "Each extra dollar of output → X extra workers"
```

#### c. Calculate employment changes (per strategy)
```python
def calc_dempl(self, dq):
    # Apply multipliers to output changes
    dempl = self.empl_multiplier * dq

    return dempl  # Jobs created in each sector
```

**Why the two-step calculation?**

1. **EMPL_COEF:** How responsive employment is to output changes (elasticity)
   - Example: If output ↑ 10%, employment ↑ 8% (EMPL_COEF = 0.8)

2. **Intensity (empl_base / q_base):** How labor-intensive production is
   - Example: Product produces $1M with 100 workers → intensity = 0.0001 workers/dollar

3. **Together:** elasticity × intensity = jobs per dollar of output

**Why needed:** We care about jobs, not just economic output. This converts GDP effects into employment effects.

**Intuition:** Some sectors are labor-intensive (restaurants - lots of workers per dollar), others are capital-intensive (oil refineries - few workers per dollar). This step accounts for these differences.

---

### 6. utils.py

**What it does:**
Helper functions used across MINDSET

**Key function we use:**
```python
def MRIO_df_to_vec(df, row_col, col_col, value_col, row_list, col_list):
    """
    Converts a dataframe (country, product, value) to a vector

    Example:
    Input DataFrame:
        country  product  value
        EGY      1        100
        EGY      2        200
        MEX      1        150
        ...

    Output vector: [100, 200, 0, 0, ..., 150, 0, ...]
    (ordered by: EGY products 1-120, then MEX products 1-120, etc.)
    """
    vector = np.zeros(len(row_list) * len(col_list))

    for _, row in df.iterrows():
        row_idx = row_list.index(row[row_col])
        col_idx = col_list.index(row[col_col])
        vector_idx = row_idx * len(col_list) + col_idx
        vector[vector_idx] = row[value_col]

    return vector
```

**Why needed:** MINDSET works with vectors (960 elements), but humans work better with dataframes (country, product, value). This converts between formats.

**Intuition:** Like converting between a spreadsheet (rows × columns) and a single list - different formats for different purposes.

---

## Custom Scripts Created

### These are scripts we wrote specifically for this analysis

---

### 1. InputOutput_SSP.py (Modified)

**What we changed:**
```python
# Original line 197:
path = f"GLORIA_db/{GLORIAv}/{year}/GLORIA_G_Base_{year}.mat"

# Our change:
path = f"GLORIA_db/{GLORIAv}/{year}/SSP/GLORIA_G_Base_{year}.mat"
#                                     ^^^^
#                                  Added SSP subfolder
```

**Same changes on lines 232 and 259** for L_BASE and Y_BASE.

**Why needed:** We created aggregated data in a `SSP/` subfolder to keep it separate from original GLORIA data. This modified script knows to look there.

**Impact:** Without this change, MINDSET would try to load 164-country matrices instead of our 8-region matrices → dimensions wouldn't match → crash.

---

### 2. TEST_FINAL_CLEAN.py

**Purpose:** Test script to validate methodology with one strategy

**Logic flow:**
```python
# 1. Load data (same as batch script)
load_crosswalk()
load_attributes()
load_MRIO()
initialize_models()

# 2. Process ONE strategy
strategy = "Strategy_1004_EGY"
load_investment(strategy)
calculate_demand()
calculate_output()
calculate_employment()
aggregate_to_ISIC()

# 3. Display results
print_results()
print_validation_checks()
```

**Why needed:** Before running 469 strategies (30-60 minutes), we needed to:
- Verify methodology is correct
- Check output structure is right
- Validate calculations match expected values
- Identify any bugs

**Result:** Confirmed everything works correctly on one case before scaling up.

**Intuition:** You wouldn't bake 100 cakes without first testing the recipe with one, right?

---

### 3. BATCH_EMPLOYMENT_ALL_STRATEGIES.py

**Purpose:** Production script - processes all 469 strategies

**High-level logic:**
```python
# SETUP (once)
load_crosswalk()  # 120 products → 20 ISIC sectors
load_attributes()  # Strategy names
load_MRIO_data()  # Economy baseline
initialize_IO_model()  # Build Leontief inverse
initialize_employment_model()  # Build employment multipliers

# PROCESS EACH STRATEGY (469 iterations)
results = []
for strategy_file in all_469_files:
    # Load investment
    investment = load_strategy(strategy_file)
    country = get_country(strategy_file)

    # Skip if ROW (we're excluding it)
    if country == 'ROW':
        continue

    # Calculate impacts
    demand = convert_investment_to_demand(investment)
    output = calculate_output_via_leontief(demand)
    employment = calculate_employment_from_output(output)

    # Separate direct vs. indirect
    direct = employment[where demand > 0]
    indirect = employment[where demand == 0]

    # Aggregate 120 products → 20 ISIC sectors
    sector_employment = {}
    for product in products:
        sectors = crosswalk[product]  # Which ISIC sector(s)?
        weight = 1.0 / len(sectors)  # Divide if multiple sectors

        for sector in sectors:
            sector_employment[sector] += employment[product] * weight

    # Calculate shares
    total = sum(sector_employment.values())
    for sector in sectors:
        share = sector_employment[sector] / total
        results.append({
            'country': country,
            'strategy': strategy_file,
            'sector': sector,
            'direct_jobs': direct_by_sector[sector],
            'indirect_jobs': indirect_by_sector[sector],
            'total_jobs': sector_employment[sector],
            'share': share
        })

# FINALIZE
df = create_dataframe(results)
merge_strategy_names(df, attributes)
validate(df)  # Check shares sum to 1.0
export_to_csv(df, 'employment_consolidated.csv')
print_summary_statistics()
```

**Key design decisions:**

#### a. One-time initialization
```python
# Load MRIO once (not 469 times)
MRIO_BASE = exog_vars()  # ~0.5 seconds

# Build models once (not 469 times)
IO_model = IO(MRIO_BASE)
IO_model.initialize()  # ~5 seconds

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)  # ~2 seconds

# Total: ~8 seconds once vs. 469 × 8 seconds = 62 minutes if repeated
```

**Intuition:** Like pre-heating an oven once instead of for each batch of cookies.

#### b. Error handling
```python
try:
    # Process strategy
    results = process_strategy(strategy_file)
except Exception as e:
    # Log error but continue
    errors.append(f"{strategy_file}: {e}")
    continue  # Don't crash, just skip this one
```

**Why:** If one strategy file is corrupted or formatted wrong, we don't want to lose results from the other 468. Log the error and move on.

#### c. Progress tracking
```python
if idx % 10 == 0:  # Every 10 strategies
    elapsed = time.now() - start
    rate = strategies_done / elapsed
    remaining_time = (total - strategies_done) / rate
    print(f"[{idx}/{total}] {strategy_name} (~{remaining_time:.1f} min remaining)")
```

**Why:** 469 strategies takes 30-60 minutes. Without progress tracking, you'd have no idea if it's frozen or just slow.

#### d. Validation
```python
# After creating dataset, verify quality
shares_per_strategy = df.groupby(['country', 'strategy'])['share'].sum()

assert shares_per_strategy.mean() ≈ 1.0, "Shares don't sum to 1.0!"
assert all(df['total_jobs'] >= 0), "Negative employment found!"
assert all(df['total_jobs'] == df['direct'] + df['indirect']), "Math error!"
```

**Why:** Catch calculation errors before spending hours analyzing wrong data.

---

## Script Logic Deep Dive

### How Direct vs. Indirect Employment Works

**The Question:** "I invest $1M in Product 90 (machinery). Where do jobs get created?"

**The Logic:**

#### Step 1: Identify which sectors receive direct demand
```python
# Investment creates demand
dy_inv_exog = [0, 0, ..., 1000 (Product 90), 0, ...]
#                        ^^^^
#                   Only Product 90 has direct demand

# Create mask
direct_mask = (dy_inv_exog > 0)
# Result: [False, False, ..., True (Product 90), False, ...]
```

#### Step 2: Calculate total output (direct + supply chain)
```python
dq = L_BASE @ dy_inv_exog

# Result might be:
dq = [
    5,     # Product 1: supplies inputs indirectly
    3,     # Product 2: supplies inputs indirectly
    ...
    1200,  # Product 90: direct production (>1000 due to multiplier)
    ...
    10     # Product 100: supplies inputs indirectly
]
```

**Why is Product 90 > $1000?** The Leontief multiplier! To produce $1000 of Product 90, you need inputs, which need inputs, etc. Total production > initial demand.

#### Step 3: Calculate employment for all products
```python
dempl = empl_multiplier * dq

# Result:
dempl = [
    0.5,   # Product 1: 0.5 jobs (indirect, supplies inputs)
    0.3,   # Product 2: 0.3 jobs (indirect)
    ...
    15.0,  # Product 90: 15 jobs (direct)
    ...
    0.8    # Product 100: 0.8 jobs (indirect)
]
```

#### Step 4: Separate using mask
```python
# Where did we have direct demand?
direct_jobs = dempl[direct_mask]
# = [15.0]  (only Product 90)

# Where did we NOT have direct demand?
indirect_jobs = dempl[~direct_mask]
# = [0.5, 0.3, ..., 0.8]  (all supply chain)

# Total
total_direct = sum(direct_jobs) = 15.0
total_indirect = sum(indirect_jobs) = 5.5
total = 20.5 jobs
```

**Intuition:**
- **Direct:** Jobs in sectors you directly bought from (Product 90 - machinery)
- **Indirect:** Jobs in all the suppliers (steel for machinery, transport for steel, etc.)

---

### How ISIC Aggregation Works

**The Challenge:** 120 products is too detailed. Policy analysis needs sectors.

**Example:** Egypt, Product 1 (wheat) creates 2.5 jobs

#### Step 1: Look up in crosswalk
```python
crosswalk[Product 1] = ['A']  # Maps to Sector A (Agriculture)
```

#### Step 2: Add to sector total
```python
sector_jobs['A'] += 2.5
```

**Simple case:** One product → one sector

**Complex case:** Product 119 (other services)
```python
crosswalk[Product 119] = ['S', 'T']  # Maps to two sectors

# Divide equally (no better information available)
weight = 1.0 / 2 = 0.5

sector_jobs['S'] += employment[Product 119] * 0.5
sector_jobs['T'] += employment[Product 119] * 0.5
```

**Why divide equally?** We don't have data on the exact split. Equal division is the conservative assumption.

---

### How Strategy Name Merging Works

**The Problem:** Strategy files are named "Strategy_1004_EGY" but we want "Agricultural Infrastructure Investment"

#### Step 1: Extract numeric ID
```python
import re

strategy_name = "Strategy_1004_EGY"
match = re.search(r'_(\d+)_', strategy_name)
numeric_id = int(match.group(1))  # = 1004
```

#### Step 2: Look up in attributes
```python
attributes = pd.read_csv('ATTRIBUTE_STRATEGY.csv')
#    strategy_id  strategy
# 0      1003      EGY Test A
# 1      1004      Agricultural Infrastructure
# 2      1005      EGY Test B

strategy_name = attributes[attributes['strategy_id'] == 1004]['strategy']
# = "Agricultural Infrastructure"
```

#### Step 3: Merge into results
```python
results['strategy_numeric_id'] = 1004

results = results.merge(
    attributes.rename(columns={'strategy': 'strategy_name'}),
    left_on='strategy_numeric_id',
    right_on='strategy_id',
    how='left'  # Keep all strategies, even if no match
)

# Drop helper columns
results = results.drop(columns=['strategy_numeric_id', 'strategy_id'])
```

**Result:** Now results have both "Strategy_1004_EGY" and "Agricultural Infrastructure" for filtering and display.

---

## Key Functions Explained

### 1. MRIO_df_to_vec

**Purpose:** Convert (country, product, value) table to a single vector

**Why needed:** MINDSET math uses vectors (960 elements), but data comes in tables

**Example:**
```python
# Input (DataFrame):
  country  product  value
  EGY      1        10
  EGY      2        20
  MEX      1        15

# Output (vector):
# [10, 20, 0, 0, ...(120 elements for EGY), 15, 0, ...(120 elements for MEX), ...]
# Position = country_idx * 120 + product_idx
```

**Logic:**
```python
def MRIO_df_to_vec(df, row_col, col_col, value_col, row_list, col_list):
    n_rows = len(row_list)  # 8 countries
    n_cols = len(col_list)  # 120 products
    vector = np.zeros(n_rows * n_cols)  # 960 elements

    for _, row in df.iterrows():
        # Find position in vector
        row_idx = row_list.index(row[row_col])  # Which country?
        col_idx = col_list.index(row[col_col])  # Which product?
        vector_idx = row_idx * n_cols + col_idx  # Position = country*120 + product

        # Store value
        vector[vector_idx] = row[value_col]

    return vector
```

**Intuition:** Like flattening a 2D spreadsheet into a single column, but keeping track of which cell is which.

---

### 2. calc_dq_exog

**Purpose:** Calculate output changes from demand changes via Leontief model

**Formula:** dq = L × dy

**Why it works:** The Leontief inverse contains all the supply chain relationships

**Example:**
```python
L = [
    [1.05, 0.10, ...],  # Product 1 needs inputs from Products 1, 2, ...
    [0.15, 1.20, ...],  # Product 2 needs inputs from ...
    ...
]

dy = [0, 0, ..., 1000 (Product 90), 0, ...]  # Demand increase

dq = L @ dy
# Result: Output changes for all products, including supply chain
```

**Breakdown:**
- `L[90,90] = 1.2`: Product 90 needs to produce $1.20 to deliver $1 to final demand (the extra $0.20 is inputs)
- `L[50,90] = 0.15`: Product 50 needs to produce $0.15 per $1 of Product 90 (supplies inputs to 90)
- Multiplying gives us everyone's production increase

---

### 3. calc_dempl

**Purpose:** Convert output changes to employment changes

**Formula:** dempl = empl_multiplier × dq

**Where empl_multiplier comes from:**
```python
empl_multiplier = EMPL_COEF × (empl_base / q_base)
                     ↑              ↑
                elasticity    intensity
```

**Example:**
```python
# Product 90 in Egypt
EMPL_COEF[90] = 0.9  # If output ↑10%, employment ↑9% (elastic)
empl_base[90] = 1000 workers
q_base[90] = $10M
intensity = 1000 / 10M = 0.0001 workers per dollar

empl_multiplier[90] = 0.9 × 0.0001 = 0.00009 jobs per dollar

# If output increases by $100k
dq[90] = 100,000
dempl[90] = 0.00009 × 100,000 = 9 jobs
```

---

## Common Patterns

### Pattern 1: Load Once, Use Many Times

**Inefficient:**
```python
for strategy in strategies:
    MRIO = load_MRIO()  # ← Loads every time!
    process(strategy, MRIO)
```

**Efficient:**
```python
MRIO = load_MRIO()  # ← Load once
for strategy in strategies:
    process(strategy, MRIO)
```

**Why:** Loading MRIO takes 0.5 seconds. × 469 strategies = 4 minutes wasted.

---

### Pattern 2: Separate Concerns

**Good practice:**
```python
# Step 1: Calculate (pure logic, no I/O)
results = calculate_employment(strategies)

# Step 2: Validate (separate concern)
validate(results)

# Step 3: Save (I/O, separate from logic)
save_to_csv(results)
```

**Why:** If validation fails, we know the calculation is wrong, not the file writing. Easier to debug.

---

### Pattern 3: Vectorization Over Loops

**Slow:**
```python
for i in range(960):
    output[i] = multiplier[i] * input[i]
```

**Fast:**
```python
output = multiplier * input  # NumPy vectorized multiplication
```

**Why:** NumPy operations are optimized in C. 100-1000x faster than Python loops.

---

### Pattern 4: Guard Clauses

**Instead of deep nesting:**
```python
def process_strategy(strategy):
    if strategy is not None:
        if strategy.country != 'ROW':
            if strategy.investment > 0:
                # ... lots of logic here
```

**Use early returns:**
```python
def process_strategy(strategy):
    if strategy is None:
        return None

    if strategy.country == 'ROW':
        return None  # Skip ROW

    if strategy.investment <= 0:
        return None  # No investment, no employment

    # ... logic here (not nested)
```

**Why:** Easier to read, easier to modify conditions, fewer indentation levels.

---

## Summary: What Each Script Contributes

| Script | Contribution | Output |
|--------|--------------|--------|
| exog_vars_SSP.py | Loads baseline economy data | LABOR_BASE, MRIO structures |
| scenario.py | Reads investment strategy | inv_exog (investment vector) |
| investment.py | Converts investment to demand | dy_inv_exog (demand vector) |
| InputOutput_SSP.py | Calculates supply chain effects | dq_total (output changes) |
| employment.py | Converts output to jobs | dempl (employment changes) |
| BATCH_EMPLOYMENT_...py | Orchestrates all + aggregation | employment_consolidated.csv |

**The Chain:**
```
inv_exog → dy_inv_exog → dq_total → dempl → ISIC aggregation → results
```

Each script does one thing well, and they compose into the complete analysis.

---

*Document Version: 1.0*
*Last Updated: March 22, 2026*
*Status: Complete*
