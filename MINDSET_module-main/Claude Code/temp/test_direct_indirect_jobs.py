"""
Test script to understand how to calculate Direct vs Indirect jobs in MINDSET
"""

import numpy as np
import pandas as pd
import sys
import os

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

# Import MINDSET modules
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario
from SourceCode.InputOutput import IO
from SourceCode.employment import empl
from SourceCode.investment import invest
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df
from SourceCode.log import log as _log

print("="*80)
print("TESTING: Direct vs Indirect Jobs Calculation")
print("="*80)

# Load MRIO data
print("\n1. Loading MRIO data...")
MRIO_BASE = exog_vars()
print(f"   ✓ Loaded")

# Load scenario
scenario_file = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios", "Strategy_1004_MEX.xlsx")
print(f"\n2. Loading scenario: {scenario_file}")

Scenario_Log = _log("Test")
Scenario = scenario(MRIO_BASE, scenario_file, Scenario_Log)
Scenario.set_exog_inv()

print(f"\n3. Investment data (Scenario.inv_exog):")
print(f"   Shape: {Scenario.inv_exog.shape}")
print(f"   Columns: {Scenario.inv_exog.columns.tolist()}")
print(f"\n   First 10 rows:")
print(Scenario.inv_exog.head(10))
print(f"\n   Total investment: ${Scenario.inv_exog['dk'].sum():,.2f}")

# Which sectors are DIRECTLY receiving investment?
direct_investment_sectors = Scenario.inv_exog[['REG_imp', 'PROD_COMM']].copy()
direct_investment_sectors['has_direct_investment'] = True
print(f"\n4. Sectors with DIRECT investment:")
print(f"   Count: {len(direct_investment_sectors)} (region, product) pairs")
print(direct_investment_sectors.head(10))

# Initialize investment module
print(f"\n5. Running investment converter...")
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
print(f"\n6. Calculating output changes...")
IO_model = IO(MRIO_BASE)
IO_model.build_L_mat()
dq_exog_fd = IO_model.calc_dq_exog(dy_inv_exog)

print(f"   Output changes shape: {dq_exog_fd.shape}")
print(f"   Total output change: ${dq_exog_fd.sum():,.2f}")

# Calculate employment changes
print(f"\n7. Calculating employment changes...")
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
dempl_exog_fd = Empl_model.calc_dempl([dq_exog_fd])[0]

# Build results DataFrame
empl_change = pd.concat([
    MRIO_BASE.mrio_list,
    pd.DataFrame(dempl_exog_fd, columns=["Jobs_Created"])
], axis=1)

print(f"\n8. Employment results:")
print(f"   Total jobs: {dempl_exog_fd.sum():,.2f}")
print(f"   Results shape: {empl_change.shape}")
print(f"\n   First 10 rows:")
print(empl_change.head(10))

# Identify DIRECT jobs
# Direct jobs = employment in (region, sector) pairs that received direct investment
print(f"\n9. Separating Direct vs Indirect jobs...")

# Merge with direct investment flags
empl_change_tagged = empl_change.merge(
    direct_investment_sectors,
    left_on=['Reg_ID', 'Sec_ID'],
    right_on=['REG_imp', 'PROD_COMM'],
    how='left'
)
empl_change_tagged['has_direct_investment'] = empl_change_tagged['has_direct_investment'].fillna(False)

# Calculate direct vs indirect
direct_jobs = empl_change_tagged[empl_change_tagged['has_direct_investment'] == True]['Jobs_Created'].sum()
total_jobs = empl_change_tagged['Jobs_Created'].sum()
indirect_jobs = total_jobs - direct_jobs

print(f"\n   Direct jobs: {direct_jobs:,.2f}")
print(f"   Indirect jobs: {indirect_jobs:,.2f}")
print(f"   Total jobs: {total_jobs:,.2f}")
print(f"   Direct/Total ratio: {direct_jobs/total_jobs*100:.1f}%")

# Show example by region
print(f"\n10. Example: Jobs by region (Direct vs Indirect)")
by_region = empl_change_tagged.groupby(['Reg_ID', 'has_direct_investment'])['Jobs_Created'].sum().reset_index()
by_region = by_region.merge(
    MRIO_BASE.R[['Region_acronyms', 'Region_names']],
    left_on='Reg_ID',
    right_on='Region_acronyms',
    how='left'
)
by_region = by_region.pivot_table(
    index=['Region_acronyms', 'Region_names'],
    columns='has_direct_investment',
    values='Jobs_Created',
    fill_value=0
).reset_index()

if False in by_region.columns:
    by_region['Indirect_Jobs'] = by_region[False]
else:
    by_region['Indirect_Jobs'] = 0

if True in by_region.columns:
    by_region['Direct_Jobs'] = by_region[True]
else:
    by_region['Direct_Jobs'] = 0

by_region['Total_Jobs'] = by_region['Direct_Jobs'] + by_region['Indirect_Jobs']
by_region = by_region[['Region_acronyms', 'Region_names', 'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs']]
by_region = by_region.sort_values('Total_Jobs', ascending=False)

print(by_region.head(10).to_string(index=False))

# Show example by sector
print(f"\n11. Example: Jobs by sector (Direct vs Indirect)")
by_sector = empl_change_tagged.groupby(['Sec_ID', 'has_direct_investment'])['Jobs_Created'].sum().reset_index()
by_sector = by_sector.merge(
    MRIO_BASE.P[['Lfd_Nr', 'Sector_names']],
    left_on='Sec_ID',
    right_on='Lfd_Nr',
    how='left'
)
by_sector = by_sector.pivot_table(
    index=['Lfd_Nr', 'Sector_names'],
    columns='has_direct_investment',
    values='Jobs_Created',
    fill_value=0
).reset_index()

if False in by_sector.columns:
    by_sector['Indirect_Jobs'] = by_sector[False]
else:
    by_sector['Indirect_Jobs'] = 0

if True in by_sector.columns:
    by_sector['Direct_Jobs'] = by_sector[True]
else:
    by_sector['Direct_Jobs'] = 0

by_sector['Total_Jobs'] = by_sector['Direct_Jobs'] + by_sector['Indirect_Jobs']
by_sector = by_sector[['Lfd_Nr', 'Sector_names', 'Direct_Jobs', 'Indirect_Jobs', 'Total_Jobs']]
by_sector = by_sector.sort_values('Total_Jobs', ascending=False)

print(by_sector.head(10).to_string(index=False))

print("\n" + "="*80)
print("✓ Test complete! This approach can be implemented in the batch script.")
print("="*80)
