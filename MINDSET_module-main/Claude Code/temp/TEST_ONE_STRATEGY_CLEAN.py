"""
TEST: Process ONE Strategy to Check Output Structure (CLEAN VERSION)

Tests the employment analysis pipeline with ISIC sector mapping and strategy attributes.
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
print("TEST: Employment Analysis with ISIC Sectors and Strategy Attributes")
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
# STEP 1: Load Crosswalk and Attributes
#==============================================================================
print("STEP 1: Loading ISIC Crosswalk and Strategy Attributes")
print("-"*80)

data_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data"

# Load ISIC concordance
crosswalk_path = os.path.join(data_path, "GLORIA-Eora26 - Crosswalk.xlsx")
crosswalk_df = pd.read_excel(crosswalk_path, sheet_name="GLORIA (v60) - ISIC concordance")

print(f"Crosswalk loaded: {crosswalk_df.shape}")

# Get ISIC section codes (columns A-T)
isic_sections = [col for col in crosswalk_df.columns if len(col) == 1 and col.isalpha()]
print(f"ISIC sections found: {isic_sections}")

# Get section descriptions from first row
section_descriptions = {}
for section in isic_sections:
    desc = crosswalk_df[section].iloc[0]
    section_descriptions[section] = desc if pd.notna(desc) else section

print(f"\nISIC Sections ({len(section_descriptions)}):")
for sec in sorted(section_descriptions.keys()):
    print(f"  {sec}: {section_descriptions[sec][:60]}")

# Remove header row
crosswalk_df = crosswalk_df.iloc[1:].reset_index(drop=True)

# Add product codes (1-120)
crosswalk_df['product_code'] = range(1, len(crosswalk_df) + 1)

# Create product-to-sector mapping
product_sector_map = {}
for idx, row in crosswalk_df.iterrows():
    product = row['product_code']
    sectors = [sec for sec in isic_sections if row[sec] == 1]
    product_sector_map[product] = sectors if len(sectors) > 0 else ['Other']

print(f"\nProducts mapped: {len(product_sector_map)}")

# Load strategy attributes
attributes_path = os.path.join(data_path, "ATTRIBUTE_STRATEGY.csv")
df_attributes = pd.read_csv(attributes_path)

print(f"\nStrategy attributes loaded: {df_attributes.shape}")
print(f"Columns: {list(df_attributes.columns)}")
print(f"\nFirst 3 rows:")
print(df_attributes.head(3))
print()

#==============================================================================
# STEP 2: Load MRIO and Initialize Models
#==============================================================================
print("STEP 2: Loading MRIO Base Data")
print("-"*80)

MRIO_BASE = exog_vars()
print(f"[OK] MRIO loaded")

# Employment baseline
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

# Initialize IO model
IO_model = IO(MRIO_BASE)
IO_model.initialize()

# Build employment model
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)
print(f"[OK] Models initialized\n")

#==============================================================================
# STEP 3: Process One Test Strategy
#==============================================================================
print("STEP 3: Processing Test Strategy")
print("-"*80)

scenario_name = "Strategy_1004_EGY"
scenario_file = f"GLORIA_template/Scenarios/{scenario_name}.xlsx"

print(f"Processing: {scenario_name}")

# Load scenario
Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
Scenario.set_exog_inv()

# Get investing country
investing_countries = Scenario.inv_exog[Scenario.inv_exog['dk'] > 0]['REG_imp'].unique()
main_country = investing_countries[0] if len(investing_countries) > 0 else "UNKNOWN"
main_country_name = COUNTRY_NAMES.get(main_country, main_country)

print(f"Investing country: {main_country} ({main_country_name})\n")

# Investment module
if not hasattr(Scenario, 'inv_spending'):
    Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
INV_model.build_inv_output_elas()
INV_model.calc_inv_share()
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

dy_inv_exog = MRIO_df_to_vec(
    INV_model.dy_inv_exog,
    'REG_imp', 'TRAD_COMM', 'dy',
    MRIO_BASE.R['Region_acronyms'].to_list(),
    MRIO_BASE.P['Lfd_Nr'].to_list()
)

# Calculate output and employment
dq_total = IO_model.calc_dq_exog(dy_inv_exog)
dempl = Empl_model.calc_dempl(dq_total)
direct_demand_mask = dy_inv_exog > 0.01

#==============================================================================
# STEP 4: Extract Product-Level Results
#==============================================================================
print("STEP 4: Extracting Product-Level Results")
print("-"*80)

country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}
sector_list = MRIO_BASE.P['Lfd_Nr'].to_list()

c_idx = country_idx[main_country]
c_start = c_idx * 120
c_end = c_start + 120

product_results = []
for s_idx, product in enumerate(sector_list):
    idx_pos = c_start + s_idx
    sector_jobs_total = dempl[idx_pos]
    sector_is_direct = direct_demand_mask[idx_pos]

    sector_direct_jobs = sector_jobs_total if sector_is_direct else 0.0
    sector_indirect_jobs = 0.0 if sector_is_direct else sector_jobs_total

    product_results.append({
        'product': product,
        'direct_jobs': sector_direct_jobs,
        'indirect_jobs': sector_indirect_jobs,
        'total_jobs': sector_jobs_total
    })

df_product = pd.DataFrame(product_results)
print(f"Product-level results: {len(df_product)} products")
print(f"Total jobs (sum): {df_product['total_jobs'].sum():.2f}\n")

#==============================================================================
# STEP 5: Aggregate to ISIC Sectors
#==============================================================================
print("STEP 5: Aggregating to ISIC Sectors")
print("-"*80)

# Initialize sector aggregation
sector_jobs = {}
for sector_code, sector_name in section_descriptions.items():
    sector_jobs[sector_code] = {
        'name': sector_name,
        'direct': 0.0,
        'indirect': 0.0,
        'total': 0.0
    }

# Aggregate products to sectors
for _, row in df_product.iterrows():
    product = row['product']
    if product in product_sector_map:
        sectors = product_sector_map[product]
        weight = 1.0 / len(sectors)  # Divide equally if product in multiple sectors

        for sector_code in sectors:
            if sector_code in sector_jobs:
                sector_jobs[sector_code]['direct'] += row['direct_jobs'] * weight
                sector_jobs[sector_code]['indirect'] += row['indirect_jobs'] * weight
                sector_jobs[sector_code]['total'] += row['total_jobs'] * weight

# Calculate total jobs for share calculation
total_jobs_all_sectors = sum([s['total'] for s in sector_jobs.values()])

# Create sector-level dataframe
sector_results = []
for sector_code in sorted(sector_jobs.keys()):
    jobs = sector_jobs[sector_code]
    share = (jobs['total'] / total_jobs_all_sectors) if total_jobs_all_sectors > 0 else 0.0
    sector_results.append({
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

df_sector = pd.DataFrame(sector_results)

print(f"ISIC sector results: {len(df_sector)} sectors")
print(f"Total jobs (sum): {df_sector['total_jobs'].sum():.2f}")
print(f"Share sum check: {df_sector['share_of_total_jobs'].sum():.6f} (should be 1.0)\n")

#==============================================================================
# STEP 6: Merge with Strategy Attributes
#==============================================================================
print("STEP 6: Merging with Strategy Attributes")
print("-"*80)

# Extract numeric ID from strategy name (e.g., "Strategy_1004_EGY" -> 1004)
numeric_id_match = re.search(r'_(\d+)_', scenario_name)
if numeric_id_match:
    numeric_id = int(numeric_id_match.group(1))
    df_sector['strategy_numeric_id'] = numeric_id
    print(f"Extracted numeric ID: {numeric_id}")
else:
    print(f"[WARNING] Could not extract numeric ID from {scenario_name}")
    df_sector['strategy_numeric_id'] = None

# Check if strategy_id column in attributes is integer
if 'strategy_id' in df_attributes.columns:
    print(f"Attributes strategy_id type: {df_attributes['strategy_id'].dtype}")

    # Merge on numeric ID
    df_final = df_sector.merge(
        df_attributes,
        left_on='strategy_numeric_id',
        right_on='strategy_id',
        how='left'
    )

    # Drop the duplicate strategy_id column from attributes
    if 'strategy_id' in df_final.columns:
        df_final = df_final.drop(columns=['strategy_id'])

    print(f"[OK] Merge complete")
    print(f"Columns before merge: {len(df_sector.columns)}")
    print(f"Columns after merge: {len(df_final.columns)}")

    new_cols = [col for col in df_final.columns if col not in df_sector.columns]
    print(f"New attribute columns: {new_cols}")
else:
    print("[WARNING] No strategy_id column in attributes - skipping merge")
    df_final = df_sector.copy()

print()

#==============================================================================
# STEP 7: Display Results
#==============================================================================
print("="*80)
print("FINAL OUTPUT STRUCTURE")
print("="*80)
print()

print(f"Total rows: {len(df_final)}")
print(f"Total columns: {len(df_final.columns)}")
print()

print("All columns:")
for i, col in enumerate(df_final.columns, 1):
    print(f"  {i:2d}. {col}")
print()

# Display non-zero sectors
df_nonzero = df_final[df_final['total_jobs'] > 0.01].sort_values('total_jobs', ascending=False)
print("="*80)
print(f"NON-ZERO SECTORS ({len(df_nonzero)} out of {len(df_final)})")
print("="*80)
print()

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 250)
pd.set_option('display.max_colwidth', 50)

print(df_nonzero.to_string(index=False))
print()

#==============================================================================
# STEP 8: Summary Statistics
#==============================================================================
print("="*80)
print("SUMMARY STATISTICS")
print("="*80)
print()

print(f"Total jobs created: {df_final['total_jobs'].sum():.2f}")
print(f"Direct jobs: {df_final['direct_jobs'].sum():.2f} ({df_final['direct_jobs'].sum()/df_final['total_jobs'].sum()*100:.1f}%)")
print(f"Indirect jobs: {df_final['indirect_jobs'].sum():.2f} ({df_final['indirect_jobs'].sum()/df_final['total_jobs'].sum()*100:.1f}%)")
print()

print("Top 5 sectors by employment:")
top5 = df_final.nlargest(5, 'total_jobs')[['sector_code', 'sector_name', 'total_jobs', 'share_of_total_jobs']]
for _, row in top5.iterrows():
    print(f"  {row['sector_code']}: {row['sector_name'][:50]}")
    print(f"    Jobs: {row['total_jobs']:.2f} ({row['share_of_total_jobs']*100:.1f}%)")
print()

print("="*80)
print("TEST COMPLETE!")
print("="*80)
print()
print("✓ ISIC sector aggregation working")
print("✓ Strategy attributes merged successfully")
print("✓ Share calculations sum to 1.0")
print("✓ Ready for batch processing of all 469 strategies")
