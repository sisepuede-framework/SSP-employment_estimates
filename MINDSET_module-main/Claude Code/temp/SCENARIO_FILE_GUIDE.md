# MINDSET Scenario File Guide

## Understanding How Demand Shocks Work

### For R Users: Think of it Like This

**In R, you might do:**
```r
# Create a demand shock vector
demand_shock <- data.frame(
  country = c("USA", "USA", "CHN"),
  product = c(1, 2, 1),
  shock_amount = c(1000000, 500000, 750000)
)

# Then multiply by Leontief inverse
output_change <- Leontief %*% demand_shock
```

**In MINDSET Python:**
- The Excel file IS your `demand_shock` data.frame
- The script reads it and does the Leontief multiplication automatically
- You just specify: Which country + Which product + How much $$$

---

## Two Ways to Specify Demand Shocks

MINDSET has TWO sheets for demand shocks (you only need ONE):

### Option 1: "Final demand" Sheet (✓ RECOMMENDED for your case)
- **Direct approach**: Specify demand shock directly
- **Simpler**: No investment converter needed
- **Perfect for**: Testing specific product demand shocks
- **Format**: Country + Product + Amount

### Option 2: "Investment by" Sheet (More complex)
- **Indirect approach**: Specify which sector invests, then converts to demand
- **More complex**: Uses investment converter matrix
- **Perfect for**: Realistic investment scenarios by industry
- **Format**: Country + Investing Sector + Amount → Converts to product demand

**For your dissertation testing different demand shocks across 120 products, use "Final demand" sheet!**

---

## Understanding the "Final demand" Sheet

### Key Concept: Final Demand vs Intermediate Demand

**R Analogy:**
```r
# GLORIA Input-Output structure:
Total_Output = Intermediate_Demand + Final_Demand

# where Final_Demand includes:
FD_1 = Household consumption
FD_2 = NPISH (non-profits)
FD_3 = Government spending
FD_4 = Gross fixed capital formation (investment)
FD_5 = Changes in inventories
FD_6 = Changes in valuables
```

**Your demand shock goes into one of these FD categories!**

### Sheet Structure

The "Final demand" sheet (after row 14 header) needs these columns:

| Column Name | What It Means | Your Input | R Equivalent |
|-------------|---------------|------------|--------------|
| **Producing country ISO*** | Which country produces the good | "USA", "CHN", "BRA" | `producer_country` |
| **Consuming country ISO*** | Which country consumes/buys it | "USA", "CHN", "ALL" | `consumer_country` |
| **Product code*** | Which GLORIA product (1-120) | 1, 2, 3, ...120 | `product_id` |
| **FD code*** | Which final demand category | FD_1, FD_3, FD_4 | `demand_category` |
| **Value*** | Amount in USD | 1000000 | `shock_amount` |
| **Type*** | How to interpret the value | abs-b, rel-b | `shock_type` |

\* = Required columns (must be named exactly like this)

### Type Options

| Type | Meaning | Example | R Equivalent |
|------|---------|---------|--------------|
| **abs-b** | Absolute value, spread proportionally if "ALL" | $1M to product 5 | `shock <- 1000000` |
| **rel-b** | Relative to baseline (as %) | 0.10 = +10% increase | `shock <- baseline * 1.10` |

**Use "abs-b" for absolute dollar amounts!**

---

## Creating Your Scenario File

### Your Goal
> "120 GLORIA products as rows, each column is a different demand shock"

### Strategy: Create One Excel File with Multiple Sheets

**Structure:**
```
MyScenarios.xlsx
├── Scenario_1      ← First demand shock scenario
├── Scenario_2      ← Second demand shock scenario
├── Scenario_3      ← Third demand shock scenario
└── ...
```

Wait, that won't work because MINDSET reads ONE file at a time!

### Better Strategy: Create Multiple Scenario Files

**Structure:**
```
GLORIA_template/Scenarios/
├── Scenario_Construction.xlsx      ← Construction sector shock
├── Scenario_Manufacturing.xlsx     ← Manufacturing shock
├── Scenario_Services.xlsx          ← Services shock
├── Scenario_Agriculture.xlsx       ← Agriculture shock
└── ...
```

Then run the script once per scenario:
```python
scenario_name = "Scenario_Construction"  # Change this each time
```

### Or: Use One File with ALL Scenarios Combined

**Best approach for your case:**
```
Scenario_AllProducts.xlsx
  Sheet: Final demand
    Row 1-15: Headers (template structure)
    Row 16: Product 1, Country 1, Shock 1
    Row 17: Product 2, Country 1, Shock 1
    ...
    Row 135: Product 120, Country 1, Shock 1
    Row 136: Product 1, Country 1, Shock 2
    Row 137: Product 2, Country 1, Shock 2
    ...
```

Values sum up automatically! MINDSET groups by (Country, Product) and sums.

---

## Step-by-Step: Creating Your Scenario File

### Step 1: Get the Template

I'll create a template Excel file for you with proper structure.

### Step 2: Understand GLORIA Products (1-120)

The 120 GLORIA products are like this:

| Code | Example Product Name | Category |
|------|---------------------|----------|
| 1 | Paddy rice | Agriculture |
| 2 | Wheat | Agriculture |
| ... | ... | ... |
| 56 | Construction | Construction |
| 57 | Retail trade | Services |
| ... | ... | ... |
| 120 | Activities of households | Services |

**To get the full list:**
```python
import pandas as pd
products = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx', 'P')
print(products[['Lfd_Nr', 'Product_name']])
```

### Step 3: Choose Your Countries

GLORIA has 162 regions. Common ones:

| ISO Code | Country/Region |
|----------|----------------|
| USA | United States |
| CHN | China |
| BRA | Brazil |
| IND | India |
| DEU | Germany |
| GBR | United Kingdom |
| ... | ... |
| ROW | Rest of World |

**Special codes:**
- **ALL** = All countries (shock spread proportionally across all)

**To get the full list:**
```python
import pandas as pd
regions = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET.xlsx', 'R')
print(regions[['Region_acronyms', 'Region_names']])
```

### Step 4: Fill in Your Data

**Example: $100M shock to Construction (product 56) in USA**

| Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
|------------------------|------------------------|---------------|----------|--------|-------|
| USA | USA | 56 | FD_4 | 100000000 | abs-b |

**Example: $1M to each of 10 products in China**

| Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
|------------------------|------------------------|---------------|----------|--------|-------|
| CHN | CHN | 1 | FD_4 | 1000000 | abs-b |
| CHN | CHN | 2 | FD_4 | 1000000 | abs-b |
| CHN | CHN | 3 | FD_4 | 1000000 | abs-b |
| ... | ... | ... | ... | ... | ... |
| CHN | CHN | 10 | FD_4 | 1000000 | abs-b |

**Example: $100M spread across ALL products proportionally**

| Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
|------------------------|------------------------|---------------|----------|--------|-------|
| USA | USA | ALL | FD_4 | 100000000 | abs-b |

MINDSET will automatically spread the $100M across all 120 products proportionally to their baseline values.

---

## Advanced Features (Optional)

### Using "ALL" for Multiple Countries/Products

**Spread $100M across all products in ALL countries:**
| Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
|------------------------|------------------------|---------------|----------|--------|-------|
| ALL | ALL | ALL | FD_4 | 100000000 | abs-b |

### Using Ranges (Hyphen)

**Products 1-10:**
| Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
|------------------------|------------------------|---------------|----------|--------|-------|
| USA | USA | 1-10 | FD_4 | 10000000 | abs-b |

MINDSET expands "1-10" to products 1,2,3,4,5,6,7,8,9,10

### Using Lists (Comma)

**Products 1,5,10,15:**
| Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
|------------------------|------------------------|---------------|----------|--------|-------|
| USA | USA | 1,5,10,15 | FD_4 | 4000000 | abs-b |

MINDSET expands to 4 rows, $1M each.

---

## Common Scenarios for Your Dissertation

### Scenario A: Test Each Product Individually

**Goal:** See employment impact of $1M investment in each of 120 products

**Approach:** 120 rows, one per product
```
Product 1: $1M
Product 2: $1M
...
Product 120: $1M
```

**Result:** Run script once, get employment multiplier for all 120 products in one Excel output

### Scenario B: Test Specific Sectors

**Goal:** Compare construction vs manufacturing vs services

**Approach:** Create 3 separate files:
- `Scenario_Construction.xlsx`: $100M to construction products
- `Scenario_Manufacturing.xlsx`: $100M to manufacturing products
- `Scenario_Services.xlsx`: $100M to services products

**Result:** Run script 3 times, compare results

### Scenario C: Test Different Countries

**Goal:** See how $100M in USA vs China vs Brazil creates different employment

**Approach:** Create 3 files or use one file with 3 rows:

| Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
|------------------------|------------------------|---------------|----------|--------|-------|
| USA | USA | 56 | FD_4 | 100000000 | abs-b |
| CHN | CHN | 56 | FD_4 | 100000000 | abs-b |
| BRA | BRA | 56 | FD_4 | 100000000 | abs-b |

**Result:** One run, compare USA vs CHN vs BRA employment impacts

---

## Template File Structure

Your Excel file should look like this:

```
Row 1-14: Header information (template boilerplate)
Row 15: Column headers: | Producing country ISO* | Consuming country ISO* | Product code* | FD code* | Value* | Type* |
Row 16+: Your data
```

**Critical:** MINDSET uses `skiprows=14` so rows 1-14 are ignored, row 15 must be headers!

---

## Checking Your File Works

### Test Script

After creating your scenario file, test it:

```python
import pandas as pd
import os

os.chdir("C:/path/to/MINDSET_module-main")

# Load your scenario
scenario_file = "GLORIA_template/Scenarios/YourScenario.xlsx"
df = pd.read_excel(scenario_file, sheet_name='Final demand', skiprows=14)

print("Columns found:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Check required columns exist
required = ['Producing country ISO*', 'Consuming country ISO*',
            'Product code*', 'FD code*', 'Value*', 'Type*']
missing = [col for col in required if col not in df.columns]
if missing:
    print(f"\n❌ Missing columns: {missing}")
else:
    print("\n✓ All required columns present!")

print(f"\nTotal investment specified: ${df['Value*'].sum():,.0f}")
print(f"Number of shock specifications: {len(df)}")
```

---

## R vs Python: Key Concepts

| R Concept | Python/MINDSET Equivalent |
|-----------|---------------------------|
| Data frame with shocks | Excel "Final demand" sheet |
| `country_id` column | "Producing country ISO*" and "Consuming country ISO*" |
| `product_id` column | "Product code*" (1-120) |
| `shock_amount` column | "Value*" |
| Multiple scenarios = list of data frames | Multiple Excel files or multiple rows |
| `for (scenario in scenarios)` | Change `scenario_name` and re-run script |

---

## Summary: What You Need

✓ **One Excel file** with "Final demand" sheet

✓ **Minimum 6 columns**:
  - Producing country ISO*
  - Consuming country ISO*
  - Product code* (1-120)
  - FD code* (use FD_4 for investment)
  - Value* (dollars)
  - Type* (use "abs-b")

✓ **Data starts at row 16** (after row 15 headers)

✓ **Multiple shocks** = multiple rows (they sum up)

✓ **Run once per scenario file** (change line 103 in script)

---

## Next Steps

1. I'll create a template Excel file for you
2. I'll create a Python script to generate scenarios programmatically
3. You fill in your specific demand shocks
4. Run the employment script
5. Analyze results!

Want me to create these files now?
