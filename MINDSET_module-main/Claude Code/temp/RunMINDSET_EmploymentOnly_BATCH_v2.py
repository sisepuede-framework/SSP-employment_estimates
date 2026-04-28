# -*- coding: utf-8 -*-
"""
MINDSET EMPLOYMENT-ONLY ESTIMATION - BATCH PROCESSING VERSION v2

UPDATES in v2:
- Added Direct, Indirect, and Total Jobs separation
- Added Country_Name column
- Enhanced all output files with new columns

Created: 2026-03-20
Purpose: Batch processing for 67 strategies × 7 countries = 469 scenarios
Based on: RunMINDSET_EmploymentOnly_BATCH.py
"""

#==============================================================================
# I. Import Required Modules
#==============================================================================

import numpy as np
import pandas as pd
import time
import sys
import os
import gc  # Garbage collection for memory management

#------------------------------------------------------------------------------
# PATH SETUP
#------------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)

os.chdir(mindset_root)

print(f"MINDSET root directory: {mindset_root}")
print(f"Current working directory: {os.getcwd()}\n")

#------------------------------------------------------------------------------
# MINDSET Modules
#------------------------------------------------------------------------------
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.InputOutput import IO
from SourceCode.employment import empl
from SourceCode.investment import invest
from SourceCode.results import results
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("\n" + "="*80)
print("MINDSET EMPLOYMENT-ONLY ESTIMATION - BATCH PROCESSING v2")
print("="*80 + "\n")

#==============================================================================
# II. Configuration - Define All Scenarios
#==============================================================================

# Countries (7 total)
ISO = ["BGR", "BLZ", "EGY", "LBY", "MAR", "MEX", "UGA"]

# Strategies (67 total)
strategy_id = [
    1004, 1005, 1006, 1007, 3001, 3002, 3059, 3060, 3061, 3062,
    3003, 3005, 3006, 3009, 3010, 3011, 3012, 1010, 3015, 3016,
    3017, 3018, 3019, 3020, 3021, 3022, 1011, 1013, 1015, 1016,
    1017, 1018, 1019, 1020, 1024, 1026, 4002, 4003, 4004, 4005,
    4006, 4007, 3025, 3026, 3027, 3028, 3029, 3030, 3035, 3036,
    3039, 3040, 3041, 3042, 3043, 3044, 2002, 2003, 2005, 2006,
    2007, 2009, 2011, 2012, 2013, 2014, 2015
]

# Configuration
SCENARIOS_FOLDER = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios")
SAVE_INDIVIDUAL_RESULTS = False  # Set to True to save individual Excel files for each scenario

# Create all scenario combinations
total_scenarios = len(strategy_id) * len(ISO)
print(f"Configuration:")
print(f"  Strategies: {len(strategy_id)}")
print(f"  Countries: {len(ISO)}")
print(f"  Total scenarios to process: {total_scenarios}")
print(f"  Scenarios folder: {SCENARIOS_FOLDER}")
print(f"  Save individual results: {SAVE_INDIVIDUAL_RESULTS}")
print()

#==============================================================================
# III. Core Function - Run Single Scenario
#==============================================================================

def run_single_scenario(strategy, country, MRIO_BASE, Scenario_Log):
    """
    Run employment estimation for a single strategy-country combination.

    NEW IN V2: Separates Direct, Indirect, and Total jobs

    Parameters:
    -----------
    strategy : int
        Strategy ID number
    country : str
        Country ISO code
    MRIO_BASE : exog_vars object
        Pre-loaded MRIO database (passed in to avoid reloading)
    Scenario_Log : object
        Logging object

    Returns:
    --------
    dict : Results dictionary with key metrics, or None if failed
    """

    scenario_name = f"Strategy_{strategy}_{country}"
    scenario_file = os.path.join(SCENARIOS_FOLDER, f"{scenario_name}.xlsx")

    # Check if scenario file exists
    if not os.path.exists(scenario_file):
        print(f"    ✗ SKIPPED: File not found: {scenario_name}.xlsx")
        return None

    try:
        # Load scenario
        Scenario = scenario(MRIO_BASE, scenario_file, Scenario_Log)
        Scenario.set_exog_inv()

        # Check if scenario has investment data
        if not hasattr(Scenario, 'inv_exog') or Scenario.inv_exog.empty:
            print(f"    ✗ SKIPPED: No investment data in {scenario_name}")
            return None

        total_investment = Scenario.inv_exog['dk'].sum()

        # NEW: Store which sectors have DIRECT investment
        # These are the (region, sector) pairs that receive investment directly
        direct_investment_sectors = Scenario.inv_exog[['REG_imp', 'PROD_COMM']].copy()
        direct_investment_sectors['has_direct_investment'] = True

        # Initialize investment module
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
        IO_model = IO(MRIO_BASE)
        IO_model.build_L_mat()
        dq_exog_fd = IO_model.calc_dq_exog(dy_inv_exog)
        dq_total = dq_exog_fd.copy()

        # Calculate employment changes
        Empl_model = empl(MRIO_BASE)
        Empl_model.build_empl_coef()
        dempl_exog_fd = Empl_model.calc_dempl([dq_exog_fd])[0]
        dempl_total = dempl_exog_fd.copy()

        # Build results DataFrames
        empl_change = pd.concat([
            MRIO_BASE.mrio_list,
            pd.DataFrame(dempl_total, columns=["Jobs_Created"])
        ], axis=1)

        # NEW: Tag employment as Direct or Indirect
        # Merge with direct investment flags
        empl_change_tagged = empl_change.merge(
            direct_investment_sectors,
            left_on=['Reg_ID', 'Sec_ID'],
            right_on=['REG_imp', 'PROD_COMM'],
            how='left'
        )
        empl_change_tagged['has_direct_investment'] = empl_change_tagged['has_direct_investment'].fillna(False)

        # Separate direct and indirect jobs
        empl_change_tagged['Direct_Jobs'] = empl_change_tagged.apply(
            lambda row: row['Jobs_Created'] if row['has_direct_investment'] else 0, axis=1
        )
        empl_change_tagged['Indirect_Jobs'] = empl_change_tagged.apply(
            lambda row: 0 if row['has_direct_investment'] else row['Jobs_Created'], axis=1
        )
        empl_change_tagged['Total_Jobs'] = empl_change_tagged['Jobs_Created']

        # Calculate summary statistics
        total_jobs = dempl_total.sum()
        direct_jobs = empl_change_tagged['Direct_Jobs'].sum()
        indirect_jobs = empl_change_tagged['Indirect_Jobs'].sum()
        employment_multiplier = total_jobs / total_investment * 1e6
        output_multiplier = dq_total.sum() / dy_inv_exog.sum()

        # Get country name
        country_name = MRIO_BASE.R[MRIO_BASE.R['Region_acronyms'] == country]['Region_names'].values
        country_name = country_name[0] if len(country_name) > 0 else country

        # Employment by region (with Direct/Indirect breakdown)
        empl_by_region = empl_change_tagged.groupby('Reg_ID').agg({
            'Direct_Jobs': 'sum',
            'Indirect_Jobs': 'sum',
            'Total_Jobs': 'sum'
        }).reset_index()

        empl_by_region = empl_by_region.merge(
            MRIO_BASE.R[['Region_acronyms', 'Region_names']],
            left_on='Reg_ID',
            right_on='Region_acronyms',
            how='left'
        )

        empl_by_region = empl_by_region[[
            'Region_acronyms', 'Region_names',
            'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs'
        ]]
        empl_by_region['Strategy'] = strategy
        empl_by_region['Investing_Country'] = country
        empl_by_region['Investing_Country_Name'] = country_name

        # Employment by sector (with Direct/Indirect breakdown)
        empl_by_sector = empl_change_tagged.groupby('Sec_ID').agg({
            'Direct_Jobs': 'sum',
            'Indirect_Jobs': 'sum',
            'Total_Jobs': 'sum'
        }).reset_index()

        empl_by_sector = empl_by_sector.merge(
            MRIO_BASE.P[['Lfd_Nr', 'Sector_names']],
            left_on='Sec_ID',
            right_on='Lfd_Nr',
            how='left'
        )

        empl_by_sector = empl_by_sector[[
            'Lfd_Nr', 'Sector_names',
            'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs'
        ]]
        empl_by_sector['Strategy'] = strategy
        empl_by_sector['Investing_Country'] = country
        empl_by_sector['Investing_Country_Name'] = country_name

        # Optional: Save individual results
        if SAVE_INDIVIDUAL_RESULTS:
            output_dir = os.path.join(os.getcwd(), "GLORIA_results", "Individual_Results")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"Results_{scenario_name}.xlsx")

            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                empl_by_region.to_excel(writer, sheet_name='Employment_by_Region', index=False)
                empl_by_sector.to_excel(writer, sheet_name='Employment_by_Sector', index=False)

        # Return results dictionary
        results_dict = {
            'strategy': strategy,
            'country': country,
            'country_name': country_name,
            'scenario_name': scenario_name,
            'total_investment': total_investment,
            'direct_jobs': direct_jobs,
            'indirect_jobs': indirect_jobs,
            'total_jobs': total_jobs,
            'employment_multiplier': employment_multiplier,
            'output_multiplier': output_multiplier,
            'empl_by_region': empl_by_region,
            'empl_by_sector': empl_by_sector,
            'status': 'SUCCESS'
        }

        # Clean up
        del Scenario, INV_CONV, INV_model, IO_model, Empl_model
        del dy_inv_exog, dq_exog_fd, dq_total, dempl_exog_fd, dempl_total
        del empl_change, empl_change_tagged, direct_investment_sectors
        gc.collect()

        return results_dict

    except Exception as e:
        print(f"    ✗ ERROR in {scenario_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'strategy': strategy,
            'country': country,
            'scenario_name': scenario_name,
            'status': 'FAILED',
            'error': str(e)
        }

#==============================================================================
# IV. Main Batch Processing Loop
#==============================================================================

print("="*80)
print("STEP 1: Loading MRIO Data (one-time)")
print("="*80)

# Load MRIO data once (reuse for all scenarios)
step_time = time.time()
MRIO_BASE = exog_vars()
print(f"✓ MRIO data loaded")
print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

# Initialize logging
from SourceCode.log import log as _log
Scenario_Log = _log("EmploymentOnly_Batch_v2")

print("="*80)
print("STEP 2: Processing All Scenarios")
print("="*80)
print()

# Storage for all results
all_results = []
all_empl_by_region = []
all_empl_by_sector = []
batch_summary = []

# Start batch timer
batch_start_time = time.time()

# Process each scenario
scenario_count = 0
success_count = 0
failed_count = 0
skipped_count = 0

for strategy in strategy_id:
    for country in ISO:
        scenario_count += 1

        print(f"[{scenario_count}/{total_scenarios}] Processing Strategy_{strategy}_{country}...")

        scenario_start_time = time.time()

        # Run scenario
        result = run_single_scenario(strategy, country, MRIO_BASE, Scenario_Log)

        scenario_runtime = time.time() - scenario_start_time

        if result is None:
            # Skipped (file not found)
            skipped_count += 1
            batch_summary.append({
                'Scenario_Number': scenario_count,
                'Strategy': strategy,
                'Country': country,
                'Country_Name': '',
                'Status': 'SKIPPED',
                'Runtime_Seconds': scenario_runtime
            })

        elif result['status'] == 'FAILED':
            # Failed with error
            failed_count += 1
            batch_summary.append({
                'Scenario_Number': scenario_count,
                'Strategy': strategy,
                'Country': country,
                'Country_Name': result.get('country_name', ''),
                'Status': 'FAILED',
                'Error': result['error'],
                'Runtime_Seconds': scenario_runtime
            })

        else:
            # Success
            success_count += 1
            print(f"    ✓ SUCCESS: {result['total_jobs']:,.0f} jobs " +
                  f"(Direct: {result['direct_jobs']:,.0f}, Indirect: {result['indirect_jobs']:,.0f}), " +
                  f"Multiplier: {result['employment_multiplier']:.2f} jobs/$1M, " +
                  f"Time: {scenario_runtime:.1f}s")

            # Store results
            all_empl_by_region.append(result['empl_by_region'])
            all_empl_by_sector.append(result['empl_by_sector'])

            batch_summary.append({
                'Scenario_Number': scenario_count,
                'Strategy': strategy,
                'Country': country,
                'Country_Name': result['country_name'],
                'Status': 'SUCCESS',
                'Total_Investment': result['total_investment'],
                'Direct_Jobs': result['direct_jobs'],
                'Indirect_Jobs': result['indirect_jobs'],
                'Total_Jobs': result['total_jobs'],
                'Employment_Multiplier': result['employment_multiplier'],
                'Output_Multiplier': result['output_multiplier'],
                'Runtime_Seconds': scenario_runtime
            })

        print()

batch_total_time = time.time() - batch_start_time

#==============================================================================
# V. Combine and Save Results
#==============================================================================

print("="*80)
print("STEP 3: Combining and Saving Results")
print("="*80)
print()

output_dir = os.path.join(os.getcwd(), "GLORIA_results")
os.makedirs(output_dir, exist_ok=True)

# Combine employment by region
if all_empl_by_region:
    combined_empl_by_region = pd.concat(all_empl_by_region, ignore_index=True)
    output_file_region = os.path.join(output_dir, "ALL_RESULTS_Employment_by_Region_v2.csv")
    combined_empl_by_region.to_csv(output_file_region, index=False)
    print(f"✓ Saved: ALL_RESULTS_Employment_by_Region_v2.csv")
    print(f"  Rows: {len(combined_empl_by_region):,}")
    print(f"  Columns: {list(combined_empl_by_region.columns)}")
    print()

# Combine employment by sector
if all_empl_by_sector:
    combined_empl_by_sector = pd.concat(all_empl_by_sector, ignore_index=True)
    output_file_sector = os.path.join(output_dir, "ALL_RESULTS_Employment_by_Sector_v2.csv")
    combined_empl_by_sector.to_csv(output_file_sector, index=False)
    print(f"✓ Saved: ALL_RESULTS_Employment_by_Sector_v2.csv")
    print(f"  Rows: {len(combined_empl_by_sector):,}")
    print(f"  Columns: {list(combined_empl_by_sector.columns)}")
    print()

# Save batch summary
batch_summary_df = pd.DataFrame(batch_summary)
output_file_summary = os.path.join(output_dir, "BATCH_SUMMARY_v2.csv")
batch_summary_df.to_csv(output_file_summary, index=False)
print(f"✓ Saved: BATCH_SUMMARY_v2.csv")
print(f"  Rows: {len(batch_summary_df):,}")
print()

#==============================================================================
# VI. Final Summary
#==============================================================================

print("="*80)
print("BATCH PROCESSING COMPLETE")
print("="*80)
print()
print(f"Total scenarios attempted: {total_scenarios}")
print(f"  ✓ Successful: {success_count}")
print(f"  ✗ Failed: {failed_count}")
print(f"  ⊘ Skipped: {skipped_count}")
print()
print(f"Total runtime: {batch_total_time/60:.1f} minutes ({batch_total_time:.0f} seconds)")
print(f"Average time per scenario: {batch_total_time/scenario_count:.1f} seconds")
print()
print("Output files created:")
print(f"  1. ALL_RESULTS_Employment_by_Region_v2.csv")
print(f"  2. ALL_RESULTS_Employment_by_Sector_v2.csv")
print(f"  3. BATCH_SUMMARY_v2.csv")
if SAVE_INDIVIDUAL_RESULTS:
    print(f"  4. Individual_Results/ folder with {success_count} Excel files")
print()

# Show sample results
if success_count > 0:
    print("="*80)
    print("SAMPLE RESULTS (First 5 successful scenarios)")
    print("="*80)
    print()
    successful_summaries = batch_summary_df[batch_summary_df['Status'] == 'SUCCESS'].head(5)
    print(successful_summaries[[
        'Strategy', 'Country', 'Country_Name',
        'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs', 'Employment_Multiplier'
    ]].to_string(index=False))
    print()

print("="*80)
print("Ready for analysis!")
print("="*80)
print()
