# -*- coding: utf-8 -*-
"""
MINDSET EMPLOYMENT-ONLY ESTIMATION - BATCH PROCESSING (FINAL VERSION)

Based on original MINDSET methodology for separating Direct vs Indirect employment effects.

Direct Employment = Employment from initial final demand (first-round effect)
Indirect Employment = Employment from supply chain multiplier (Leontief effect)

Total Employment = Direct + Indirect

Created: 2026-03-20
Grounded in: MINDSET original documentation and RunMINDSET.py
"""

#==============================================================================
# I. Import Required Modules
#==============================================================================

import numpy as np
import pandas as pd
import time
import sys
import os
import gc

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
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("\n" + "="*80)
print("MINDSET EMPLOYMENT-ONLY BATCH PROCESSING")
print("Direct vs Indirect Employment Separation")
print("="*80 + "\n")

#==============================================================================
# II. Configuration
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

SCENARIOS_FOLDER = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios")
SAVE_INDIVIDUAL_RESULTS = False

total_scenarios = len(strategy_id) * len(ISO)
print(f"Configuration:")
print(f"  Strategies: {len(strategy_id)}")
print(f"  Countries: {len(ISO)}")
print(f"  Total scenarios: {total_scenarios}")
print(f"  Scenarios folder: {SCENARIOS_FOLDER}\n")

#==============================================================================
# III. Core Function - Run Single Scenario
#==============================================================================

def run_single_scenario(strategy, country, MRIO_BASE, Scenario_Log):
    """
    Run employment estimation for a single strategy-country combination.

    Calculates Direct and Indirect employment based on IO theory:
    - Direct = Employment from initial final demand
    - Indirect = Employment from supply chain multiplier (Leontief)
    - Total = Direct + Indirect

    Returns:
    --------
    dict : Results dictionary, or None if failed/skipped
    """

    scenario_name = f"Strategy_{strategy}_{country}"
    scenario_file = os.path.join(SCENARIOS_FOLDER, f"{scenario_name}.xlsx")

    if not os.path.exists(scenario_file):
        print(f"    ✗ SKIPPED: File not found: {scenario_name}.xlsx")
        return None

    try:
        # ===================================================================
        # STEP 1: Load Scenario
        # ===================================================================
        Scenario = scenario(MRIO_BASE, scenario_file, Scenario_Log)
        Scenario.set_exog_inv()

        if not hasattr(Scenario, 'inv_exog') or Scenario.inv_exog.empty:
            print(f"    ✗ SKIPPED: No investment data in {scenario_name}")
            return None

        total_investment = Scenario.inv_exog['dk'].sum()

        # ===================================================================
        # STEP 2: Investment Converter (Sector Investment → Product Demand)
        # ===================================================================
        # Set default inv_spending (needed for investment module, not used in employment-only mode)
        if not hasattr(Scenario, 'inv_spending'):
            Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

        INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
        INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
        INV_model.build_inv_output_elas()
        INV_model.calc_inv_share()
        INV_model.calc_dy_inv_exog(Scenario.inv_exog)

        # Convert to vector: This is INITIAL FINAL DEMAND
        dy_inv_exog = MRIO_df_to_vec(
            INV_model.dy_inv_exog,
            'REG_imp', 'TRAD_COMM', 'dy',
            MRIO_BASE.R['Region_acronyms'].to_list(),
            MRIO_BASE.P['Lfd_Nr'].to_list()
        )

        # ===================================================================
        # STEP 3: Calculate Output Changes (IO Model)
        # ===================================================================
        IO_model = IO(MRIO_BASE)

        # Build Leontief inverse if not already loaded
        if not hasattr(IO_model, 'L_BASE'):
            print(f"  [{scenario_name}] Calculating Leontief inverse...")
            IO_model.build_A_base()  # Build technical coefficients matrix
            IO_model.invert_A_base()  # Calculate L = (I - A)^(-1)

        # Apply Leontief inverse: dX = L × dY
        # This gives TOTAL output change (direct + indirect)
        dq_total = IO_model.calc_dq_exog(dy_inv_exog)

        # ===================================================================
        # STEP 4: Calculate Employment Changes
        # ===================================================================
        Empl_model = empl(MRIO_BASE)
        Empl_model.build_empl_coef()

        # TOTAL employment (direct + indirect)
        # Formula: dE_total = e × (L × dY)
        dempl_total = Empl_model.calc_dempl([dq_total])[0]

        # DIRECT employment (first-round effect only)
        # Formula: dE_direct = e × dY
        dempl_direct = Empl_model.calc_dempl([dy_inv_exog])[0]

        # INDIRECT employment (supply chain multiplier)
        # Formula: dE_indirect = dE_total - dE_direct
        dempl_indirect = dempl_total - dempl_direct

        # ===================================================================
        # STEP 5: Build Results DataFrames
        # ===================================================================

        # Combine with MRIO structure
        empl_results = pd.concat([
            MRIO_BASE.mrio_list,
            pd.DataFrame({
                'Direct_Jobs': dempl_direct,
                'Indirect_Jobs': dempl_indirect,
                'Total_Jobs': dempl_total
            })
        ], axis=1)

        # Calculate summary statistics
        total_jobs = dempl_total.sum()
        direct_jobs = dempl_direct.sum()
        indirect_jobs = dempl_indirect.sum()
        employment_multiplier = total_jobs / total_investment * 1e6
        output_multiplier = dq_total.sum() / dy_inv_exog.sum()

        # Get country name
        country_name_lookup = MRIO_BASE.R[MRIO_BASE.R['Region_acronyms'] == country]['Region_names'].values
        country_name = country_name_lookup[0] if len(country_name_lookup) > 0 else country

        # ===================================================================
        # Employment by Region
        # ===================================================================
        empl_by_region = empl_results.groupby('Reg_ID').agg({
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

        # ===================================================================
        # Employment by Sector
        # ===================================================================
        empl_by_sector = empl_results.groupby('Sec_ID').agg({
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

        # ===================================================================
        # Optional: Save Individual Results
        # ===================================================================
        if SAVE_INDIVIDUAL_RESULTS:
            output_dir = os.path.join(os.getcwd(), "GLORIA_results", "Individual_Results")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"Results_{scenario_name}.xlsx")

            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                empl_by_region.to_excel(writer, sheet_name='Employment_by_Region', index=False)
                empl_by_sector.to_excel(writer, sheet_name='Employment_by_Sector', index=False)

        # ===================================================================
        # Return Results Dictionary
        # ===================================================================
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
        del dy_inv_exog, dq_total, dempl_total, dempl_direct, dempl_indirect
        del empl_results
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

step_time = time.time()
MRIO_BASE = exog_vars()
print(f"✓ MRIO data loaded")
print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

# Initialize logging (optional)
try:
    from SourceCode.log import log as _log
    Scenario_Log = _log("EmploymentOnly_Batch")
except:
    # Create a simple mock logger
    class MockLog:
        def log_to_csv(self, *args, **kwargs):
            pass
        def log(self, *args, **kwargs):
            pass
    Scenario_Log = MockLog()
    print("Note: Using mock logger (this is OK)\n")

print("="*80)
print("STEP 2: Processing All Scenarios")
print("="*80)
print()

# Storage
all_empl_by_region = []
all_empl_by_sector = []
batch_summary = []

# Counters
batch_start_time = time.time()
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
# V. Save Results
#==============================================================================

print("="*80)
print("STEP 3: Saving Results")
print("="*80)
print()

output_dir = os.path.join(os.getcwd(), "GLORIA_results")
os.makedirs(output_dir, exist_ok=True)

# Employment by region
if all_empl_by_region:
    combined_empl_by_region = pd.concat(all_empl_by_region, ignore_index=True)
    output_file = os.path.join(output_dir, "ALL_RESULTS_Employment_by_Region.csv")
    combined_empl_by_region.to_csv(output_file, index=False)
    print(f"✓ Saved: ALL_RESULTS_Employment_by_Region.csv")
    print(f"  Rows: {len(combined_empl_by_region):,}")
    print(f"  Columns: {list(combined_empl_by_region.columns)}\n")

# Employment by sector
if all_empl_by_sector:
    combined_empl_by_sector = pd.concat(all_empl_by_sector, ignore_index=True)
    output_file = os.path.join(output_dir, "ALL_RESULTS_Employment_by_Sector.csv")
    combined_empl_by_sector.to_csv(output_file, index=False)
    print(f"✓ Saved: ALL_RESULTS_Employment_by_Sector.csv")
    print(f"  Rows: {len(combined_empl_by_sector):,}")
    print(f"  Columns: {list(combined_empl_by_sector.columns)}\n")

# Batch summary
batch_summary_df = pd.DataFrame(batch_summary)
output_file = os.path.join(output_dir, "BATCH_SUMMARY.csv")
batch_summary_df.to_csv(output_file, index=False)
print(f"✓ Saved: BATCH_SUMMARY.csv")
print(f"  Rows: {len(batch_summary_df):,}\n")

#==============================================================================
# VI. Final Summary
#==============================================================================

print("="*80)
print("BATCH PROCESSING COMPLETE")
print("="*80)
print()
print(f"Total scenarios: {total_scenarios}")
print(f"  ✓ Successful: {success_count}")
print(f"  ✗ Failed: {failed_count}")
print(f"  ⊘ Skipped: {skipped_count}")
print()
print(f"Total runtime: {batch_total_time/60:.1f} minutes ({batch_total_time:.0f} seconds)")
print(f"Average per scenario: {batch_total_time/scenario_count:.1f} seconds")
print()

if success_count > 0:
    print("="*80)
    print("SAMPLE RESULTS (First 5 successful scenarios)")
    print("="*80)
    print()
    successful = batch_summary_df[batch_summary_df['Status'] == 'SUCCESS'].head(5)
    print(successful[[
        'Strategy', 'Country', 'Country_Name',
        'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs', 'Employment_Multiplier'
    ]].to_string(index=False))
    print()

print("="*80)
print("Ready for analysis!")
print("="*80)
