"""
BATCH EMPLOYMENT ANALYSIS - ALL 469 STRATEGY FILES (FINAL VERSION)

Processes all Strategy files and generates employment estimates using MINDSET methodology.

KEY FEATURES:
- Maps 120 GLORIA products to ISIC economic sectors
- Direct vs Indirect employment decomposition
- ALL ISIC sectors included for each strategy (even zeros)
- Share of total jobs calculated per sector
- Results filtered to investing country only
- Merges with ATTRIBUTE_STRATEGY.csv for strategy names/attributes

MAIN OUTPUT:
employment_consolidated.csv with columns:
- country_name, country_ISO, strategy_id, strategy attributes
- sector_code, sector_name
- direct_jobs, indirect_jobs, total_jobs
- share_of_total_jobs (sector jobs / total jobs for that strategy-country)

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

# Country name mapping
COUNTRY_NAMES = {
    'ROW': 'Rest of World',
    'BGR': 'Bulgaria',
    'BLZ': 'Belize',
    'EGY': 'Egypt',
    'LBY': 'Libya',
    'MAR': 'Morocco',
    'MEX': 'Mexico',
    'UGA': 'Uganda'
}

#==============================================================================
# STEP 0: Load Product-to-Sector Crosswalk and Strategy Attributes
#==============================================================================
print("STEP 0: Loading Data Mappings")
print("-"*80)

# Path to data files
data_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data"
crosswalk_path = os.path.join(data_path, "GLORIA-Eora26 - Crosswalk.xlsx")
attributes_path = os.path.join(data_path, "ATTRIBUTE_STRATEGY.csv")

# Load Product-to-ISIC Sector Crosswalk
try:
    # Load ISIC concordance mapping 120 GLORIA products to ISIC sectors
    crosswalk_df = pd.read_excel(crosswalk_path, sheet_name="GLORIA (v60) - ISIC concordance")

    print(f"[OK] ISIC concordance loaded: {crosswalk_df.shape}")
    print(f"  Columns: {list(crosswalk_df.columns)}")

    # Identify product and sector columns
    # Expected columns might be: 'Lfd_Nr', 'Product', 'ISIC_Code', 'ISIC_Section', 'ISIC_Description', etc.
    product_col = None
    sector_code_col = None
    sector_name_col = None

    for col in crosswalk_df.columns:
        if 'Lfd' in col or 'lfd' in col or col == 'Product_Code':
            product_col = col
        elif 'ISIC_Section' in col or 'Section' in col:
            sector_code_col = col
        elif 'ISIC_Description' in col or 'Section_Description' in col or 'Description' in col:
            sector_name_col = col

    # Fallback to first few columns if not found
    if product_col is None:
        product_col = crosswalk_df.columns[0]
        print(f"  [WARNING] Using first column as product: {product_col}")
    if sector_code_col is None:
        sector_code_col = [col for col in crosswalk_df.columns if 'ISIC' in col or 'Section' in col][0] if any('ISIC' in col or 'Section' in col for col in crosswalk_df.columns) else crosswalk_df.columns[1]
        print(f"  [WARNING] Using column as sector code: {sector_code_col}")
    if sector_name_col is None:
        sector_name_col = sector_code_col  # Use same as code if name not found

    print(f"  Mapping: {product_col} -> {sector_code_col} ({sector_name_col})")
    print(f"  Sample mapping:")
    print(crosswalk_df[[product_col, sector_code_col, sector_name_col]].head(10))
    print()

    # Create product-to-sector mapping
    product_sector_map = {}
    for _, row in crosswalk_df.iterrows():
        product = row[product_col]
        sector_code = row[sector_code_col]
        sector_name = row[sector_name_col] if sector_name_col in row.index else sector_code

        # Handle NaN or missing values
        if pd.notna(product) and pd.notna(sector_code):
            product_sector_map[product] = {
                'code': sector_code,
                'name': sector_name
            }

    # Get unique sector list
    all_sectors = {}
    for mapping in product_sector_map.values():
        all_sectors[mapping['code']] = mapping['name']

    print(f"  Total products mapped: {len(product_sector_map)}")
    print(f"  Total unique ISIC sectors: {len(all_sectors)}")
    print(f"  Sectors: {list(all_sectors.keys())[:10]}...")
    print()

except Exception as e:
    print(f"[ERROR] Could not load ISIC concordance: {e}")
    print(f"  Tried: {crosswalk_path}")
    print("  Falling back to product-level analysis (120 products)")
    product_sector_map = None
    all_sectors = None
    print()

# Load Strategy Attributes
try:
    df_attributes = pd.read_csv(attributes_path)
    print(f"[OK] Strategy attributes loaded: {df_attributes.shape}")
    print(f"  Columns: {list(df_attributes.columns)}")

    # Identify strategy ID column
    strategy_id_col = None
    for col in df_attributes.columns:
        if 'strategy' in col.lower() and ('id' in col.lower() or 'name' in col.lower()):
            strategy_id_col = col
            break

    if strategy_id_col is None:
        strategy_id_col = df_attributes.columns[0]
        print(f"  [WARNING] Using first column as strategy ID: {strategy_id_col}")

    print(f"  Strategy ID column: {strategy_id_col}")
    print(f"  Sample records:")
    print(df_attributes.head())
    print()

except Exception as e:
    print(f"[ERROR] Could not load strategy attributes: {e}")
    print(f"  Tried: {attributes_path}")
    print("  Will proceed without strategy attributes")
    df_attributes = None
    strategy_id_col = None
    print()

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
print(f"  Countries: {', '.join([f'{c} ({COUNTRY_NAMES[c]})' for c in MRIO_BASE.COU_ID])}")
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
all_results_product = []  # Product-level (before sector aggregation)

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
        main_country_name = COUNTRY_NAMES.get(main_country, main_country)

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

        # Calculate direct vs indirect employment (global)
        direct_demand_mask = dy_inv_exog > 0.01

        # Focus on investing country only
        if main_country in country_idx:
            c_idx = country_idx[main_country]
            c_start = c_idx * 120
            c_end = c_start + 120

            # Product-level detail: ALL 120 products
            for s_idx, product in enumerate(sector_list):
                idx_pos = c_start + s_idx
                sector_demand = dy_inv_exog[idx_pos]
                sector_output = dq_total[idx_pos]
                sector_jobs_total = dempl[idx_pos]
                sector_is_direct = direct_demand_mask[idx_pos]

                # Separate direct and indirect
                if sector_is_direct:
                    sector_direct_jobs = sector_jobs_total
                    sector_indirect_jobs = 0.0
                else:
                    sector_direct_jobs = 0.0
                    sector_indirect_jobs = sector_jobs_total

                # Save product-level results (will aggregate to sectors later)
                all_results_product.append({
                    'country_name': main_country_name,
                    'country_ISO': main_country,
                    'strategy_id': scenario_name,
                    'product': product,
                    'direct_jobs': sector_direct_jobs,
                    'indirect_jobs': sector_indirect_jobs,
                    'total_jobs': sector_jobs_total
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
# STEP 4: Aggregate Products to ISIC Sectors
#==============================================================================
print("STEP 4: Aggregating Products to ISIC Economic Sectors")
print("-"*80)

df_product = pd.DataFrame(all_results_product)

if product_sector_map is not None:
    # Map products to ISIC sectors and aggregate
    sector_results = []

    for (country_name, country_iso, strategy_id), group in df_product.groupby(['country_name', 'country_ISO', 'strategy_id']):
        # Initialize sector aggregation
        sector_jobs = {}
        for sector_code, sector_name in all_sectors.items():
            sector_jobs[sector_code] = {
                'name': sector_name,
                'direct': 0.0,
                'indirect': 0.0,
                'total': 0.0
            }

        # Aggregate products to sectors
        for _, row in group.iterrows():
            product = row['product']

            if product in product_sector_map:
                sector_info = product_sector_map[product]
                sector_code = sector_info['code']

                # Aggregate to sector
                if sector_code in sector_jobs:
                    sector_jobs[sector_code]['direct'] += row['direct_jobs']
                    sector_jobs[sector_code]['indirect'] += row['indirect_jobs']
                    sector_jobs[sector_code]['total'] += row['total_jobs']
            else:
                # Product not in mapping - add to "Others" or skip
                if 'Others' not in sector_jobs:
                    sector_jobs['Others'] = {'name': 'Others', 'direct': 0.0, 'indirect': 0.0, 'total': 0.0}
                sector_jobs['Others']['direct'] += row['direct_jobs']
                sector_jobs['Others']['indirect'] += row['indirect_jobs']
                sector_jobs['Others']['total'] += row['total_jobs']

        # Calculate total jobs for this strategy-country (for share calculation)
        total_jobs_all_sectors = sum([s['total'] for s in sector_jobs.values()])

        # Save sector-level results
        for sector_code, jobs in sector_jobs.items():
            share = (jobs['total'] / total_jobs_all_sectors) if total_jobs_all_sectors > 0 else 0.0

            sector_results.append({
                'country_name': country_name,
                'country_ISO': country_iso,
                'strategy_id': strategy_id,
                'sector_code': sector_code,
                'sector_name': jobs['name'],
                'direct_jobs': jobs['direct'],
                'indirect_jobs': jobs['indirect'],
                'total_jobs': jobs['total'],
                'share_of_total_jobs': share
            })

    df_consolidated = pd.DataFrame(sector_results)
    print(f"[OK] Aggregated to {len(all_sectors)} ISIC sectors")
    print(f"     Final rows: {len(df_consolidated):,} ({processed_count} strategies × {len(all_sectors)} sectors)")

else:
    # Fallback: Use product-level data
    print("[WARNING] Using product-level data (120 products) - no sector aggregation")

    df_consolidated = df_product.copy()
    df_consolidated['sector_code'] = df_consolidated['product']
    df_consolidated['sector_name'] = 'Product_' + df_consolidated['product'].astype(str)

    # Calculate share of total jobs
    total_by_strategy = df_consolidated.groupby(['country_ISO', 'strategy_id'])['total_jobs'].transform('sum')
    df_consolidated['share_of_total_jobs'] = df_consolidated['total_jobs'] / total_by_strategy
    df_consolidated['share_of_total_jobs'] = df_consolidated['share_of_total_jobs'].fillna(0)

print()

#==============================================================================
# STEP 5: Merge with Strategy Attributes
#==============================================================================
print("STEP 5: Merging with Strategy Attributes")
print("-"*80)

if df_attributes is not None:
    try:
        # Try to match strategy_id column
        # Strategy files are named like "Strategy_1004_MEX", attributes might be "Strategy_1004_MEX" or just "1004" or "1004_MEX"

        # First, let's see if we can directly merge
        merge_key = 'strategy_id'

        # Check if strategy_id_col exists in df_attributes
        if strategy_id_col in df_attributes.columns:
            # Rename to match our column name
            df_attributes_merge = df_attributes.rename(columns={strategy_id_col: merge_key})
        else:
            df_attributes_merge = df_attributes.copy()
            # Assume first column is the key
            df_attributes_merge.columns = [merge_key] + list(df_attributes_merge.columns[1:])

        # Try merge
        before_cols = df_consolidated.columns.tolist()
        df_consolidated = df_consolidated.merge(
            df_attributes_merge,
            on=merge_key,
            how='left'
        )

        # Check merge success
        new_cols = [col for col in df_consolidated.columns if col not in before_cols]
        matched = df_consolidated[new_cols[0]].notna().sum() if len(new_cols) > 0 else 0

        print(f"[OK] Merged with strategy attributes")
        print(f"  New columns added: {new_cols}")
        print(f"  Matched strategies: {matched}/{processed_count}")

        if matched < processed_count * 0.8:  # Less than 80% matched
            print(f"  [WARNING] Low match rate - check strategy ID format")
            print(f"  Sample strategy_id from results: {df_consolidated['strategy_id'].iloc[0]}")
            print(f"  Sample strategy_id from attributes: {df_attributes_merge[merge_key].iloc[0]}")
        print()

    except Exception as e:
        print(f"[WARNING] Could not merge strategy attributes: {e}")
        print("  Proceeding without attributes")
        print()
else:
    print("[INFO] No strategy attributes to merge")
    print()

#==============================================================================
# STEP 6: Validate and Save Results
#==============================================================================
print("STEP 6: Validating and Saving Results")
print("-"*80)

output_dir = "Claude Code/temp/employment_results"
os.makedirs(output_dir, exist_ok=True)

# Validate share calculations sum to ~1.0 per strategy
share_check = df_consolidated.groupby(['country_ISO', 'strategy_id'])['share_of_total_jobs'].sum()
print(f"[VALIDATION] Share calculation check:")
print(f"  Mean sum of shares per strategy: {share_check.mean():.6f} (should be 1.0)")
print(f"  Min: {share_check.min():.6f}, Max: {share_check.max():.6f}")
print()

# Reorder columns to put key fields first
key_cols = ['country_name', 'country_ISO', 'strategy_id']
sector_cols = ['sector_code', 'sector_name']
job_cols = ['direct_jobs', 'indirect_jobs', 'total_jobs', 'share_of_total_jobs']
other_cols = [col for col in df_consolidated.columns if col not in key_cols + sector_cols + job_cols]

df_consolidated = df_consolidated[key_cols + other_cols + sector_cols + job_cols]

# Save main consolidated output
output_file = f"{output_dir}/employment_consolidated.csv"
df_consolidated.to_csv(output_file, index=False)
print(f"[OK] MAIN OUTPUT saved: {output_file}")
print(f"     Rows: {len(df_consolidated):,}")
print(f"     Columns: {list(df_consolidated.columns)}")
print()

# Save product-level data as well (for reference)
output_file_product = f"{output_dir}/employment_by_product_strategy.csv"
df_product.to_csv(output_file_product, index=False)
print(f"[OK] Product-level data saved: {output_file_product}")
print(f"     Rows: {len(df_product):,} (120 products per strategy)")
print()

# Error log
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
# STEP 7: Create Summary Excel File
#==============================================================================
print("STEP 7: Creating Excel Summary")
print("-"*80)

output_file = f"{output_dir}/employment_summary_consolidated.xlsx"
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

    # Sheet 1: Consolidated sector-level data
    df_consolidated.to_excel(writer, sheet_name='Employment_by_Sector', index=False)

    # Sheet 2: Summary by strategy (total jobs only)
    summary_cols = ['country_name', 'country_ISO', 'strategy_id'] + other_cols
    df_strategy_summary = df_consolidated.groupby(summary_cols).agg({
        'direct_jobs': 'sum',
        'indirect_jobs': 'sum',
        'total_jobs': 'sum'
    }).reset_index()
    df_strategy_summary.to_excel(writer, sheet_name='Strategy_Summary', index=False)

    # Sheet 3: Non-zero sectors only (for easier viewing)
    df_nonzero = df_consolidated[df_consolidated['total_jobs'] > 0.01]
    df_nonzero.to_excel(writer, sheet_name='Non_Zero_Sectors_Only', index=False)

    # Sheet 4: Top sectors by total jobs across all strategies
    top_sectors = df_consolidated.groupby('sector_name')['total_jobs'].sum().sort_values(ascending=False).head(15)
    top_sectors_df = pd.DataFrame({
        'sector': top_sectors.index,
        'total_jobs_all_strategies': top_sectors.values
    })
    top_sectors_df.to_excel(writer, sheet_name='Top_15_Sectors', index=False)

    # Sheet 5: Pivot - Total jobs by sector and country
    pivot_jobs = df_consolidated.pivot_table(
        index='sector_name',
        columns='country_ISO',
        values='total_jobs',
        aggfunc='sum',
        fill_value=0
    )
    pivot_jobs.to_excel(writer, sheet_name='Pivot_Jobs_by_Sector')

    # Sheet 6: Average sector shares (when active)
    df_active = df_consolidated[df_consolidated['total_jobs'] > 0.01]
    avg_shares = df_active.groupby('sector_name')['share_of_total_jobs'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    avg_shares.columns = ['avg_share', 'num_strategies']
    avg_shares.to_excel(writer, sheet_name='Avg_Sector_Shares')

print(f"[OK] Saved Excel summary: {output_file}")
print(f"     Sheets: 6 sheets with sector-level analysis")
print()

#==============================================================================
# STEP 8: Summary Statistics
#==============================================================================
print("="*80)
print("SUMMARY STATISTICS")
print("="*80)
print()

# Strategy-level aggregation
agg_cols = ['country_ISO', 'country_name', 'strategy_id'] + other_cols
df_strategy_agg = df_consolidated.groupby(agg_cols).agg({
    'direct_jobs': 'sum',
    'indirect_jobs': 'sum',
    'total_jobs': 'sum'
}).reset_index()

print("Total Jobs per Strategy:")
print(f"  Mean:   {df_strategy_agg['total_jobs'].mean():.1f}")
print(f"  Median: {df_strategy_agg['total_jobs'].median():.1f}")
print(f"  Min:    {df_strategy_agg['total_jobs'].min():.1f}")
print(f"  Max:    {df_strategy_agg['total_jobs'].max():.1f}")
print()

print("Direct vs Indirect Jobs (across all strategies):")
total_direct = df_strategy_agg['direct_jobs'].sum()
total_indirect = df_strategy_agg['indirect_jobs'].sum()
total_all = df_strategy_agg['total_jobs'].sum()
print(f"  Total Direct:   {total_direct:,.0f} ({total_direct/total_all*100:.1f}%)")
print(f"  Total Indirect: {total_indirect:,.0f} ({total_indirect/total_all*100:.1f}%)")
print()

print("By Country:")
country_stats = df_strategy_agg.groupby(['country_ISO', 'country_name']).agg({
    'total_jobs': ['mean', 'sum'],
    'direct_jobs': 'mean',
    'indirect_jobs': 'mean',
    'strategy_id': 'count'
}).round(1)

for (iso, name), row in country_stats.iterrows():
    print(f"  {iso} ({name}):")
    print(f"    Mean total jobs per strategy: {row[('total_jobs', 'mean')]:.1f}")
    print(f"    Mean direct: {row[('direct_jobs', 'mean')]:.1f}, Mean indirect: {row[('indirect_jobs', 'mean')]:.1f}")
    print(f"    Number of strategies: {int(row[('strategy_id', 'count')])}")
print()

print("Most job-intensive sectors (total jobs across all strategies):")
sector_totals = df_consolidated.groupby('sector_name')['total_jobs'].sum().sort_values(ascending=False).head(10)
for sector, jobs in sector_totals.items():
    strategies_with_sector = len(df_consolidated[(df_consolidated['sector_name'] == sector) & (df_consolidated['total_jobs'] > 0.01)])
    print(f"  {sector}: {jobs:,.0f} total jobs (active in {strategies_with_sector} strategies)")
print()

print("Sectors with highest average share (when active):")
df_active = df_consolidated[df_consolidated['total_jobs'] > 0.01]
avg_shares = df_active.groupby('sector_name')['share_of_total_jobs'].mean().sort_values(ascending=False).head(10)
for sector, avg_share in avg_shares.items():
    print(f"  {sector}: {avg_share*100:.1f}% average share (when active)")
print()

print("="*80)
print("OUTPUT FILES READY FOR ANALYSIS")
print("="*80)
print()
print(f"Location: {output_dir}/")
print()
print("MAIN OUTPUT FILE:")
print()
print("employment_consolidated.csv")
print(f"  - {len(df_consolidated):,} rows")
print("  - Key columns:")
print("    * country_name, country_ISO")
print("    * strategy_id + strategy attributes (if merged)")
print("    * sector_code, sector_name (ISIC sectors)")
print("    * direct_jobs, indirect_jobs, total_jobs")
print("    * share_of_total_jobs")
print()
print("  - ALL ISIC sectors included for each strategy (including zeros)")
print("  - share_of_total_jobs sums to 1.0 (100%) per strategy-country")
print("  - Results filtered to investing country only")
print()
print("SUPPLEMENTARY FILES:")
print()
print("employment_by_product_strategy.csv")
print("  - Product-level detail (120 products before sector aggregation)")
print()
print("employment_summary_consolidated.xlsx")
print("  - Multiple sheets with different views and analyses")
print()
print("="*80)
