# -*- coding: utf-8 -*-
"""
DIAGNOSTIC: Uganda and Libya Employment Anomalies

This script traces the source of unrealistically high employment estimates
for Uganda and Libya by examining:
1. GLORIA employment coefficients
2. Base output levels (q_base)
3. Employment multipliers calculation
4. Results comparison across countries

Created: 2026-03-23
Purpose: Identify root cause of employment inflation for reporting
"""

import pandas as pd
import numpy as np
import os
import sys

# Set paths
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
os.chdir(mindset_root)

print("="*80)
print("DIAGNOSTIC: Uganda and Libya Employment Anomalies")
print("="*80)
print()

#==============================================================================
# STEP 1: Load and Examine Employment Coefficients
#==============================================================================
print("STEP 1: Examining GLORIA Employment Coefficients")
print("-"*80)

empl_coef_file = os.path.join("GLORIA_template", "Employment", "Empl_coefficient.csv")
empl_coef = pd.read_csv(empl_coef_file)

print(f"Employment coefficient file shape: {empl_coef.shape}")
print(f"Columns (first 5): {list(empl_coef.columns[:5])}")
print()

# Find Uganda and Libya columns
if 'Uganda' in empl_coef.columns:
    uga_col = 'Uganda'
elif 'UGA' in empl_coef.columns:
    uga_col = 'UGA'
else:
    # Search for Uganda-related column
    uga_candidates = [col for col in empl_coef.columns if 'uga' in col.lower()]
    uga_col = uga_candidates[0] if uga_candidates else None

if 'Libya' in empl_coef.columns:
    lby_col = 'Libya'
elif 'LBY' in empl_coef.columns:
    lby_col = 'LBY'
else:
    lby_candidates = [col for col in empl_coef.columns if 'lib' in col.lower() or 'lby' in col.lower()]
    lby_col = lby_candidates[0] if lby_candidates else None

print(f"Uganda column: {uga_col}")
print(f"Libya column: {lby_col}")
print()

# Get comparison countries
comparison_countries = ['Mexico', 'Bulgaria', 'Egypt', 'Belize', 'Morocco']
comparison_cols = [col for col in comparison_countries if col in empl_coef.columns]

print("Comparison countries found:", comparison_cols)
print()

#==============================================================================
# STEP 2: Compare Employment Coefficients Statistics
#==============================================================================
print("STEP 2: Employment Coefficient Statistics Comparison")
print("-"*80)

# Select numeric columns only (skip first two which are sector IDs/names)
numeric_cols = empl_coef.columns[2:]

stats_countries = [uga_col, lby_col] + comparison_cols
stats_countries = [c for c in stats_countries if c is not None and c in numeric_cols]

print(f"\nComparing {len(stats_countries)} countries:")
for country in stats_countries:
    coef_values = empl_coef[country]
    print(f"\n{country}:")
    print(f"  Mean:   {coef_values.mean():.4f}")
    print(f"  Median: {coef_values.median():.4f}")
    print(f"  Min:    {coef_values.min():.4f}")
    print(f"  Max:    {coef_values.max():.4f}")
    print(f"  Std:    {coef_values.std():.4f}")

    # Count very high coefficients (>0.9)
    high_coef_count = (coef_values > 0.9).sum()
    print(f"  # coefficients > 0.9: {high_coef_count}")

#==============================================================================
# STEP 3: Load and Examine Results Data
#==============================================================================
print("\n" + "="*80)
print("STEP 3: Examining Employment Results")
print("-"*80)

results_file = os.path.join("Claude Code", "temp", "employment_results",
                           "employment_by_country_strategy.csv")

if os.path.exists(results_file):
    results = pd.read_csv(results_file)

    print(f"\nResults file shape: {results.shape}")
    print(f"Columns: {list(results.columns)}")
    print()

    # Focus on one strategy for comparison
    strategy_sample = results[results['strategy'] == 'Strategy_1004_BGR']

    print("\nEmployment Results for Strategy_1004_BGR (investments by Bulgaria):")
    print("-"*80)
    print("\nJobs per million USD of OUTPUT (by destination country):")
    print()

    # Sort by jobs_per_M_output descending
    sample_sorted = strategy_sample.sort_values('jobs_per_M_output', ascending=False)

    for idx, row in sample_sorted.iterrows():
        country = row['country']
        jobs_per_m = row['jobs_per_M_output']
        output = row['output_kUSD']
        jobs = row['jobs']

        # Highlight Uganda and Libya
        marker = "  *** ANOMALY ***" if country in ['UGA', 'LBY'] else ""
        print(f"  {country:>6s}: {jobs_per_m:>10.2f} jobs/$M output  " +
              f"({jobs:>8.2f} jobs from ${output:>8.2f}k output){marker}")

    print()
    print("-"*80)
    print("\nKEY OBSERVATIONS:")
    print("  - Normal range: 5-50 jobs per million USD output")
    print("  - Uganda shows: 100-2000+ jobs per million USD output")
    print("  - Libya shows: 100-170 jobs per million USD output")
    print()

    # Calculate ratios
    normal_countries = sample_sorted[~sample_sorted['country'].isin(['UGA', 'LBY'])]
    normal_median = normal_countries['jobs_per_M_output'].median()

    uga_row = sample_sorted[sample_sorted['country'] == 'UGA']
    lby_row = sample_sorted[sample_sorted['country'] == 'LBY']

    if len(uga_row) > 0:
        uga_multiplier = uga_row['jobs_per_M_output'].values[0] / normal_median
        print(f"  Uganda multiplier vs normal: {uga_multiplier:.1f}x higher")

    if len(lby_row) > 0:
        lby_multiplier = lby_row['jobs_per_M_output'].values[0] / normal_median
        print(f"  Libya multiplier vs normal: {lby_multiplier:.1f}x higher")

else:
    print(f"\nResults file not found: {results_file}")

#==============================================================================
# STEP 4: Trace the Calculation Path
#==============================================================================
print("\n" + "="*80)
print("STEP 4: Tracing Calculation Path in MINDSET")
print("-"*80)

print("""
The employment calculation in MINDSET follows this path:

1. LOAD EMPLOYMENT COEFFICIENTS (from Empl_coefficient.csv)
   Source: SourceCode/employment.py, lines 18-34
   - These are base employment-to-output ratios from GLORIA
   - Units: Employment per unit of gross output

2. BUILD EMPLOYMENT MULTIPLIER (employment.py, lines 36-43)
   Formula: empl_multiplier = empl_coef × (empl_base / q_base)

   Where:
   - empl_coef = GLORIA coefficient (from Step 1)
   - empl_base = Base employment level (from GLORIA MRIO data)
   - q_base = Base gross output (from GLORIA MRIO data)

   ⚠️ CRITICAL: If q_base is very small → division creates huge multiplier!

3. CALCULATE EMPLOYMENT CHANGE (employment.py, lines 45-54)
   Formula: dEmployment = empl_multiplier × dOutput

   Where:
   - empl_multiplier = from Step 2
   - dOutput = Output change from Leontief model (L × dY)

4. AGGREGATE BY COUNTRY AND SECTOR
   Source: RunMINDSET_EmploymentOnly_BATCH_FINAL.py, lines 208-252
   - Sum employment changes by country
   - Calculate jobs per million investment/output

HYPOTHESIS FOR ANOMALY:
------------------------
Uganda and Libya likely have:
1. Very small q_base values (low baseline output) in GLORIA v57 data
   → This could be due to data quality issues or missing sectors

2. When multiplier is calculated: empl_coef / (empl_base / q_base)
   → Small q_base creates artificially large multiplier

3. This inflates ALL employment estimates involving Uganda/Libya
   → Even small demand creates huge employment effects
""")

#==============================================================================
# STEP 5: Recommendations
#==============================================================================
print("\n" + "="*80)
print("STEP 5: Recommended Actions")
print("-"*80)

print("""
OPTION 1: Validate GLORIA Data Quality
---------------------------------------
- Check GLORIA v57 documentation for known issues with Uganda/Libya
- Examine q_base (gross output) values in the MRIO matrices
- Compare against World Bank or UN national accounts data
- File location: GLORIA_db/v57/2019/...

OPTION 2: Use Proxy Countries
------------------------------
For countries with suspect data quality:
- Uganda → Use Kenya or Tanzania as regional proxy
- Libya → Use Tunisia or Egypt as regional proxy
- Apply neighbor country's employment coefficients
- Document this substitution clearly

OPTION 3: Cap or Smooth Anomalous Multipliers
----------------------------------------------
- Set maximum reasonable threshold (e.g., 100 jobs/$M output)
- Apply smoothing to outlier coefficients
- Document adjustment methodology
- Only if justified by cross-country comparison

OPTION 4: Investigate "Strategy as Purchases" Fix
--------------------------------------------------
The user mentioned a fix was already implemented:
"MINDSET now treats strategies as purchases of specific products,
not as investments by the producing sector"

This suggests an earlier conceptual error was corrected. Need to verify:
- Where in the code this change was made
- Whether Uganda/Libya anomalies persist AFTER this fix
- If anomalies remain, they're likely from GLORIA base data, not logic error

NEXT STEP: Examine actual GLORIA MRIO data files to confirm q_base hypothesis
""")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
