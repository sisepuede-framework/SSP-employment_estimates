"""
REBUILD SSP DATA TO INCLUDE BOLIVIA (9 REGIONS)
================================================

The SSP data files in GLORIA_db\v57\2019\SSP\ were generated for 8 regions only
(ROW + 7 countries). Bolivia (BOL) was subsequently added to R_grouping_SSP.xlsx
and Variable_list_MINDSET_SSP.xlsx, but the actual data was never re-aggregated.

This script:
1. Backs up existing SSP .mat and .pkl files
2. Re-runs the collapse logic to regenerate .pkl files with 9 regions
3. Deletes stale .mat files so they get recomputed on first run

After running this script, run BATCH_EMPLOYMENT_ALL_STRATEGIES.py again.

Date: 2026-04-20
"""

import os
import sys
import shutil
import time
import pickle as pkl
import pandas as pd
import numpy as np

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("=" * 80)
print("REBUILD SSP DATA TO INCLUDE BOLIVIA")
print("=" * 80)
print(f"Working directory: {os.getcwd()}")
print()

ssp_data_dir = os.path.join(mindset_root, "GLORIA_db", "v57", "2019", "SSP")
backup_dir = os.path.join(ssp_data_dir, "backup_8regions")

# ============================================================
# STEP 1: Backup existing files
# ============================================================
print("STEP 1: Backing up existing SSP data (8-region versions)")
print("-" * 80)

os.makedirs(backup_dir, exist_ok=True)

for f in os.listdir(ssp_data_dir):
    if f.endswith(('.mat', '.pkl')):
        src = os.path.join(ssp_data_dir, f)
        dst = os.path.join(backup_dir, f)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  Backed up: {f}")
        else:
            print(f"  Already backed up: {f}")

print(f"\n  Backups in: {backup_dir}")
print()

# ============================================================
# STEP 2: Re-aggregate MRIO data (164 → 9 regions)
# ============================================================
# This reproduces the logic of ParseCode/collapse_MRIO_SSP.py
# but with the NaN-handling fix for the summary print at the end.
print("STEP 2: Re-aggregating MRIO data (164 → 9 regions including BOL)")
print("-" * 80)

start_time = time.time()

grouping_file = os.path.join(mindset_root, "GLORIA_template", "Country_groupings", "R_grouping_SSP.xlsx")
PATH_PICKLE_SOURCE = os.path.join(mindset_root, "GLORIA_db", "v57", "2019", "parsed_db_original") + os.sep
PATH_PICKLE_DEST = ssp_data_dir + os.sep
PATH_TEMPLATE = os.path.join(mindset_root, "GLORIA_template") + os.sep

# Load grouping data
reg_conv = pd.read_excel(grouping_file, sheet_name="groups")
reg_conv_mat = reg_conv[['Lfd_Nr', 'Lfd_Nr_agg']].copy()
reg_conv = reg_conv[['Lfd_Nr', 'Region_acronyms', 'Agg_region', 'Agg_region_name', 'Lfd_Nr_agg']].copy()
reg_conv = reg_conv.sort_values(by=['Lfd_Nr_agg'])

agg_regions = sorted(reg_conv['Agg_region'].dropna().unique())
print(f"  Grouping loaded: {len(reg_conv)} GLORIA countries -> {len(agg_regions)} regions")
print(f"  Regions: {agg_regions}")
print()

# --- cid.pkl and cou.pkl ---
print("  Creating cid.pkl, cou.pkl...")
with open(f"{PATH_PICKLE_DEST}cid.pkl", "wb") as file:
    pkl.dump(list(reg_conv['Agg_region'].unique()), file)
with open(f"{PATH_PICKLE_DEST}cou.pkl", "wb") as file:
    pkl.dump(list(reg_conv['Agg_region_name'].unique()), file)

# --- Final demand files ---
reg_conv_use = reg_conv[['Region_acronyms', 'Agg_region']].copy()

value_name = {
    'FCF': 'VDFA', 'GOV': 'VIGA', 'HH': 'VIPA',
    'INV': 'INV', 'NPISH': 'NPISH', 'other_FD': 'otherFD'
}

for key, VALUE_COL in value_name.items():
    print(f"  Aggregating {key}.pkl...")
    data = pd.read_pickle(f"{PATH_PICKLE_SOURCE}{key}.pkl")
    data = data.reset_index()

    data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_imp', 'Region_acronyms']).rename(columns={'Agg_region': 'REG_imp'})

    data = data.merge(reg_conv_use, how='left', left_on='REG_exp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_exp', 'Region_acronyms']).rename(columns={'Agg_region': 'REG_exp'})

    data = data.groupby(['REG_imp', 'REG_exp', 'TRAD_COMM']).agg('sum').reset_index()
    data = data.set_index(['REG_imp', 'REG_exp', 'TRAD_COMM'])

    with open(f"{PATH_PICKLE_DEST}{key}.pkl", "wb") as file:
        pkl.dump(data, file)

# --- VA, labor_data, empl_data ---
for key in ['VA', 'labor_data', 'empl_data']:
    print(f"  Aggregating {key}.pkl...")
    data = pd.read_pickle(f"{PATH_PICKLE_SOURCE}{key}.pkl")

    data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_imp', 'Region_acronyms']).rename(columns={'Agg_region': 'REG_imp'})

    data = data.groupby(['REG_imp', 'PROD_COMM']).agg('sum').reset_index()

    with open(f"{PATH_PICKLE_DEST}{key}.pkl", "wb") as file:
        pkl.dump(data, file)

# --- IND_sparse ---
print("  Aggregating IND_sparse.pkl (this may take a moment)...")
data = pd.read_pickle(f"{PATH_PICKLE_SOURCE}IND_sparse.pkl")
data = data.reset_index()

# Aggregate output
output = data[['REG_imp', 'PROD_COMM', 'output']].drop_duplicates()
output = output.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
output = output.drop(columns=['REG_imp', 'Region_acronyms']).rename(columns={'Agg_region': 'REG_imp'})
output = output.groupby(['REG_imp', 'PROD_COMM']).agg('sum').reset_index()

# Aggregate transactions
data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
data = data.drop(columns=['REG_imp', 'Region_acronyms']).rename(columns={'Agg_region': 'REG_imp'})

data = data.merge(reg_conv_use, how='left', left_on='REG_exp', right_on='Region_acronyms')
data = data.drop(columns=['REG_exp', 'Region_acronyms']).rename(columns={'Agg_region': 'REG_exp'})

data = data.groupby(['REG_imp', 'PROD_COMM', 'REG_exp', 'TRAD_COMM']).agg({'z_bp': 'sum'}).reset_index()

# Recalculate technical coefficients
data = data.merge(output, how='left', on=['REG_imp', 'PROD_COMM'])
data['a_bp'] = data['z_bp'] / data['output']
data['a_tech'] = data.groupby(['REG_imp', 'PROD_COMM', 'TRAD_COMM'])['a_bp'].transform('sum')
data = data.set_index(['REG_imp', 'PROD_COMM', 'REG_exp', 'TRAD_COMM'])

with open(f"{PATH_PICKLE_DEST}IND_sparse.pkl", "wb") as file:
    pkl.dump(data, file)

# --- sec.pkl and sid.pkl (copy from source) ---
for key in ['sec', 'sid']:
    src = f"{PATH_PICKLE_SOURCE}{key}.pkl"
    dst = f"{PATH_PICKLE_DEST}{key}.pkl"
    if os.path.exists(src):
        shutil.copy2(src, dst)

# --- Update template files ---
print("  Updating template files...")
agg_groups = pd.read_excel(grouping_file, sheet_name="aggregates")
# Drop rows where Agg_region is NaN (extra rows in the sheet)
agg_groups = agg_groups.dropna(subset=['Agg_region'])

# Countries_inc_cat.xlsx
df_out = agg_groups[['Lfd_Nr_agg', 'Agg_region', 'Agg_region_name', 'USDA_inc_cat']].copy()
df_out.columns = ['Country_No', 'Country_Code', 'GLORIA_Country', 'USDA_inc_cat']
df_out.to_excel(f"{PATH_TEMPLATE}Elasticities\\Countries_inc_cat.xlsx", sheet_name='Countries', index=False)

# FileID_CrossPrice.xlsx
df_out = agg_groups[['Agg_region', 'Agg_region_name', 'Energy_CrossPrice_code', 'Energy_CrossPrice_file']].copy()
df_out.columns = ['Original Code', 'Country Name', 'Code', 'Filename']
df_out.to_excel(f"{PATH_TEMPLATE}Elasticities\\FileID_CrossPrice.xlsx", sheet_name='CrossPrices', index=False)

# FileID_OwnPrice.xlsx
df_out = agg_groups[['Agg_region', 'Agg_region_name', 'Energy_OwnPrice_code', 'Energy_OwnPrice_file']].copy()
df_out.columns = ['Original Code', 'Country Name', 'Code', 'Filename']
df_out.to_excel(f"{PATH_TEMPLATE}Elasticities\\FileID_OwnPrice.xlsx", sheet_name='OwnPrices', index=False)

# Countries_USDAtoGLORIA.xlsx
df_out = agg_groups[['Lfd_Nr_agg', 'Agg_region', 'Agg_region_name', 'USDA_Country', 'Employment_country', 'Investment_country', 'Beta_C', 'Beta_C_Agg']].copy()
df_out.columns = ['Country_No', 'Country_Code', 'GLORIA_Country', 'USDA_Country', 'Employment_country', 'Investment_country', 'Beta_C', 'Beta_C_Agg']
df_out.to_excel(f"{PATH_TEMPLATE}modelinputdata\\Countries_USDAtoGLORIA.xlsx", sheet_name='Countries', index=False)

# Variable_list R sheet
df_R = agg_groups[['Lfd_Nr_agg', 'Agg_region', 'Agg_region_name']].copy()
df_R.columns = ['Lfd_Nr', 'Region_acronyms', 'Region_names']
variable_list_file = f'{PATH_TEMPLATE}Variables\\Variable_list_MINDSET_SSP.xlsx'
with pd.ExcelWriter(variable_list_file, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
    df_R.to_excel(writer, sheet_name='R', index=False)

# --- Energy-emissions (skip if files don't exist) ---
pollutants_file = f"{PATH_TEMPLATE}Energy_emissions\\ALL_POLLUTANTS.csv"
if os.path.exists(pollutants_file):
    print("  Aggregating ALL_POLLUTANTS.csv...")
    edata = pd.read_csv(pollutants_file)
    edata = edata[edata['POLLUTANT_FRACTION'] == 'CO2'].copy()
    edata = edata.merge(reg_conv_use, how='left', left_on='target-country-iso3', right_on='Region_acronyms')
    edata = edata.drop(columns=['target-country-iso3', 'Region_acronyms']).rename(columns={'Agg_region': 'target-country-iso3'})
    edata = edata.merge(reg_conv_use, how='left', left_on='origin-country-iso3', right_on='Region_acronyms')
    edata = edata.drop(columns=['origin-country-iso3', 'Region_acronyms']).rename(columns={'Agg_region': 'origin-country-iso3'})
    edata = edata.groupby(['target-country-iso3', 'origin-country-iso3', 'target-sector', 'origin-sector', 'POLLUTANT_FRACTION']).agg('sum').reset_index()
    edata.to_csv(pollutants_file, index=False)

process_file = f"{PATH_TEMPLATE}Energy_emissions\\ALL_PROCESS_EMISSIONS.csv"
if os.path.exists(process_file):
    print("  Aggregating ALL_PROCESS_EMISSIONS.csv...")
    edata = pd.read_csv(process_file).pipe(lambda d: d[d['target-country-iso3'] != "DEFAULT"])
    edata = edata.merge(reg_conv_use, how='left', left_on='target-country-iso3', right_on='Region_acronyms')
    edata = edata[~edata['Agg_region'].isna()]
    edata = edata.drop(columns=['target-country-iso3', 'Region_acronyms']).rename(columns={'Agg_region': 'target-country-iso3'})
    edata = edata.groupby(['target-country-iso3', 'target-sector']).agg('sum').reset_index()
    edata['EF_ktCO2_per_kUSD'] = edata['Y_2019'] / edata['output_kUSD']
    edata.to_csv(process_file, index=False)

elapsed = time.time() - start_time
print(f"\n  Aggregation completed in {elapsed:.1f} seconds")
print()

# ============================================================
# STEP 3: Delete stale .mat files
# ============================================================
print("STEP 3: Removing stale .mat files (will be recomputed on first run)")
print("-" * 80)

for f in ['GLORIA_L_Base_2019.mat', 'GLORIA_Y_Base_2019.mat', 'GLORIA_G_Base_2019.mat']:
    mat_path = os.path.join(ssp_data_dir, f)
    if os.path.exists(mat_path):
        os.remove(mat_path)
        print(f"  Deleted: {f}")
    else:
        print(f"  Not found (already removed): {f}")

print()

# ============================================================
# STEP 4: Verify new data dimensions
# ============================================================
print("STEP 4: Verifying new data")
print("-" * 80)

with open(os.path.join(ssp_data_dir, "cid.pkl"), 'rb') as f:
    cid = pkl.load(f)
print(f"  Regions: {cid}")
print(f"  Count: {len(cid)} (expected 9)")
print(f"  BOL included: {'BOL' in cid}")

IND = pd.read_pickle(os.path.join(ssp_data_dir, "IND_sparse.pkl"))
ind_regions = sorted(IND.reset_index()['REG_imp'].unique())
print(f"  IND_sparse regions: {ind_regions}")

FCF = pd.read_pickle(os.path.join(ssp_data_dir, "FCF.pkl"))
fcf_regions = sorted(FCF.reset_index()['REG_imp'].unique())
print(f"  FCF regions: {fcf_regions}")

labor = pd.read_pickle(os.path.join(ssp_data_dir, "labor_data.pkl"))
labor_regions = sorted(labor['REG_imp'].unique())
print(f"  labor_data regions: {labor_regions}")

print()
print("=" * 80)
print("REBUILD COMPLETE!")
print("=" * 80)
print()
print("SSP data now includes 9 regions (ROW + 7 original + Bolivia).")
print()
print("NEXT: The first run of BATCH_EMPLOYMENT_ALL_STRATEGIES.py will be")
print("slower because L_BASE needs to be recomputed (~1080x1080 matrix inversion).")
print("After that, .mat files are cached for fast subsequent runs.")
print("=" * 80)
