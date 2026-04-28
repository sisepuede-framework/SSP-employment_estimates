# -*- coding: utf-8 -*-
"""
MINDSET EMPLOYMENT-ONLY ESTIMATION

Modified version of RunMINDSET.py for employment impact estimation only.
This script SKIPS: energy, trade, household, price, tax, and income modules.
This script RUNS: data loading, scenario, IO calculations, employment, results.

Created: 2026-03-09
Purpose: Simplified MINDSET workflow for dissertation employment analysis
Based on: Original RunMINDSET.py by wb582890

USAGE:
    python RunMINDSET_EmploymentOnly.py

CONFIGURATION:
    Set SPYDER = True and modify scenario_name below (line 55)
    Or run from command line: python RunMINDSET_EmploymentOnly.py "ScenarioName"

WHAT THIS SCRIPT DOES:
    1. Load MRIO data (Leontief inverse, employment coefficients)
    2. Load investment scenario (exogenous final demand shock)
    3. Calculate output changes: dX = L × dY
    4. Calculate employment changes: dE = e × dX
    5. Save results to Excel
"""

#==============================================================================
# I. Import Required Modules
#==============================================================================

import numpy as np
import pandas as pd
import time
import sys
import os

#------------------------------------------------------------------------------
# PATH SETUP - Critical for finding MINDSET modules
#------------------------------------------------------------------------------
# In R, this is like: setwd("C:/path/to/project")
# In Python, we add the MINDSET root directory to sys.path so imports work

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up to MINDSET_module-main root (two levels up from Claude Code/temp)
# This is like using "../.." in R
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

# Add to Python's search path (like .libPaths() in R)
if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)

# Change working directory to MINDSET root (like setwd() in R)
os.chdir(mindset_root)

print(f"MINDSET root directory: {mindset_root}")
print(f"Current working directory: {os.getcwd()}\n")

#------------------------------------------------------------------------------

# ✓ REQUIRED: Core MINDSET modules for employment estimation
from SourceCode.exog_vars_SSP import exog_vars  # Using custom version with selected countries
from SourceCode.scenario import scenario
from SourceCode.InputOutput import IO
from SourceCode.employment import empl
from SourceCode.investment import invest  # Investment module for converting investment to final demand
from SourceCode.results import results

# ✓ REQUIRED: Utility functions
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df

# ✗ SKIPPED: Modules not needed for employment-only
# from SourceCode.ener_elas import ener_elas
# from SourceCode.ener_balance import ener_balance
# from SourceCode.tax_rev import tax_rev
# from SourceCode.BTA import BTA
# from SourceCode.prod_cost import prod_cost
# from SourceCode.price import price
# from SourceCode.household import household as hh
# from SourceCode.government import gov
# from SourceCode.trade import trade
# from SourceCode.investment import invest
# from SourceCode.income import income
# from SourceCode.GDP import GDP

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("\n" + "="*80)
print("MINDSET EMPLOYMENT-ONLY ESTIMATION")
print("="*80 + "\n")

#==============================================================================
# II. Configuration and Scenario Selection
#==============================================================================

SPYDER = True  # Set to True if running from IDE, False for command line

if SPYDER:
    # CONFIGURE YOUR SCENARIO HERE:
    scenario_name = "Infrastructure_Investment"  # ← CHANGE THIS TO YOUR SCENARIO NAME
    print(f"Running in IDE mode with scenario: {scenario_name}")
else:
    # Command line mode
    if len(sys.argv) > 1:
        scenario_name = sys.argv[1]
    else:
        print("ERROR: No scenario name provided.")
        print("Usage: python RunMINDSET_EmploymentOnly.py ScenarioName")
        sys.exit(1)

# File paths
# Note: os.getcwd() now points to MINDSET root because we changed it above
# In R, this is like: file.path(getwd(), "GLORIA_template", "Scenarios", paste0(scenario_name, ".xlsx"))
scenario_path = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios", f"{scenario_name}.xlsx")

print(f"Scenario file: {scenario_path}")
print(f"Checking if scenario file exists: {os.path.exists(scenario_path)}\n")

# Start timer
start_time = time.time()

#==============================================================================
# III. STEP 1: Load MRIO Data
#==============================================================================
print("-" * 80)
print("STEP 1: Loading MRIO Data")
print("-" * 80)

step_time = time.time()

# Load all exogenous variables
# This loads: L_BASE (Leontief inverse), EMPL_COEF (employment coefficients),
# country/sector IDs, and other required data structures
MRIO_BASE = exog_vars()

print(f"✓ Loaded Leontief inverse: {MRIO_BASE.L_BASE.shape}")
print(f"✓ Loaded employment coefficients")
print(f"✓ Loaded {len(MRIO_BASE.COU_ID)} countries/regions")
print(f"✓ Loaded {len(MRIO_BASE.SEC_ID)} sectors")
print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# IV. STEP 2: Load Investment Scenario
#==============================================================================
print("-" * 80)
print("STEP 2: Loading Investment Scenario")
print("-" * 80)

step_time = time.time()

# Load scenario (your infrastructure investment shock)
# This reads the Excel file and extracts investment specifications
Scenario = scenario(MRIO_BASE, scenario_path, None)

# ✗ SKIP: Carbon tax settings (not needed for infrastructure investment)
# if tax_incidence_file is None:
#     Scenario.set_carbon_tax()

# ✗ SKIP: Energy balance and tax incidence (not needed)
# Energy_emissions = ener_balance(MRIO_BASE, Scenario)
# carbon_tax = Energy_emissions.calculate_tax_incidence()

# ✗ SKIP: Revenue split, tax parameters (not needed)
# rev_split = Scenario.build_rev_split()
# payr_tax_split = Scenario.build_payr_tax_split()

# ✗ SKIP: IO changes, cost shocks (not applicable)
# io_changes = Scenario.set_io_changes()
# Scenario.set_cost_shock()

# ✓ REQUIRED: Extract exogenous investment from scenario file
# This reads the "Investment by" sheet from your Excel file
Scenario.set_exog_inv()

# Check if we have investment data
if hasattr(Scenario, 'inv_exog') and not Scenario.inv_exog.empty:
    total_investment = Scenario.inv_exog['dk'].sum()
    print(f"✓ Loaded exogenous investment: ${total_investment:,.0f}")
    print(f"✓ Investment by {len(Scenario.inv_exog)} sector-region pairs")

    # ✓ REQUIRED: Initialize investment module to convert investment to final demand
    # This converts "sector X invests $Y" into "demand for goods A, B, C"
    print(f"✓ Initializing investment module...")

    # Build investment converter (accounts for scenario adjustments)
    INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)

    # Initialize investment model
    INV_model = invest(MRIO_BASE, INV_CONV, Scenario)

    # Build investment parameters
    INV_model.build_inv_output_elas()
    INV_model.calc_inv_share()

    # Convert investment to final demand for goods
    # Input: Scenario.inv_exog (REG_imp, PROD_COMM, dk)
    # Output: INV_model.dy_inv_exog (REG_imp, TRAD_COMM, dy)
    INV_model.calc_dy_inv_exog(Scenario.inv_exog)

    print(f"✓ Converted investment to final demand using investment converter")

else:
    print("WARNING: No exogenous investment found in scenario file.")
    print("Check that your scenario Excel file has 'Investment by' sheet with data.")
    sys.exit(1)

print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# V. STEP 3: Calculate Output Changes (Input-Output Model)
#==============================================================================
print("-" * 80)
print("STEP 3: Calculating Output Changes")
print("-" * 80)

step_time = time.time()

# Initialize Input-Output model
IO_model = IO(MRIO_BASE)
IO_model.initialize()

print(f"✓ Initialized IO model")
print(f"✓ Baseline output (q_base): {MRIO_BASE.L_BASE.shape[0]} sector-regions")

# ✗ SKIP: Energy elasticity calculations
# Ener_model = ener_elas(MRIO_BASE)
# tech_coef_ener = Ener_model.calc_tech_coef_ener()
# dL_ener = IO_model.build_dL_ener(...)
# dq_tech_eff = IO_model.calc_dq_energy(dL_ener)

# ✗ SKIP: Price calculations
# Price_model = price(MRIO_BASE, IO_model.L_BASE, BTA_cou)
# dp_base = Price_model.calc_dp_base(v_base)

# ✗ SKIP: Household demand response
# HH_model = hh(MRIO_BASE)
# HH_price_eff, HH_inc_eff = HH_model.calc_hh_demand_change(...)

# ✗ SKIP: Government spending from tax revenue
# GOV_model = gov(MRIO_BASE, Scenario)
# GOV_recyc = GOV_model.calc_gov_demand_change(recyc_rev)

# ✗ SKIP: Trade substitution
# Trade_model = trade(MRIO_BASE)
# ind_trade = Trade_model.calc_IO_coef(ind_ener_glo, dp_pre_trade)

# ✗ SKIP: Induced investment
# INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
# dq_inv_induced = INV_model.calc_dy_inv_induced(...)

# ✓ REQUIRED: Extract final demand from investment module as vector
# Convert from DataFrame to vector matching MRIO dimensions
# This is the output from investment module: demand for investment goods
dy_inv_exog = MRIO_df_to_vec(
    INV_model.dy_inv_exog,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

print(f"✓ Converted investment demand to vector (size: {len(dy_inv_exog)})")
print(f"✓ Total final demand from investment: ${dy_inv_exog.sum():,.0f}")

# ✓ REQUIRED: Calculate output changes using Leontief model
# This is the KEY calculation: dX = L × dY
dq_exog_fd = IO_model.calc_dq_exog(dy_inv_exog)

print(f"✓ Calculated output changes: dX = L × dY")
print(f"✓ Total output change: ${dq_exog_fd.sum():,.0f}")
print(f"✓ Output multiplier: {dq_exog_fd.sum() / dy_inv_exog.sum():.2f}x")

# For simplicity in employment-only mode, total output change = exogenous shock effect
# No iterations, no behavioral responses, just direct + indirect effects
dq_total = dq_exog_fd.copy()

print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# VI. STEP 4: Calculate Employment Changes
#==============================================================================
print("-" * 80)
print("STEP 4: Calculating Employment Changes")
print("-" * 80)

step_time = time.time()

# Build employment model
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()

print(f"✓ Loaded employment coefficients")

# ✗ SKIP: Employment multiplier calculation using base employment data
# (We're using simpler approach with just coefficients)
# Empl_model.calc_empl_multiplier(empl_base, q_base)

# ✓ REQUIRED: Calculate employment changes
# This is the KEY employment calculation: dE = e × dX
# where e = employment coefficient, dX = output change
dempl_exog_fd = Empl_model.calc_dempl([dq_exog_fd])[0]

print(f"✓ Calculated employment changes: dE = e × dX")
print(f"✓ Total jobs created: {dempl_exog_fd.sum():,.0f}")
print(f"✓ Employment multiplier: {dempl_exog_fd.sum() / dy_inv_exog.sum() * 1e6:.2f} jobs per $1M")

# For employment-only: total employment change = exogenous shock effect
dempl_total = dempl_exog_fd.copy()

print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# VII. STEP 5: Format and Save Results
#==============================================================================
print("-" * 80)
print("STEP 5: Saving Results")
print("-" * 80)

step_time = time.time()

# ✗ SKIP: GDP calculations
# GDP_model = GDP(IO_model)
# gdp_base = GDP_model.calc_gdp_base()
# dgdp_total = GDP_model.calc_gdp_changes(...)

# ✗ SKIP: Price changes
# price_change = ...

# ✗ SKIP: Tax revenue
# total_revenue = Tax_rev.build_tax_rev_result(...)

# ✓ REQUIRED: Build output change results
output_change = pd.concat([
    MRIO_BASE.mrio_list,
    pd.DataFrame(IO_model.q_base, columns=["q_base"]),
    pd.DataFrame(dq_exog_fd, columns=["dq_exog_fd"]),
    pd.DataFrame(dq_total, columns=["dq_total"])
], axis=1)

print(f"✓ Formatted output change results")

# ✓ REQUIRED: Build employment change results
empl_change = pd.concat([
    MRIO_BASE.mrio_list,
    pd.DataFrame(dempl_exog_fd, columns=["dempl_exog_fd"]),
    pd.DataFrame(dempl_total, columns=["dempl_total"])
], axis=1)

print(f"✓ Formatted employment change results")

# ✓ REQUIRED: Build summary statistics
# Calculate total employment by region
empl_by_region = empl_change.groupby('Reg_ID')['dempl_total'].sum().reset_index()
empl_by_region.columns = ['Region', 'Jobs_Created']
empl_by_region = empl_by_region.merge(
    MRIO_BASE.R[['Region_acronyms', 'Region_names']],
    left_on='Region',
    right_on='Region_acronyms',
    how='left'
)
empl_by_region = empl_by_region[['Region_names', 'Jobs_Created']]

# Calculate total employment by sector
empl_by_sector = empl_change.groupby('Sec_ID')['dempl_total'].sum().reset_index()
empl_by_sector.columns = ['Sector', 'Jobs_Created']
empl_by_sector = empl_by_sector.merge(
    MRIO_BASE.P[['Lfd_Nr', 'Product_name']],
    left_on='Sector',
    right_on='Lfd_Nr',
    how='left'
)
empl_by_sector = empl_by_sector[['Product_name', 'Jobs_Created']]

# Calculate employment multiplier
total_jobs = dempl_total.sum()
total_investment = dy_inv_exog.sum()
employment_multiplier = total_jobs / total_investment * 1e6  # Jobs per $1M

summary_stats = pd.DataFrame({
    'Metric': [
        'Total Investment (USD)',
        'Total Jobs Created',
        'Employment Multiplier (jobs/$1M)',
        'Average Output Multiplier'
    ],
    'Value': [
        f"${total_investment:,.0f}",
        f"{total_jobs:,.0f}",
        f"{employment_multiplier:.2f}",
        f"{dq_total.sum() / total_investment:.2f}x"
    ]
})

print(f"✓ Created summary statistics")
print(f"\nSUMMARY:")
print(f"  Total Investment: ${total_investment:,.0f}")
print(f"  Total Jobs Created: {total_jobs:,.0f}")
print(f"  Employment Multiplier: {employment_multiplier:.2f} jobs per $1M")

# ✓ REQUIRED: Save to Excel
# Output directory is relative to MINDSET root (current working directory)
output_dir = os.path.join(os.getcwd(), "GLORIA_results")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, f"Results_{scenario_name}_EmploymentOnly.xlsx")

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Summary sheet
    summary_stats.to_excel(writer, sheet_name='Summary', index=False)

    # Employment by region
    empl_by_region.to_excel(writer, sheet_name='Employment_by_Region', index=False)

    # Employment by sector
    empl_by_sector.to_excel(writer, sheet_name='Employment_by_Sector', index=False)

    # Detailed employment changes
    empl_change.to_excel(writer, sheet_name='Employment_Details', index=False)

    # Detailed output changes
    output_change.to_excel(writer, sheet_name='Output_Details', index=False)

print(f"✓ Results saved to: {output_file}")
print(f"Time: {round(time.time() - step_time, 1)} seconds\n")

#==============================================================================
# VIII. Final Summary
#==============================================================================
total_time = time.time() - start_time

print("="*80)
print("EMPLOYMENT ESTIMATION COMPLETE")
print("="*80)
print(f"\nTotal Runtime: {round(total_time, 1)} seconds")
print(f"\nResults saved to:")
print(f"  {output_file}")
print(f"\nSheets created:")
print(f"  1. Summary - Key metrics and multipliers")
print(f"  2. Employment_by_Region - Jobs created by region")
print(f"  3. Employment_by_Sector - Jobs created by sector")
print(f"  4. Employment_Details - Full sector-region breakdown")
print(f"  5. Output_Details - Output changes for validation")
print(f"\nEmployment Impact:")
print(f"  Investment: ${total_investment:,.0f}")
print(f"  Jobs Created: {total_jobs:,.0f}")
print(f"  Multiplier: {employment_multiplier:.2f} jobs/$1M")
print("\n" + "="*80 + "\n")

#==============================================================================
# NOTES FOR REPLICATION
#==============================================================================
"""
MODULES USED (5):
1. exog_vars.py - Load MRIO data
2. scenario.py - Load investment scenario
3. InputOutput.py - Calculate dX = L × dY
4. employment.py - Calculate dE = e × dX
5. utils.py - Data conversion utilities

MODULES SKIPPED (11):
1. ener_elas.py - Energy substitution (not needed)
2. ener_balance.py - Carbon tax incidence (not needed)
3. tax_rev.py - Tax revenue calculation (not applicable)
4. BTA.py - Border tax adjustments (not applicable)
5. prod_cost.py - Production cost changes (not needed)
6. price.py - Price effects (not needed)
7. household.py - Household demand response (not needed)
8. government.py - Government spending (no tax revenue)
9. trade.py - Trade substitution (not needed)
10. investment.py - Induced investment (not needed)
11. income.py - Income feedback loop (not needed)

CORE EQUATIONS:
1. Output changes: dX = L × dY
   where L = Leontief inverse, dY = final demand shock

2. Employment changes: dE = e × dX
   where e = employment coefficient, dX = output change

3. Employment multiplier: m = Σ(dE) / Investment
   measured in jobs per $1M invested

ASSUMPTIONS:
- No behavioral responses (households, firms don't respond to prices/income)
- No energy substitution or trade substitution
- No induced investment from output growth
- No iterative income-employment loop
- Linear technology (constant returns to scale)
- No capacity constraints

VALIDATION:
- Compare employment multiplier to literature (typical range: 5-20 jobs/$1M)
- Check output multiplier is reasonable (typical range: 1.5-3.0)
- Verify no negative employment changes
- Ensure results sum correctly across regions and sectors
"""
