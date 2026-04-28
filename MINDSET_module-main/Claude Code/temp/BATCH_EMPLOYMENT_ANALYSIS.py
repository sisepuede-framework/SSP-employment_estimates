"""
BATCH EMPLOYMENT ANALYSIS - ALL 469 STRATEGY FILES

Processes all Strategy files and generates employment estimates using MINDSET methodology.

OUTPUT FILES:
1. employment_by_sector_country_strategy.csv - Detailed sector-level results
2. employment_by_country_strategy.csv - Country-level summary
3. employment_summary_consolidated.xlsx - Final dataset for analysis

Author: Claude Code
Date: 2026-03-22
"""

import sys
import os
import time
import numpy as np
import pandas as pd
from glob import glob

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("BATCH EMPLOYMENT ANALYSIS - ALL STRATEGY FILES")
print("="*80)
print()

# Import MINDSET modules
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.investment import invest
from SourceCode.InputOutput_SSP import IO
from SourceCode.employment import empl
from SourceCode.utils import MRIO_df_to_vec

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass
    def log(self, *args, **kwargs): pass

#==============================================================================
# STEP 1: Find all Strategy files
#==============================================================================
print("STEP 1: Finding all Strategy files")
print("-"*80)

scenario_pattern = "GLORIA_template/Scenarios/Strategy_*.xlsx"
scenario_files = sorted(glob(scenario_pattern))

print(f"Found {len(scenario_files)} Strategy files")
print()

if len(scenario_files) == 0:
    print("[ERROR] No Strategy files found!")
    print(f"  Looked in: {scenario_pattern}")
    sys.exit(1)

#==============================================================================
# STEP 2: Load MRIO Base Data (once)
#==============================================================================
print("STEP 2: Loading MRIO Base Data (one time)")
print("-"*80)

start_time = time.time()
MRIO_BASE = exog_vars()

print(f"[OK] MRIO data loaded in {time.time() - start_time:.1f} seconds")
print(f"  Countries: {', '.join(MRIO_BASE.COU_ID)}")
print(f"  Sectors: {len(MRIO_BASE.SEC_ID)}")
print()

# Calculate employment baseline from LABOR_BASE
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_low"] = empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"]
empl_base_df["vol_high"] = empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
empl_base_df["vol_total"] = empl_base_df["vol_low"] + empl_base_df["vol_high"]

empl_base = MRIO_df_to_vec(
    empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]],
    "REG_imp", "PROD_COMM", "vol_total",
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

# Initialize IO model (loads L_BASE, Y_BASE, G_BASE, calculates q_base)
print("Initializing IO model (loading L_BASE, Y_BASE, G_BASE)...")
IO_model = IO(MRIO_BASE)
IO_model.initialize()
print(f"[OK] q_base calculated: {IO_model.q_base.shape}")
print()

# Build employment model
print("Building employment model...")
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)
print(f"[OK] Employment multipliers calculated")
print()

#==============================================================================
# STEP 3: Process each Strategy file
#==============================================================================
print("STEP 3: Processing all Strategy files")
print("-"*80)
print()

# Storage for results
all_results_detailed = []  # Sector-level results
all_results_country = []   # Country-level summary
all_results_strategy = []  # Strategy-level summary

country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}
sector_list = MRIO_BASE.P['Lfd_Nr'].to_list()

errors = []
processed_count = 0
start_batch = time.time()

for idx, scenario_file in enumerate(scenario_files, 1):
    scenario_name = os.path.basename(scenario_file).replace('.xlsx', '')

    # Progress indicator
    if idx % 10 == 0 or idx == 1:
        elapsed = time.time() - start_batch
        rate = idx / elapsed if elapsed > 0 else 0
        remaining = (len(scenario_files) - idx) / rate if rate > 0 else 0
        print(f"[{idx}/{len(scenario_files)}] Processing {scenario_name} "
              f"(~{remaining/60:.1f} min remaining)")

    try:
        # Load scenario
        Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
        Scenario.set_exog_inv()

        total_investment = Scenario.inv_exog['dk'].sum()

        # Get investing country from scenario file
        investing_countries = Scenario.inv_exog[Scenario.inv_exog['dk'] > 0]['REG_imp'].unique()
        main_country = investing_countries[0] if len(investing_countries) > 0 else "UNKNOWN"

        # Investment module
        if not hasattr(Scenario, 'inv_spending'):
            Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

        INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
        INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
        INV_model.build_inv_output_elas()
        INV_model.calc_inv_share()
        INV_model.calc_dy_inv_exog(Scenario.inv_exog)

        # Convert to vector
        dy_inv_exog = MRIO_df_to_vec(
            INV_model.dy_inv_exog,
            'REG_imp', 'TRAD_COMM', 'dy',
            MRIO_BASE.R['Region_acronyms'].to_list(),
            MRIO_BASE.P['Lfd_Nr'].to_list()
        )

        # Calculate output changes
        dq_total = IO_model.calc_dq_exog(dy_inv_exog)

        # Calculate employment changes
        dempl = Empl_model.calc_dempl(dq_total)

        # Total employment
        total_jobs = dempl.sum()

        # Extract results by country and sector
        for country in MRIO_BASE.COU_ID:
            c_idx = country_idx[country]
            c_start = c_idx * 120
            c_end = c_start + 120

            country_investment = Scenario.inv_exog[Scenario.inv_exog['REG_imp'] == country]['dk'].sum()
            country_demand = dy_inv_exog[c_start:c_end].sum()
            country_output = dq_total[c_start:c_end].sum()
            country_jobs = dempl[c_start:c_end].sum()

            # Country-level summary
            all_results_country.append({
                'strategy': scenario_name,
                'main_country': main_country,
                'country': country,
                'investment_kUSD': country_investment,
                'demand_kUSD': country_demand,
                'output_kUSD': country_output,
                'jobs': country_jobs,
                'jobs_per_M_investment': (country_jobs / (country_investment / 1000)) if country_investment > 0 else 0,
                'jobs_per_M_output': (country_jobs / (country_output / 1000)) if country_output > 0 else 0
            })

            # Sector-level detail
            for s_idx, sector in enumerate(sector_list):
                idx_pos = c_start + s_idx
                sector_output = dq_total[idx_pos]
                sector_jobs = dempl[idx_pos]

                if abs(sector_output) > 0.01 or abs(sector_jobs) > 0.01:  # Only save non-zero
                    all_results_detailed.append({
                        'strategy': scenario_name,
                        'main_country': main_country,
                        'country': country,
                        'sector': sector,
                        'output_kUSD': sector_output,
                        'jobs': sector_jobs
                    })

        # Strategy-level summary
        all_results_strategy.append({
            'strategy': scenario_name,
            'main_country': main_country,
            'total_investment_kUSD': total_investment,
            'total_demand_kUSD': dy_inv_exog.sum(),
            'total_output_kUSD': dq_total.sum(),
            'total_jobs': total_jobs,
            'jobs_per_M_investment': (total_jobs / (total_investment / 1000)) if total_investment > 0 else 0,
            'output_multiplier': (dq_total.sum() / dy_inv_exog.sum()) if dy_inv_exog.sum() > 0 else 0
        })

        processed_count += 1

    except Exception as e:
        error_msg = f"{scenario_name}: {str(e)}"
        errors.append(error_msg)
        print(f"  [ERROR] {error_msg}")

print()
print("="*80)
print("PROCESSING COMPLETE")
print("="*80)
print(f"Successfully processed: {processed_count}/{len(scenario_files)}")
print(f"Errors: {len(errors)}")
print(f"Total time: {(time.time() - start_batch)/60:.1f} minutes")
print()

#==============================================================================
# STEP 4: Save Results
#==============================================================================
print("STEP 4: Saving Results")
print("-"*80)

output_dir = "Claude Code/temp/employment_results"
os.makedirs(output_dir, exist_ok=True)

# 1. Detailed sector-level results
if len(all_results_detailed) > 0:
    df_detailed = pd.DataFrame(all_results_detailed)
    output_file = f"{output_dir}/employment_by_sector_country_strategy.csv"
    df_detailed.to_csv(output_file, index=False)
    print(f"[OK] Saved detailed results: {output_file}")
    print(f"     Rows: {len(df_detailed):,}")

# 2. Country-level summary
if len(all_results_country) > 0:
    df_country = pd.DataFrame(all_results_country)
    output_file = f"{output_dir}/employment_by_country_strategy.csv"
    df_country.to_csv(output_file, index=False)
    print(f"[OK] Saved country summary: {output_file}")
    print(f"     Rows: {len(df_country):,}")

# 3. Strategy-level summary
if len(all_results_strategy) > 0:
    df_strategy = pd.DataFrame(all_results_strategy)
    output_file = f"{output_dir}/employment_by_strategy.csv"
    df_strategy.to_csv(output_file, index=False)
    print(f"[OK] Saved strategy summary: {output_file}")
    print(f"     Rows: {len(df_strategy):,}")

# 4. Consolidated Excel file with multiple sheets
if len(all_results_country) > 0:
    output_file = f"{output_dir}/employment_summary_consolidated.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Country-level (pivot: strategies × countries)
        pivot_country = df_country.pivot_table(
            index='strategy',
            columns='country',
            values='jobs',
            aggfunc='sum',
            fill_value=0
        )
        pivot_country['main_country'] = df_country.drop_duplicates('strategy').set_index('strategy')['main_country']
        pivot_country['TOTAL'] = pivot_country[MRIO_BASE.COU_ID].sum(axis=1)
        pivot_country.to_excel(writer, sheet_name='Jobs_by_Country')

        # Sheet 2: Strategy summary
        df_strategy.to_excel(writer, sheet_name='Strategy_Summary', index=False)

        # Sheet 3: Investment amounts
        pivot_inv = df_country.pivot_table(
            index='strategy',
            columns='country',
            values='investment_kUSD',
            aggfunc='sum',
            fill_value=0
        )
        pivot_inv.to_excel(writer, sheet_name='Investment_by_Country')

        # Sheet 4: Jobs per $M investment
        pivot_jobs_per_m = df_country[df_country['investment_kUSD'] > 0].pivot_table(
            index='strategy',
            columns='country',
            values='jobs_per_M_investment',
            aggfunc='mean',
            fill_value=0
        )
        pivot_jobs_per_m.to_excel(writer, sheet_name='Jobs_per_M_Investment')

    print(f"[OK] Saved consolidated Excel: {output_file}")
    print(f"     Sheets: Jobs_by_Country, Strategy_Summary, Investment_by_Country, Jobs_per_M_Investment")

print()

# 5. Error log
if len(errors) > 0:
    error_file = f"{output_dir}/processing_errors.txt"
    with open(error_file, 'w') as f:
        f.write("PROCESSING ERRORS\n")
        f.write("="*80 + "\n\n")
        for error in errors:
            f.write(f"{error}\n")
    print(f"[WARNING] Errors logged to: {error_file}")
    print()

#==============================================================================
# STEP 5: Summary Statistics
#==============================================================================
print("="*80)
print("SUMMARY STATISTICS")
print("="*80)
print()

if len(all_results_strategy) > 0:
    print("Jobs per $M Investment (across all strategies):")
    print(f"  Mean:   {df_strategy['jobs_per_M_investment'].mean():.1f}")
    print(f"  Median: {df_strategy['jobs_per_M_investment'].median():.1f}")
    print(f"  Min:    {df_strategy['jobs_per_M_investment'].min():.1f}")
    print(f"  Max:    {df_strategy['jobs_per_M_investment'].max():.1f}")
    print()

    print("By Main Country (average jobs per $M investment):")
    country_avg = df_strategy.groupby('main_country')['jobs_per_M_investment'].mean().sort_values(ascending=False)
    for country, avg_jobs in country_avg.items():
        count = len(df_strategy[df_strategy['main_country'] == country])
        print(f"  {country}: {avg_jobs:.1f} jobs/$M (n={count} strategies)")
    print()

print("="*80)
print("OUTPUT FILES READY FOR ANALYSIS")
print("="*80)
print()
print(f"Location: {output_dir}/")
print()
print("Files created:")
print("  1. employment_by_sector_country_strategy.csv - Detailed sector-level data")
print("  2. employment_by_country_strategy.csv - Country-level summary")
print("  3. employment_by_strategy.csv - Strategy-level summary")
print("  4. employment_summary_consolidated.xlsx - Final consolidated dataset")
print()
print("The consolidated Excel file contains:")
print("  - Jobs_by_Country: Matrix of strategies × countries")
print("  - Strategy_Summary: Overall statistics per strategy")
print("  - Investment_by_Country: Investment amounts by strategy and country")
print("  - Jobs_per_M_Investment: Employment multipliers by strategy and country")
print()
print("="*80)
