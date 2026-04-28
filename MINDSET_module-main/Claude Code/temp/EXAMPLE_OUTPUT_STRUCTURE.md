# BATCH EMPLOYMENT ANALYSIS - OUTPUT STRUCTURE EXAMPLE

This document shows the structure of outputs that will be generated from processing all 469 Strategy files.

## OUTPUT FILES

The batch processing will create 4 files in `Claude Code/temp/employment_results/`:

1. **employment_by_sector_country_strategy.csv** - Detailed sector-level results
2. **employment_by_country_strategy.csv** - Country-level summary
3. **employment_by_strategy.csv** - Strategy-level summary
4. **employment_summary_consolidated.xlsx** - Final consolidated dataset (Excel with multiple sheets)

---

## FILE 1: employment_by_sector_country_strategy.csv

**Purpose:** Most detailed view - shows employment by sector within each country for each strategy

**Columns:**
- strategy: Strategy file name (e.g., "Strategy_1004_MEX")
- main_country: Country making the investment
- country: Country where employment occurs
- sector: GLORIA product code (1-120)
- output_kUSD: Output change in this sector (thousands USD)
- jobs: Employment change in this sector

**Example rows (from Strategy_1004_MEX and Strategy_1004_EGY):**

```
strategy,main_country,country,sector,output_kUSD,jobs
Strategy_1004_MEX,MEX,MEX,86,45.23,0.18
Strategy_1004_MEX,MEX,MEX,89,89.45,0.52
Strategy_1004_MEX,MEX,MEX,90,31.87,0.15
Strategy_1004_MEX,MEX,MEX,91,37.70,0.16
Strategy_1004_MEX,MEX,ROW,1,125.67,1.89
Strategy_1004_MEX,MEX,ROW,65,89.23,2.34
Strategy_1004_MEX,MEX,ROW,89,245.78,8.92
Strategy_1004_EGY,EGY,EGY,86,78.34,3.45
Strategy_1004_EGY,EGY,EGY,89,156.89,12.67
Strategy_1004_EGY,EGY,EGY,90,98.45,4.23
Strategy_1004_EGY,EGY,ROW,1,234.56,3.45
Strategy_1004_EGY,EGY,ROW,65,178.90,4.78
Strategy_1004_EGY,EGY,MAR,90,5.67,1.89
```

**Expected size:** ~50,000-100,000 rows
- 469 strategies × 8 countries × ~15-30 sectors with non-zero values per country

**Use case:**
- Analyze which sectors generate most jobs in each country
- Identify sectoral employment patterns across strategies
- Track supply chain effects across countries and sectors

---

## FILE 2: employment_by_country_strategy.csv

**Purpose:** Country-level summary - aggregates all sectors within each country

**Columns:**
- strategy: Strategy file name
- main_country: Country making the investment
- country: Country where employment occurs
- investment_kUSD: Direct investment in this country (thousands USD)
- demand_kUSD: Final demand generated in this country (thousands USD)
- output_kUSD: Total output change in this country (thousands USD)
- jobs: Total jobs created in this country
- jobs_per_M_investment: Jobs per million USD of investment in this country
- jobs_per_M_output: Jobs per million USD of output in this country

**Example rows:**

```
strategy,main_country,country,investment_kUSD,demand_kUSD,output_kUSD,jobs,jobs_per_M_investment,jobs_per_M_output
Strategy_1004_MEX,MEX,MEX,1000.0,135.23,204.25,1.01,1.01,4.94
Strategy_1004_MEX,MEX,ROW,0.0,840.36,2027.20,33.80,40.22,16.68
Strategy_1004_MEX,MEX,BGR,0.0,2.21,3.61,0.07,30.32,19.39
Strategy_1004_MEX,MEX,EGY,0.0,0.64,1.59,0.15,228.86,94.34
Strategy_1004_MEX,MEX,MAR,0.0,0.60,2.18,0.05,80.60,22.94
Strategy_1004_EGY,EGY,EGY,1000.0,323.65,471.49,20.93,64.66,44.39
Strategy_1004_EGY,EGY,ROW,0.0,652.45,1688.00,28.72,44.02,17.01
Strategy_1004_EGY,EGY,BGR,0.0,9.93,13.58,0.10,9.73,7.36
Strategy_1004_EGY,EGY,LBY,0.0,3.69,5.33,0.67,182.86,125.70
Strategy_1004_EGY,EGY,MAR,0.0,8.19,9.96,2.54,310.51,255.02
Strategy_1004_EGY,EGY,MEX,0.0,2.05,7.32,0.07,32.76,9.56
```

**Expected size:** ~3,752 rows
- 469 strategies × 8 countries = 3,752 rows

**Use case:**
- Compare employment impacts across countries for each strategy
- Identify spillover effects (jobs created outside investing country)
- Calculate country-specific employment multipliers

---

## FILE 3: employment_by_strategy.csv

**Purpose:** Strategy-level summary - overall statistics per strategy

**Columns:**
- strategy: Strategy file name
- main_country: Country making the investment
- total_investment_kUSD: Total investment across all countries (thousands USD)
- total_demand_kUSD: Total final demand generated (thousands USD)
- total_output_kUSD: Total output change across all countries (thousands USD)
- total_jobs: Total jobs created globally
- jobs_per_M_investment: Global jobs per million USD invested
- output_multiplier: Total output / Total demand ratio

**Example rows:**

```
strategy,main_country,total_investment_kUSD,total_demand_kUSD,total_output_kUSD,total_jobs,jobs_per_M_investment,output_multiplier
Strategy_1004_MEX,MEX,1000.0,979.04,2240.14,35.08,35.08,2.29
Strategy_1004_EGY,EGY,1000.0,999.91,2196.28,53.03,53.03,2.20
Strategy_1005_MEX,MEX,1500.0,1468.56,3360.21,52.62,35.08,2.29
Strategy_1005_EGY,EGY,1500.0,1499.87,3294.42,79.55,53.03,2.20
Strategy_1006_BGR,BGR,800.0,785.20,1856.34,28.45,35.56,2.36
Strategy_1007_MAR,MAR,1200.0,1175.34,2845.67,89.34,74.45,2.42
```

**Expected size:** 469 rows
- One row per strategy

**Use case:**
- Compare strategies by overall employment impact
- Identify most job-intensive strategies
- Compare output multipliers across strategies
- Analyze by main_country to see country-level patterns

---

## FILE 4: employment_summary_consolidated.xlsx

**Purpose:** Final consolidated dataset with multiple sheets for easy analysis

### Sheet 1: Jobs_by_Country

**Structure:** Pivot table with strategies as rows, countries as columns

```
                        ROW    BGR   BLZ   EGY   LBY   MAR   MEX   UGA  main_country  TOTAL
Strategy_1004_MEX     33.80  0.07  0.00  0.15  0.00  0.05  1.01  0.00  MEX           35.08
Strategy_1004_EGY     28.72  0.10  0.00  20.93 0.67  2.54  0.07  0.00  EGY           53.03
Strategy_1005_MEX     50.70  0.11  0.00  0.23  0.00  0.08  1.52  0.00  MEX           52.64
Strategy_1005_EGY     43.08  0.15  0.00  31.40 1.01  3.81  0.11  0.00  EGY           79.56
Strategy_1006_BGR     22.56  4.67  0.00  0.12  0.00  0.04  0.09  0.00  BGR           27.48
```

**Use case:**
- Quickly see employment distribution across countries for each strategy
- Compare total job creation across strategies
- Identify which country benefits most from each strategy

---

### Sheet 2: Strategy_Summary

**Structure:** Same as employment_by_strategy.csv but in Excel format

```
strategy          main_country  total_investment_kUSD  total_demand_kUSD  total_output_kUSD  total_jobs  jobs_per_M_investment  output_multiplier
Strategy_1004_MEX MEX          1000.0                 979.04             2240.14            35.08       35.08                  2.29
Strategy_1004_EGY EGY          1000.0                 999.91             2196.28            53.03       53.03                  2.20
Strategy_1005_MEX MEX          1500.0                 1468.56            3360.21            52.62       35.08                  2.29
```

**Use case:**
- Overall strategy comparison
- Summary statistics
- Main country analysis

---

### Sheet 3: Investment_by_Country

**Structure:** Pivot table showing investment amounts by strategy and country

```
                        ROW    BGR   BLZ     EGY   LBY    MAR     MEX   UGA
Strategy_1004_MEX        0      0     0       0     0      0    1000.0    0
Strategy_1004_EGY        0      0     0    1000.0   0      0       0      0
Strategy_1005_MEX        0      0     0       0     0      0    1500.0    0
Strategy_1005_EGY        0      0     0    1500.0   0      0       0      0
Strategy_1006_BGR        0    800.0   0       0     0      0       0      0
```

**Use case:**
- See which countries receive direct investment in each strategy
- Verify investment patterns
- Cross-reference with job creation

---

### Sheet 4: Jobs_per_M_Investment

**Structure:** Pivot table showing employment multipliers (jobs per million USD investment) by strategy and country

```
                        ROW    BGR   BLZ    EGY    LBY    MAR    MEX   UGA
Strategy_1004_MEX     40.22  30.32  0.00  228.86  0.00  80.60   1.01  0.00
Strategy_1004_EGY     44.02   9.73  0.00   64.66 182.86 310.51  32.76  0.00
Strategy_1005_MEX     40.22  30.32  0.00  228.86  0.00  80.60   1.01  0.00
Strategy_1005_EGY     44.02   9.73  0.00   64.66 182.86 310.51  32.76  0.00
```

**Use case:**
- Compare employment intensity across countries
- Identify which countries have highest job creation per dollar invested
- Analyze country-specific multipliers

---

## KEY INSIGHTS FROM STRUCTURE

1. **Multi-level analysis:** Can analyze at sector level (File 1), country level (File 2), or strategy level (File 3)

2. **Supply chain effects visible:** Investment in one country creates jobs in others (visible in country-level data)

3. **Employment multipliers:** Both direct (in investing country) and indirect (in supply chain countries)

4. **Product-specific effects:** Sector-level data shows which products drive employment

5. **Country comparisons:** Easy to compare employment impacts across strategies and countries

6. **Excel pivot tables:** Quick analysis and visualization in Sheet format

---

## EXAMPLE ANALYSIS QUESTIONS THIS DATASET CAN ANSWER

1. Which strategy creates the most jobs globally?
2. Which country benefits most from investments in Egypt?
3. Which sectors are most labor-intensive in Mexico?
4. What's the average employment multiplier for infrastructure investments?
5. How do jobs created locally compare to jobs created in supply chain?
6. Which countries have highest indirect employment effects?
7. What's the relationship between output multiplier and employment multiplier?
8. Which products generate most employment per dollar invested?

---

## DATA QUALITY CHECKS

The script includes automatic validation:
- Investment preservation check (demand ≈ investment)
- Output multiplier range check (typically 1.5-3.0x)
- Employment multiplier plausibility (5-50 jobs per $M for most strategies)
- Error logging for any failed strategies
- Summary statistics by main_country

---

## NEXT STEPS

After reviewing this structure, the batch processing script will:
1. Load MRIO data once (optimize performance)
2. Process all 469 Strategy files (~30-60 minutes estimated)
3. Generate all 4 output files
4. Provide summary statistics
5. Flag any anomalies or errors

The final consolidated.xlsx file will be ready for direct use in your dissertation analysis.
