"""
BATCH EMPLOYMENT ANALYSIS - ALL 469 STRATEGIES
===============================================

Processes all Strategy files and generates consolidated employment estimates.

LOCATION: This script should be placed in "SSP - Codes" folder
RUN FROM: MINDSET_module-main root directory

OUTPUT:
- employment_consolidated.csv in SSP - Results folder
- Contains all 7 countries (BGR, BLZ, EGY, LBY, MAR, MEX, UGA)
- ROW excluded per user request
- All 20 ISIC sectors per strategy (including zeros)
- Strategy attributes merged

Columns:
1. country_name
2. country_ISO
3. strategy_id
4. strategy_name
5. sector_code
6. sector_name
7. direct_jobs
8. indirect_jobs
9. total_jobs
10. share_of_total_jobs

Author: Claude Code
Date: 2026-03-22
"""

import sys
import os
import time
import re
import numpy as np
import pandas as pd
from glob import glob

# Setup paths - works whether run from root or from SSP - Codes folder
script_dir = os.path.dirname(os.path.abspath(__file__))

# Check if we're in SSP - Codes folder
if os.path.basename(script_dir) == 'SSP - Codes':
    # Script is in SSP - Codes, go up one level to MINDSET_module-main
    mindset_root = os.path.abspath(os.path.join(script_dir, ".."))
elif os.path.basename(script_dir) == 'temp':
    # Script is in Claude Code\temp, go up two levels
    mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
else:
    # Assume we're already at root
    mindset_root = script_dir

sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("="*80)
print("BATCH EMPLOYMENT ANALYSIS - ALL 469 STRATEGIES")
print("="*80)
print()
print(f"Working directory: {os.getcwd()}")
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

# Country name mapping (excluding ROW per user request)
COUNTRY_NAMES = {
    'BGR': 'Bulgaria',
    'BLZ': 'Belize',
    'EGY': 'Egypt',
    'LBY': 'Libya',
    'MAR': 'Morocco',
    'MEX': 'Mexico',
    'UGA': 'Uganda'
}

#==============================================================================
# STEP 1: Load Crosswalk and Strategy Attributes
#==============================================================================
print("STEP 1: Loading ISIC Crosswalk and Strategy Attributes")
print("-"*80)

# Absolute path to data folder (won't break regardless of where script is)
data_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data"

# Load ISIC concordance
crosswalk_path = os.path.join(data_path, "GLORIA-Eora26 - Crosswalk.xlsx")
if not os.path.exists(crosswalk_path):
    print(f"[ERROR] Crosswalk file not found: {crosswalk_path}")
    sys.exit(1)

crosswalk_df = pd.read_excel(crosswalk_path, sheet_name="GLORIA (v60) - ISIC concordance")

print(f"[OK] Crosswalk loaded: {crosswalk_df.shape}")

# Get ISIC section codes (A-T)
isic_sections = [col for col in crosswalk_df.columns if len(col) == 1 and col.isalpha()]

# Get section descriptions from first row
section_descriptions = {}
for section in isic_sections:
    desc = crosswalk_df[section].iloc[0]
    section_descriptions[section] = desc if pd.notna(desc) else section

print(f"  ISIC sections: {len(section_descriptions)}")

# Remove header row and create mapping
crosswalk_df = crosswalk_df.iloc[1:].reset_index(drop=True)
crosswalk_df['product_code'] = range(1, len(crosswalk_df) + 1)

# Create product-to-sector mapping
product_sector_map = {}
for idx, row in crosswalk_df.iterrows():
    product = row['product_code']
    sectors = [sec for sec in isic_sections if row[sec] == 1]
    product_sector_map[product] = sectors if len(sectors) > 0 else ['Other']

print(f"  Products mapped: {len(product_sector_map)}")

# Load strategy attributes
attributes_path = os.path.join(data_path, "ATTRIBUTE_STRATEGY.csv")
if not os.path.exists(attributes_path):
    print(f"[ERROR] Strategy attributes file not found: {attributes_path}")
    sys.exit(1)

df_attributes = pd.read_csv(attributes_path)

print(f"[OK] Strategy attributes loaded: {df_attributes.shape}")
print(f"  Columns: {list(df_attributes.columns)}")
print()

#==============================================================================
# STEP 2: Find all Strategy files
#==============================================================================
print("STEP 2: Finding all Strategy files")
print("-"*80)

# Relative path from MINDSET_module-main root
scenario_pattern = "GLORIA_template/Scenarios/Strategy_*.xlsx"
scenario_files = sorted(glob(scenario_pattern))

print(f"[OK] Found {len(scenario_files)} Strategy files")

if len(scenario_files) == 0:
    print("[ERROR] No Strategy files found!")
    print(f"  Searched: {os.path.abspath(scenario_pattern)}")
    print(f"  Current directory: {os.getcwd()}")
    sys.exit(1)

print(f"  Sample: {scenario_files[0]}")
print()

#==============================================================================
# STEP 3: Load MRIO Base Data (once)
#==============================================================================
print("STEP 3: Loading MRIO Base Data (one time)")
print("-"*80)

start_time = time.time()
MRIO_BASE = exog_vars()

print(f"[OK] MRIO data loaded in {time.time() - start_time:.1f} seconds")
print(f"  Countries: {', '.join(MRIO_BASE.COU_ID)}")
print(f"  Products: {len(MRIO_BASE.SEC_ID)}")
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

# Initialize IO model
print("Initializing IO model...")
IO_model = IO(MRIO_BASE)
IO_model.initialize()
print(f"[OK] IO model initialized")

# Build employment model
print("Building employment model...")
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)
print(f"[OK] Employment model ready")
print()

#==============================================================================
# STEP 4: Process each Strategy file
#==============================================================================
print("STEP 4: Processing all Strategy files")
print("-"*80)
print()

all_results = []
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
        print(f"[{idx}/{len(scenario_files)}] {scenario_name} "
              f"(~{remaining/60:.1f} min remaining)")

    try:
        # Load scenario
        Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
        Scenario.set_exog_inv()

        # Get investing country
        investing_countries = Scenario.inv_exog[Scenario.inv_exog['dk'] > 0]['REG_imp'].unique()
        main_country = investing_countries[0] if len(investing_countries) > 0 else "UNKNOWN"

        # Skip if ROW (per user request to exclude ROW)
        if main_country == 'ROW':
            continue

        # Skip if country not in our list
        if main_country not in COUNTRY_NAMES:
            continue

        main_country_name = COUNTRY_NAMES[main_country]

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

        # Direct vs indirect mask
        direct_demand_mask = dy_inv_exog > 0.01

        # Focus on investing country only
        if main_country in country_idx:
            c_idx = country_idx[main_country]
            c_start = c_idx * 120
            c_end = c_start + 120

            # Extract product-level employment
            product_results = []
            for s_idx, product in enumerate(sector_list):
                idx_pos = c_start + s_idx
                total_jobs = dempl[idx_pos]
                is_direct = direct_demand_mask[idx_pos]

                product_results.append({
                    'product': product,
                    'direct_jobs': total_jobs if is_direct else 0.0,
                    'indirect_jobs': 0.0 if is_direct else total_jobs,
                    'total_jobs': total_jobs
                })

            # Aggregate to ISIC sectors
            sector_jobs = {}
            for sec in section_descriptions.keys():
                sector_jobs[sec] = {'name': section_descriptions[sec], 'direct': 0.0, 'indirect': 0.0, 'total': 0.0}

            for prod_row in product_results:
                product = prod_row['product']
                if product in product_sector_map:
                    sectors = product_sector_map[product]
                    weight = 1.0 / len(sectors)

                    for sec in sectors:
                        if sec in sector_jobs:
                            sector_jobs[sec]['direct'] += prod_row['direct_jobs'] * weight
                            sector_jobs[sec]['indirect'] += prod_row['indirect_jobs'] * weight
                            sector_jobs[sec]['total'] += prod_row['total_jobs'] * weight

            # Calculate total for share
            total_jobs_all = sum([s['total'] for s in sector_jobs.values()])

            # Save results for all sectors (including zeros)
            for sector_code in sorted(sector_jobs.keys()):
                jobs = sector_jobs[sector_code]
                share = jobs['total'] / total_jobs_all if total_jobs_all > 0 else 0.0

                all_results.append({
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
# STEP 5: Create Final Consolidated Dataset
#==============================================================================
print("STEP 5: Creating Final Consolidated Dataset")
print("-"*80)

if len(all_results) == 0:
    print("[ERROR] No results to save!")
    sys.exit(1)

df_consolidated = pd.DataFrame(all_results)

# Extract numeric ID from strategy names
df_consolidated['strategy_numeric_id'] = df_consolidated['strategy_id'].apply(
    lambda x: int(re.search(r'_(\d+)_', x).group(1)) if re.search(r'_(\d+)_', x) else None
)

# Merge with strategy attributes
df_consolidated = df_consolidated.merge(
    df_attributes.rename(columns={'strategy': 'strategy_name'}),
    left_on='strategy_numeric_id',
    right_on='strategy_id',
    how='left',
    suffixes=('', '_attr')
)

# Drop merge artifacts
cols_to_drop = [col for col in df_consolidated.columns if col in ['strategy_numeric_id', 'strategy_id_attr']]
df_consolidated = df_consolidated.drop(columns=cols_to_drop)

# Final column order
final_cols = ['country_name', 'country_ISO', 'strategy_id', 'strategy_name',
              'sector_code', 'sector_name', 'direct_jobs', 'indirect_jobs',
              'total_jobs', 'share_of_total_jobs']

df_consolidated = df_consolidated[final_cols]

print(f"[OK] Dataset created")
print(f"  Total rows: {len(df_consolidated):,}")
print(f"  Unique strategies: {df_consolidated['strategy_id'].nunique()}")
print(f"  Countries: {sorted(df_consolidated['country_ISO'].unique())}")
print()

# Validate share sums
share_check = df_consolidated.groupby(['country_ISO', 'strategy_id'])['share_of_total_jobs'].sum()
print(f"[VALIDATION] Share sum check:")
print(f"  Mean: {share_check.mean():.6f} (should be 1.0)")
print(f"  Min: {share_check.min():.6f}, Max: {share_check.max():.6f}")
print()

#==============================================================================
# STEP 6: Save Results
#==============================================================================
print("STEP 6: Saving Results")
print("-"*80)

# Output directory - relative to MINDSET_module-main root
output_dir = "SSP - Results"
os.makedirs(output_dir, exist_ok=True)

# Save main consolidated file
output_file = os.path.join(output_dir, "employment_consolidated.csv")
df_consolidated.to_csv(output_file, index=False)

print(f"[OK] SAVED: {output_file}")
print(f"  Full path: {os.path.abspath(output_file)}")
print(f"  Rows: {len(df_consolidated):,}")
print(f"  Columns: {len(df_consolidated.columns)}")
print()

# Save error log if any
if len(errors) > 0:
    error_file = os.path.join(output_dir, "processing_errors.txt")
    with open(error_file, 'w') as f:
        f.write("PROCESSING ERRORS\n")
        f.write("="*80 + "\n\n")
        for error in errors:
            f.write(f"{error}\n")
    print(f"[WARNING] Errors logged to: {error_file}")
    print()

#==============================================================================
# STEP 7: Summary Statistics
#==============================================================================
print("="*80)
print("SUMMARY STATISTICS")
print("="*80)
print()

# Overall statistics
print("Dataset Overview:")
print(f"  Total rows: {len(df_consolidated):,}")
print(f"  Strategies: {df_consolidated['strategy_id'].nunique()}")
print(f"  Countries: {df_consolidated['country_ISO'].nunique()} (excl. ROW)")
print(f"  ISIC sectors: {df_consolidated['sector_code'].nunique()}")
print()

# Jobs summary
total_jobs = df_consolidated.groupby(['country_ISO', 'strategy_id'])['total_jobs'].sum()
print("Total Jobs per Strategy:")
print(f"  Mean:   {total_jobs.mean():.1f}")
print(f"  Median: {total_jobs.median():.1f}")
print(f"  Min:    {total_jobs.min():.1f}")
print(f"  Max:    {total_jobs.max():.1f}")
print()

# Direct vs Indirect
strategy_agg = df_consolidated.groupby(['country_ISO', 'strategy_id']).agg({
    'direct_jobs': 'sum',
    'indirect_jobs': 'sum',
    'total_jobs': 'sum'
}).reset_index()

total_direct = strategy_agg['direct_jobs'].sum()
total_indirect = strategy_agg['indirect_jobs'].sum()
total_all = strategy_agg['total_jobs'].sum()

print("Direct vs Indirect Jobs (all strategies):")
print(f"  Total Direct:   {total_direct:,.0f} ({total_direct/total_all*100:.1f}%)")
print(f"  Total Indirect: {total_indirect:,.0f} ({total_indirect/total_all*100:.1f}%)")
print()

# By country
print("By Country:")
country_stats = strategy_agg.groupby('country_ISO').agg({
    'total_jobs': ['mean', 'sum'],
    'direct_jobs': 'mean',
    'indirect_jobs': 'mean',
    'strategy_id': 'count'
}).round(1)

for country_iso in sorted(COUNTRY_NAMES.keys()):
    if country_iso in country_stats.index:
        row = country_stats.loc[country_iso]
        country_name = COUNTRY_NAMES[country_iso]
        print(f"  {country_iso} ({country_name}):")
        print(f"    Mean jobs per strategy: {row[('total_jobs', 'mean')]:.1f}")
        print(f"    Total jobs all strategies: {row[('total_jobs', 'sum')]:,.0f}")
        print(f"    Number of strategies: {int(row[('strategy_id', 'count')])}")
print()

# Top sectors
print("Most job-intensive sectors (all strategies):")
sector_totals = df_consolidated.groupby('sector_name')['total_jobs'].sum().sort_values(ascending=False).head(10)
for sector, jobs in sector_totals.items():
    print(f"  {sector[:50]}: {jobs:,.0f} jobs")
print()

print("="*80)
print("OUTPUT FILE READY")
print("="*80)
print()
print(f"Location: {output_file}")
print(f"Full path: {os.path.abspath(output_file)}")
print()
print("File structure:")
print("  - country_name: Full country name")
print("  - country_ISO: 3-letter code (BGR, BLZ, EGY, LBY, MAR, MEX, UGA)")
print("  - strategy_id: Full strategy name (e.g., Strategy_1004_EGY)")
print("  - strategy_name: Strategy description from attributes")
print("  - sector_code: ISIC section code (A-T)")
print("  - sector_name: ISIC sector description")
print("  - direct_jobs: Direct employment")
print("  - indirect_jobs: Indirect/supply chain employment")
print("  - total_jobs: Total employment (direct + indirect)")
print("  - share_of_total_jobs: Sector share (sums to 1.0 per strategy)")
print()
print("  - ALL 20 ISIC sectors included per strategy (including zeros)")
print("  - ROW excluded per request")
print("  - Ready for dissertation analysis")
print()
print("="*80)
