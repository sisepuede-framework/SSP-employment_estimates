"""
TEST: Process ONE Strategy - FINAL CLEAN VERSION

Clean output structure with proper column names.
"""

import sys
import os
import re
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("TEST: Employment Analysis - FINAL CLEAN OUTPUT")
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

COUNTRY_NAMES = {
    'ROW': 'Rest of World', 'BGR': 'Bulgaria', 'BLZ': 'Belize',
    'EGY': 'Egypt', 'LBY': 'Libya', 'MAR': 'Morocco', 'MEX': 'Mexico', 'UGA': 'Uganda'
}

#==============================================================================
# STEP 1: Load Data
#==============================================================================
print("STEP 1: Loading Crosswalk and Attributes")
print("-"*80)

data_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data"

# Load ISIC concordance
crosswalk_df = pd.read_excel(
    os.path.join(data_path, "GLORIA-Eora26 - Crosswalk.xlsx"),
    sheet_name="GLORIA (v60) - ISIC concordance"
)

# Get ISIC sections
isic_sections = [col for col in crosswalk_df.columns if len(col) == 1 and col.isalpha()]
section_descriptions = {sec: crosswalk_df[sec].iloc[0] for sec in isic_sections}

# Remove header row and create mapping
crosswalk_df = crosswalk_df.iloc[1:].reset_index(drop=True)
crosswalk_df['product_code'] = range(1, len(crosswalk_df) + 1)

product_sector_map = {}
for idx, row in crosswalk_df.iterrows():
    product = row['product_code']
    sectors = [sec for sec in isic_sections if row[sec] == 1]
    product_sector_map[product] = sectors if len(sectors) > 0 else ['Other']

print(f"ISIC sections: {len(section_descriptions)}")

# Load strategy attributes
df_attributes = pd.read_csv(os.path.join(data_path, "ATTRIBUTE_STRATEGY.csv"))
print(f"Strategy attributes: {df_attributes.shape}")
print()

#==============================================================================
# STEP 2: Initialize MINDSET
#==============================================================================
print("STEP 2: Initializing MINDSET")
print("-"*80)

MRIO_BASE = exog_vars()

# Employment baseline
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_total"] = (
    empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"] +
    empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
)

empl_base = MRIO_df_to_vec(
    empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]],
    "REG_imp", "PROD_COMM", "vol_total",
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

# IO and employment models
IO_model = IO(MRIO_BASE)
IO_model.initialize()

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)
print("[OK] Models ready\n")

#==============================================================================
# STEP 3: Process Strategy
#==============================================================================
print("STEP 3: Processing Strategy_1004_EGY")
print("-"*80)

scenario_name = "Strategy_1004_EGY"
scenario_file = f"GLORIA_template/Scenarios/{scenario_name}.xlsx"

Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

investing_countries = Scenario.inv_exog[Scenario.inv_exog['dk'] > 0]['REG_imp'].unique()
main_country = investing_countries[0]
main_country_name = COUNTRY_NAMES[main_country]

print(f"Country: {main_country_name} ({main_country})\n")

# Run investment and employment calculations
if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

dy_inv_exog = MRIO_df_to_vec(
    INV_model.dy_inv_exog, 'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

dq_total = IO_model.calc_dq_exog(dy_inv_exog)
dempl = Empl_model.calc_dempl(dq_total)
direct_demand_mask = dy_inv_exog > 0.01

#==============================================================================
# STEP 4: Extract and Aggregate Results
#==============================================================================
print("STEP 4: Aggregating to ISIC Sectors")
print("-"*80)

country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}
c_idx = country_idx[main_country]
c_start = c_idx * 120
c_end = c_start + 120

# Product-level extraction
product_results = []
for s_idx, product in enumerate(MRIO_BASE.P['Lfd_Nr'].to_list()):
    idx_pos = c_start + s_idx
    total_jobs = dempl[idx_pos]
    is_direct = direct_demand_mask[idx_pos]

    product_results.append({
        'product': product,
        'direct_jobs': total_jobs if is_direct else 0.0,
        'indirect_jobs': 0.0 if is_direct else total_jobs,
        'total_jobs': total_jobs
    })

df_product = pd.DataFrame(product_results)

# Aggregate to sectors
sector_jobs = {sec: {'name': section_descriptions[sec], 'direct': 0.0, 'indirect': 0.0, 'total': 0.0}
               for sec in section_descriptions.keys()}

for _, row in df_product.iterrows():
    product = row['product']
    if product in product_sector_map:
        sectors = product_sector_map[product]
        weight = 1.0 / len(sectors)
        for sec in sectors:
            if sec in sector_jobs:
                sector_jobs[sec]['direct'] += row['direct_jobs'] * weight
                sector_jobs[sec]['indirect'] += row['indirect_jobs'] * weight
                sector_jobs[sec]['total'] += row['total_jobs'] * weight

total_jobs_all = sum([s['total'] for s in sector_jobs.values()])

# Create clean dataframe
results = []
for sector_code in sorted(sector_jobs.keys()):
    jobs = sector_jobs[sector_code]
    share = jobs['total'] / total_jobs_all if total_jobs_all > 0 else 0.0

    results.append({
        'country_name': main_country_name,
        'country_ISO': main_country,
        'strategy_id': scenario_name,
        'sector_code': sector_code,
        'sector_name': jobs['name'],
        'direct_jobs': jobs['direct'],
        'indirect_jobs': jobs['indirect'],
        'total_jobs': jobs['total'],
        'share_of_total_jobs': share
    })

df_final = pd.DataFrame(results)

print(f"Sectors: {len(df_final)}")
print(f"Total jobs: {df_final['total_jobs'].sum():.2f}")
print(f"Share sum: {df_final['share_of_total_jobs'].sum():.6f}\n")

#==============================================================================
# STEP 5: Merge with Strategy Attributes
#==============================================================================
print("STEP 5: Merging Strategy Attributes")
print("-"*80)

# Extract numeric ID from strategy name
numeric_id = int(re.search(r'_(\d+)_', scenario_name).group(1))
df_final['strategy_numeric_id'] = numeric_id

# Merge with attributes
df_final = df_final.merge(
    df_attributes.rename(columns={'strategy': 'strategy_name'}),
    left_on='strategy_numeric_id',
    right_on='strategy_id',
    how='left',
    suffixes=('', '_attr')
)

# Clean up columns - drop merge artifacts
cols_to_drop = [col for col in df_final.columns if col in ['strategy_numeric_id', 'strategy_id_attr']]
df_final = df_final.drop(columns=cols_to_drop)

# Final column order
final_cols = ['country_name', 'country_ISO', 'strategy_id', 'strategy_name',
              'sector_code', 'sector_name', 'direct_jobs', 'indirect_jobs',
              'total_jobs', 'share_of_total_jobs']

df_final = df_final[final_cols]

print(f"[OK] Merge complete\n")

#==============================================================================
# STEP 6: Display Results
#==============================================================================
print("="*80)
print("FINAL OUTPUT STRUCTURE")
print("="*80)
print()

print(f"Total rows: {len(df_final)}")
print(f"Total columns: {len(df_final.columns)}")
print()

print("Columns:")
for i, col in enumerate(df_final.columns, 1):
    print(f"  {i:2d}. {col}")
print()

print("="*80)
print("NON-ZERO SECTORS")
print("="*80)
print()

df_nonzero = df_final[df_final['total_jobs'] > 0.01].sort_values('total_jobs', ascending=False)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_colwidth', 60)

print(df_nonzero.to_string(index=False))
print()

print("="*80)
print("SUMMARY")
print("="*80)
print()
print(f"Total jobs: {df_final['total_jobs'].sum():.2f}")
print(f"Direct: {df_final['direct_jobs'].sum():.2f} ({df_final['direct_jobs'].sum()/df_final['total_jobs'].sum()*100:.1f}%)")
print(f"Indirect: {df_final['indirect_jobs'].sum():.2f} ({df_final['indirect_jobs'].sum()/df_final['total_jobs'].sum()*100:.1f}%)")
print()

print("Top 3 sectors:")
for _, row in df_final.nlargest(3, 'total_jobs').iterrows():
    print(f"  {row['sector_code']}: {row['sector_name'][:45]}")
    print(f"    {row['total_jobs']:.2f} jobs ({row['share_of_total_jobs']*100:.1f}%)")
print()

print("="*80)
print("TEST COMPLETE - Structure confirmed!")
print("="*80)
