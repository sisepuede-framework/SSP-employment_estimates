# MINDSET Batch Processing Guide

## Overview

The `RunMINDSET_EmploymentOnly_BATCH.py` script automatically processes all 467 scenario files (67 strategies × 7 countries) and combines the results into analysis-ready datasets.

---

## Quick Start

### 1. Ensure All Scenario Files Exist

Your scenario files should be named:
```
Strategy_{strategy_id}_{ISO}.xlsx
```

Examples:
- `Strategy_3010_MEX.xlsx`
- `Strategy_3010_MAR.xlsx`
- `Strategy_1004_BGR.xlsx`

**Location:** `GLORIA_template/Scenarios/`

**Total files expected:** 469 files (67 strategies × 7 countries)

### 2. Run the Batch Script

```bash
cd "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main"

python "Claude Code/temp/RunMINDSET_EmploymentOnly_BATCH.py"
```

**Or in Positron/RStudio:**
- Open `RunMINDSET_EmploymentOnly_BATCH.py`
- Press **Ctrl+Shift+Enter** (Run entire script)

### 3. Monitor Progress

The script will print progress for each scenario:
```
[1/469] Processing Strategy_1004_BGR...
    ✓ SUCCESS: 1,234 jobs, Multiplier: 12.3 jobs/$1M, Time: 5.2s

[2/469] Processing Strategy_1004_BLZ...
    ✓ SUCCESS: 1,150 jobs, Multiplier: 11.5 jobs/$1M, Time: 5.1s
```

### 4. Collect Results

After completion, you'll have 3 files in `GLORIA_results/`:

1. **ALL_RESULTS_Employment_by_Region.csv**
2. **ALL_RESULTS_Employment_by_Sector.csv**
3. **BATCH_SUMMARY.csv**

---

## What the Script Does

### Step-by-Step Process

1. **Load MRIO Data Once** (1-2 minutes)
   - Loads Leontief inverse matrix
   - Loads employment coefficients
   - Shared across all scenarios (efficient!)

2. **Loop Through All Scenarios** (~5 seconds per scenario)
   - For each strategy-country combination:
     - Reads scenario file
     - Runs employment estimation
     - Stores results
     - Clears memory

3. **Combine Results** (~10 seconds)
   - Concatenates all scenario results
   - Saves to CSV files

4. **Generate Summary** (~5 seconds)
   - Creates log with success/failure status
   - Calculates runtime statistics

---

## Output Files Explained

### 1. ALL_RESULTS_Employment_by_Region.csv

**What it contains:** Jobs created in each region for each scenario

**Columns:**
- `Strategy` - Strategy ID (e.g., 3010)
- `Investing_Country` - Country that invested (e.g., MEX)
- `Region_acronyms` - Where jobs were created (e.g., USA, CHN)
- `Region_names` - Full region name
- `Jobs_Created` - Number of jobs created in that region

**Example rows:**
```csv
Strategy,Investing_Country,Region_acronyms,Region_names,Jobs_Created
3010,MEX,MEX,Mexico,950.5
3010,MEX,USA,United States,80.2
3010,MEX,CHN,China,50.3
3010,MAR,MAR,Morocco,900.1
3010,MAR,USA,United States,75.4
```

**Use for:**
- ✓ Spillover analysis: How many jobs does Country A's investment create in Country B?
- ✓ Regional impact: Which regions benefit most from each strategy?
- ✓ Domestic vs. foreign jobs: Compare jobs in investing country vs. elsewhere

**R analysis example:**
```r
library(dplyr)
library(ggplot2)

results <- read.csv("GLORIA_results/ALL_RESULTS_Employment_by_Region.csv")

# Spillover analysis: Jobs in investing country vs. other countries
results %>%
  mutate(Job_Type = ifelse(Investing_Country == Region_acronyms,
                           "Domestic", "Spillover")) %>%
  group_by(Strategy, Investing_Country, Job_Type) %>%
  summarize(Total_Jobs = sum(Jobs_Created))

# Top 5 regions benefiting from Mexico's Strategy 3010
results %>%
  filter(Strategy == 3010, Investing_Country == "MEX") %>%
  arrange(desc(Jobs_Created)) %>%
  head(5)
```

---

### 2. ALL_RESULTS_Employment_by_Sector.csv

**What it contains:** Jobs created in each economic sector for each scenario

**Columns:**
- `Strategy` - Strategy ID
- `Investing_Country` - Country that invested
- `Lfd_Nr` - Sector code (1-120)
- `Sector_names` - Sector name (e.g., Construction, Manufacturing)
- `Jobs_Created` - Number of jobs in that sector

**Example rows:**
```csv
Strategy,Investing_Country,Lfd_Nr,Sector_names,Jobs_Created
3010,MEX,1,Agriculture,50.2
3010,MEX,56,Construction,800.5
3010,MEX,57,Utilities,120.3
3010,MAR,1,Agriculture,45.1
3010,MAR,56,Construction,750.2
```

**Use for:**
- ✓ Sectoral breakdown: Which industries benefit from investment?
- ✓ Direct vs. indirect: Identify target sector vs. supplier sectors
- ✓ Industry comparison: Compare labor intensity across sectors

**R analysis example:**
```r
results <- read.csv("GLORIA_results/ALL_RESULTS_Employment_by_Sector.csv")

# Top 10 sectors benefiting from all strategies in Mexico
results %>%
  filter(Investing_Country == "MEX") %>%
  group_by(Sector_names) %>%
  summarize(Total_Jobs = sum(Jobs_Created)) %>%
  arrange(desc(Total_Jobs)) %>%
  head(10) %>%
  ggplot(aes(x = reorder(Sector_names, Total_Jobs), y = Total_Jobs)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  labs(title = "Top 10 Sectors - Mexico Investment")

# Compare sectoral patterns across countries for same strategy
results %>%
  filter(Strategy == 3010) %>%
  group_by(Investing_Country, Sector_names) %>%
  summarize(Jobs = sum(Jobs_Created)) %>%
  pivot_wider(names_from = Investing_Country, values_from = Jobs)
```

---

### 3. BATCH_SUMMARY.csv

**What it contains:** Summary statistics for each scenario run

**Columns:**
- `Scenario_Number` - Sequential number (1-469)
- `Strategy` - Strategy ID
- `Country` - Investing country
- `Status` - SUCCESS, FAILED, or SKIPPED
- `Total_Investment` - Investment amount (USD)
- `Total_Jobs` - Total jobs created across all regions
- `Employment_Multiplier` - Jobs per $1M invested
- `Output_Multiplier` - Output change / investment
- `Runtime_Seconds` - Time to process this scenario

**Example rows:**
```csv
Scenario_Number,Strategy,Country,Status,Total_Investment,Total_Jobs,Employment_Multiplier,Output_Multiplier,Runtime_Seconds
1,1004,BGR,SUCCESS,100000000,1234.5,12.3,1.85,5.2
2,1004,BLZ,SUCCESS,100000000,1150.2,11.5,1.78,5.1
3,1004,EGY,FAILED,,,,,4.8
```

**Use for:**
- ✓ Quality control: Identify failed scenarios
- ✓ Multiplier comparison: Compare employment multipliers across countries
- ✓ Strategy ranking: Which strategies create most jobs per dollar?
- ✓ Performance monitoring: Check runtime issues

**R analysis example:**
```r
summary <- read.csv("GLORIA_results/BATCH_SUMMARY.csv")

# Check success rate
table(summary$Status)

# Average multiplier by country
summary %>%
  filter(Status == "SUCCESS") %>%
  group_by(Country) %>%
  summarize(
    Avg_Multiplier = mean(Employment_Multiplier),
    Avg_Jobs = mean(Total_Jobs),
    N_Strategies = n()
  ) %>%
  arrange(desc(Avg_Multiplier))

# Top 10 strategies overall (across all countries)
summary %>%
  filter(Status == "SUCCESS") %>%
  arrange(desc(Employment_Multiplier)) %>%
  head(10) %>%
  select(Strategy, Country, Total_Jobs, Employment_Multiplier)

# Compare same strategy across countries
summary %>%
  filter(Strategy == 3010, Status == "SUCCESS") %>%
  select(Country, Total_Jobs, Employment_Multiplier) %>%
  arrange(desc(Employment_Multiplier))
```

---

## Configuration Options

### Save Individual Result Files

By default, the script only saves combined results. To also save individual Excel files for each scenario:

**Edit line 81 in `RunMINDSET_EmploymentOnly_BATCH.py`:**
```python
SAVE_INDIVIDUAL_RESULTS = True  # Change from False to True
```

**Output:** Creates `GLORIA_results/Individual_Results/` with 469 Excel files:
- `Results_Strategy_1004_BGR.xlsx`
- `Results_Strategy_1004_BLZ.xlsx`
- etc.

**Trade-off:** Slower (adds ~2 seconds per scenario), uses more disk space (~50 MB total)

---

## Expected Runtime

### Full Batch (469 scenarios)

**Conservative estimate:**
- MRIO loading: 2 minutes
- Processing: 469 scenarios × 5 seconds = 40 minutes
- Combining results: 1 minute
- **Total: ~45 minutes**

**Optimistic estimate (if your system is fast):**
- MRIO loading: 1 minute
- Processing: 469 scenarios × 3 seconds = 25 minutes
- Combining results: 0.5 minutes
- **Total: ~27 minutes**

### Partial Batch (Testing)

To test with fewer scenarios, edit the script (lines 72-77):

**Test with 3 strategies × 3 countries = 9 scenarios:**
```python
# Replace original lists with:
ISO = ["MEX", "MAR", "EGY"]  # Just 3 countries
strategy_id = [3010, 3011, 3012]  # Just 3 strategies
```

**Runtime: ~2 minutes total**

---

## Troubleshooting

### Issue 1: "File not found" for many scenarios

**Symptom:**
```
[1/469] Processing Strategy_1004_BGR...
    ✗ SKIPPED: File not found: Strategy_1004_BGR.xlsx
```

**Cause:** Scenario files are not in the expected location

**Solution:**
1. Check scenario files are in `GLORIA_template/Scenarios/`
2. Verify filename format: `Strategy_{ID}_{ISO}.xlsx` (exact match)
3. Check for typos in filenames

---

### Issue 2: "No investment data" errors

**Symptom:**
```
[5/469] Processing Strategy_1004_MEX...
    ✗ SKIPPED: No investment data in Strategy_1004_MEX
```

**Cause:** Scenario file exists but "Investment by" sheet is empty

**Solution:**
1. Open the scenario file in Excel
2. Check "Investment by" sheet has data starting at row 16
3. Verify columns: Country ISO*, Sector investing code*, Value*, Type*

---

### Issue 3: Script crashes with memory error

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Cause:** Running out of RAM (especially if many scenarios)

**Solution:**
1. Close other programs
2. Process in smaller batches:
   ```python
   # Edit lines 72-77 to process 100 scenarios at a time
   strategy_id = strategy_id[:15]  # First 15 strategies
   # Run, then change to:
   strategy_id = strategy_id[15:30]  # Next 15 strategies
   ```
3. Set `SAVE_INDIVIDUAL_RESULTS = False` to save memory

---

### Issue 4: One scenario fails, stops entire batch

**Good news:** The script is designed to continue even if one scenario fails!

**What happens:**
- Failed scenario is logged with status "FAILED"
- Script continues to next scenario
- All results are still combined at the end

**Check BATCH_SUMMARY.csv:**
```r
summary <- read.csv("GLORIA_results/BATCH_SUMMARY.csv")
summary %>% filter(Status == "FAILED")
```

---

## Parallel Processing (Advanced)

For faster processing on multi-core systems, use the parallel version (if needed, I can create this).

**Benefits:**
- 8 cores: ~45 min → ~6 minutes
- 16 cores: ~45 min → ~3 minutes

**Requirements:**
- Multi-core CPU
- Sufficient RAM (8+ GB recommended)
- `joblib` package installed

---

## Analysis Workflow

### Step 1: Load All Results

```r
library(dplyr)
library(ggplot2)

empl_region <- read.csv("GLORIA_results/ALL_RESULTS_Employment_by_Region.csv")
empl_sector <- read.csv("GLORIA_results/ALL_RESULTS_Employment_by_Sector.csv")
summary <- read.csv("GLORIA_results/BATCH_SUMMARY.csv")

# Check data loaded correctly
dim(empl_region)  # Should be many rows × 5 columns
dim(empl_sector)  # Should be many rows × 5 columns
dim(summary)       # Should be 469 rows × 9 columns
```

### Step 2: Quality Control

```r
# Check success rate
table(summary$Status)

# Identify failed scenarios
failed <- summary %>% filter(Status == "FAILED")
if(nrow(failed) > 0) {
  print("Failed scenarios:")
  print(failed)
}

# Check for missing data
summary %>%
  filter(Status == "SUCCESS") %>%
  summary()
```

### Step 3: Country-Level Analysis

```r
# Average multiplier by country
country_summary <- summary %>%
  filter(Status == "SUCCESS") %>%
  group_by(Country) %>%
  summarize(
    N_Strategies = n(),
    Avg_Multiplier = mean(Employment_Multiplier),
    SD_Multiplier = sd(Employment_Multiplier),
    Min_Multiplier = min(Employment_Multiplier),
    Max_Multiplier = max(Employment_Multiplier),
    Avg_Jobs = mean(Total_Jobs),
    Total_Investment = sum(Total_Investment)
  ) %>%
  arrange(desc(Avg_Multiplier))

print(country_summary)

# Visualize
ggplot(country_summary, aes(x = reorder(Country, Avg_Multiplier),
                            y = Avg_Multiplier)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  geom_errorbar(aes(ymin = Avg_Multiplier - SD_Multiplier,
                    ymax = Avg_Multiplier + SD_Multiplier),
                width = 0.2) +
  coord_flip() +
  labs(title = "Average Employment Multiplier by Country",
       x = "Country", y = "Jobs per $1M Investment") +
  theme_minimal()
```

### Step 4: Strategy-Level Analysis

```r
# Top 10 strategies overall
top_strategies <- summary %>%
  filter(Status == "SUCCESS") %>%
  group_by(Strategy) %>%
  summarize(
    N_Countries = n(),
    Avg_Multiplier = mean(Employment_Multiplier),
    Avg_Jobs = mean(Total_Jobs)
  ) %>%
  arrange(desc(Avg_Multiplier)) %>%
  head(10)

print(top_strategies)

# Compare strategy across countries
strategy_comparison <- summary %>%
  filter(Status == "SUCCESS", Strategy == 3010) %>%
  select(Country, Total_Jobs, Employment_Multiplier) %>%
  arrange(desc(Employment_Multiplier))

print(strategy_comparison)
```

### Step 5: Spillover Analysis

```r
# Calculate domestic vs. spillover jobs
spillover_analysis <- empl_region %>%
  mutate(Job_Location = ifelse(Investing_Country == Region_acronyms,
                                "Domestic", "Spillover")) %>%
  group_by(Strategy, Investing_Country, Job_Location) %>%
  summarize(Total_Jobs = sum(Jobs_Created)) %>%
  pivot_wider(names_from = Job_Location, values_from = Total_Jobs) %>%
  mutate(
    Spillover_Rate = Spillover / (Domestic + Spillover),
    Total = Domestic + Spillover
  )

# Average spillover rate by country
spillover_summary <- spillover_analysis %>%
  group_by(Investing_Country) %>%
  summarize(
    Avg_Spillover_Rate = mean(Spillover_Rate),
    Avg_Domestic_Jobs = mean(Domestic),
    Avg_Spillover_Jobs = mean(Spillover)
  )

print(spillover_summary)
```

### Step 6: Sectoral Analysis

```r
# Top sectors benefiting across all scenarios
top_sectors <- empl_sector %>%
  group_by(Sector_names) %>%
  summarize(Total_Jobs = sum(Jobs_Created)) %>%
  arrange(desc(Total_Jobs)) %>%
  head(20)

print(top_sectors)

# Visualize
ggplot(top_sectors, aes(x = reorder(Sector_names, Total_Jobs), y = Total_Jobs)) +
  geom_bar(stat = "identity", fill = "darkgreen") +
  coord_flip() +
  labs(title = "Top 20 Sectors by Total Job Creation",
       x = "Sector", y = "Total Jobs Created") +
  theme_minimal()
```

---

## Python Analysis Examples

### Load Results

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

empl_region = pd.read_csv("GLORIA_results/ALL_RESULTS_Employment_by_Region.csv")
empl_sector = pd.read_csv("GLORIA_results/ALL_RESULTS_Employment_by_Sector.csv")
summary = pd.read_csv("GLORIA_results/BATCH_SUMMARY.csv")
```

### Country Comparison

```python
# Average multiplier by country
country_stats = summary[summary['Status'] == 'SUCCESS'].groupby('Country').agg({
    'Employment_Multiplier': ['mean', 'std', 'min', 'max'],
    'Total_Jobs': 'mean'
}).round(2)

print(country_stats)

# Visualize
country_avg = summary[summary['Status'] == 'SUCCESS'].groupby('Country')['Employment_Multiplier'].mean()
country_avg.sort_values().plot(kind='barh', figsize=(10, 6), color='steelblue')
plt.xlabel('Jobs per $1M')
plt.title('Average Employment Multiplier by Country')
plt.tight_layout()
plt.savefig('multiplier_by_country.png')
```

### Strategy Ranking

```python
# Top 10 strategies overall
strategy_rank = summary[summary['Status'] == 'SUCCESS'].groupby('Strategy').agg({
    'Employment_Multiplier': 'mean',
    'Total_Jobs': 'mean',
    'Country': 'count'
}).rename(columns={'Country': 'N_Countries'}).sort_values('Employment_Multiplier', ascending=False).head(10)

print(strategy_rank)
```

### Spillover Analysis

```python
# Domestic vs. spillover jobs
empl_region['Job_Type'] = empl_region.apply(
    lambda x: 'Domestic' if x['Investing_Country'] == x['Region_acronyms'] else 'Spillover',
    axis=1
)

spillover = empl_region.groupby(['Strategy', 'Investing_Country', 'Job_Type'])['Jobs_Created'].sum().unstack(fill_value=0)
spillover['Spillover_Rate'] = spillover['Spillover'] / (spillover['Domestic'] + spillover['Spillover'])

print(spillover.head(10))
```

---

## Next Steps After Batch Processing

1. **Quality Control**
   - Check BATCH_SUMMARY.csv for failed scenarios
   - Investigate and fix any failures
   - Re-run failed scenarios individually if needed

2. **Exploratory Analysis**
   - Load combined results in R/Python
   - Calculate summary statistics
   - Create visualizations

3. **Statistical Analysis**
   - Compare multipliers across countries (ANOVA, t-tests)
   - Regression analysis: What predicts higher multipliers?
   - Cluster analysis: Group similar strategies

4. **Dissertation Writing**
   - Results section: Present key findings
   - Tables: Summary statistics by country/strategy
   - Figures: Multiplier comparisons, sectoral breakdowns
   - Discussion: Policy implications

---

## Support

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review BATCH_SUMMARY.csv for error patterns
3. Test with small batch (3 strategies × 3 countries) first
4. Check scenario file format and location

---

**Happy analyzing!**
