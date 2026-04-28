# -*- coding: utf-8 -*-
"""
COLLAPSE MRIO FOR SSP ANALYSIS (8 regions: ROW + 7 countries)

Modified from collapse_MRIO.py to:
- Read from: GLORIA_db\v57\2019\parsed_db_original\ (164 GLORIA countries)
- Write to: GLORIA_db\v57\2019\parsed_db\ (8 aggregated regions)
- Use: R_grouping_SSP.xlsx (BGR, BLZ, EGY, LBY, MAR, MEX, ROW, UGA)

This aggregates 157 GLORIA countries into ROW by SUMMING their:
- IO transactions (IND_sparse)
- Final demand (HH, GOV, FCF, INV, NPISH)
- Employment (empl_data)
- Value added (VA)
- Labor compensation (labor_data)

The 7 main countries (BGR, BLZ, EGY, LBY, MAR, MEX, UGA) remain as individual regions.

Author: Modified for SSP analysis
Date: 2026-03-22
"""

import pickle as pkl
import pandas as pd
import sys
import os

print("="*80)
print("COLLAPSE MRIO FOR SSP ANALYSIS")
print("="*80)
print(f"Working directory: {os.getcwd()}")

# Define paths
grouping_file = "GLORIA_template\\Country_groupings\\R_grouping_SSP.xlsx"
PATH_PICKLE_SOURCE = "GLORIA_db\\v57\\2019\\parsed_db_original\\"  # READ from here (164 countries)
PATH_PICKLE_DEST = "GLORIA_db\\v57\\2019\\SSP\\"                   # WRITE to here (8 regions)
PATH_TEMPLATE = "GLORIA_template\\"

print(f"\nGrouping file: {grouping_file}")
print(f"Source (164 countries): {PATH_PICKLE_SOURCE}")
print(f"Destination (8 regions): {PATH_PICKLE_DEST}")

# Create destination directory if it doesn't exist
os.makedirs(PATH_PICKLE_DEST, exist_ok=True)
print(f"✓ Created destination directory: {PATH_PICKLE_DEST}")

# Load grouping data
print(f"\nLoading grouping file...")
reg_conv = pd.read_excel(grouping_file, sheet_name="groups")
reg_conv_mat = reg_conv[['Lfd_Nr','Lfd_Nr_agg']].copy()
reg_conv = reg_conv[['Lfd_Nr','Region_acronyms','Agg_region','Agg_region_name','Lfd_Nr_agg']].copy()
reg_conv = reg_conv.sort_values(by=['Lfd_Nr_agg'])

print(f"✓ Loaded grouping: {len(reg_conv)} GLORIA countries → {len(reg_conv['Agg_region'].unique())} aggregated regions")
print(f"  Aggregated regions: {sorted(reg_conv['Agg_region'].unique())}")

#%%

print("\n" + "="*80)
print("STEP 1: Create aggregated country lists (cid.pkl, cou.pkl)")
print("="*80)

# cid.pkl (3-letter codes)
output_file = f"{PATH_PICKLE_DEST}cid.pkl"
with open(output_file, "wb") as file:
    pkl.dump(list(reg_conv['Agg_region'].unique()), file)
print(f"✓ Created: {output_file}")

# cou.pkl (full names)
output_file = f"{PATH_PICKLE_DEST}cou.pkl"
with open(output_file, "wb") as file:
    pkl.dump(list(reg_conv['Agg_region_name'].unique()), file)
print(f"✓ Created: {output_file}")

#%%

print("\n" + "="*80)
print("STEP 2: Aggregate final demand files (FCF, GOV, HH, INV, NPISH, other_FD)")
print("="*80)

value_name = {
    'FCF': 'VDFA',
    'GOV': 'VIGA',
    'HH': 'VIPA',
    'INV': 'INV',
    'NPISH': 'NPISH',
    'other_FD': 'otherFD'
    }

# reg-imp reg-exp trad-comm [these are in index]
reg_conv_use = reg_conv[['Region_acronyms','Agg_region']].copy()

for key, VALUE_COL in value_name.items():
    input_file = f"{PATH_PICKLE_SOURCE}{key}.pkl"
    output_file = f"{PATH_PICKLE_DEST}{key}.pkl"

    print(f"\nProcessing: {key}.pkl")
    data = pd.read_pickle(input_file)
    print(f"  Source shape: {data.shape}")

    # Aggregate both reg-imp and reg-exp
    data = data.reset_index()
    data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_imp','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'REG_imp'})

    data = data.merge(reg_conv_use, how='left', left_on='REG_exp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_exp','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'REG_exp'})

    # Sum by aggregated regions
    data = data.groupby(['REG_imp','REG_exp','TRAD_COMM']).agg('sum').reset_index()
    data = data.set_index(['REG_imp','REG_exp','TRAD_COMM'])

    print(f"  Aggregated shape: {data.shape}")
    with open(output_file, "wb") as file:
        pkl.dump(data, file)
    print(f"  ✓ Created: {output_file}")

#%%

print("\n" + "="*80)
print("STEP 3: Aggregate other data files (VA, labor_data, empl_data)")
print("="*80)

# These have only reg-imp and prod-comm (no reg-exp)
dfs = ['VA','labor_data','empl_data']

for key in dfs:
    input_file = f"{PATH_PICKLE_SOURCE}{key}.pkl"
    output_file = f"{PATH_PICKLE_DEST}{key}.pkl"

    print(f"\nProcessing: {key}.pkl")
    data = pd.read_pickle(input_file)
    print(f"  Source shape: {data.shape}")

    # Aggregate reg-imp only
    data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_imp','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'REG_imp'})

    # Sum by aggregated regions
    data = data.groupby(['REG_imp','PROD_COMM']).agg('sum').reset_index()

    print(f"  Aggregated shape: {data.shape}")
    with open(output_file, "wb") as file:
        pkl.dump(data, file)
    print(f"  ✓ Created: {output_file}")

#%%

print("\n" + "="*80)
print("STEP 4: Aggregate IND_sparse (MRIO table)")
print("="*80)

key = "IND_sparse"
input_file = f"{PATH_PICKLE_SOURCE}{key}.pkl"
output_file = f"{PATH_PICKLE_DEST}{key}.pkl"

print(f"\nProcessing: {key}.pkl")
data = pd.read_pickle(input_file)
print(f"  Source shape: {data.shape}")

data = data.reset_index()

# First aggregate output
output = data[['REG_imp','PROD_COMM','output']]
output = output.drop_duplicates()
output = output.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
output = output.drop(columns=['REG_imp','Region_acronyms'])
output = output.rename(columns={'Agg_region':'REG_imp'})
output = output.groupby(['REG_imp','PROD_COMM']).agg('sum').reset_index()
print(f"  Aggregated output shape: {output.shape}")

# Aggregate reg-imp
data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
data = data.drop(columns=['REG_imp','Region_acronyms'])
data = data.rename(columns={'Agg_region':'REG_imp'})

# Aggregate reg-exp
data = data.merge(reg_conv_use, how='left', left_on='REG_exp', right_on='Region_acronyms')
data = data.drop(columns=['REG_exp','Region_acronyms'])
data = data.rename(columns={'Agg_region':'REG_exp'})

# Sum transactions
data = data.groupby(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM']).agg({'z_bp':'sum'}).reset_index()
print(f"  Aggregated transactions shape: {data.shape}")

# Recalculate technical coefficients: a_bp = z_bp / output
data = data.merge(output, how='left', on=['REG_imp','PROD_COMM'])
data['a_bp'] = data['z_bp'] / data['output']
data['a_tech'] = data.groupby(['REG_imp','PROD_COMM','TRAD_COMM'])['a_bp'].transform('sum')
data = data.set_index(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])

with open(output_file, "wb") as file:
    pkl.dump(data, file)
print(f"  ✓ Created: {output_file}")

#%%

print("\n" + "="*80)
print("STEP 5: Update template files")
print("="*80)

agg_groups = pd.read_excel(grouping_file, sheet_name="aggregates")

# Countries_inc_cat.xlsx
print(f"\nCreating Countries_inc_cat.xlsx...")
df = agg_groups[['Lfd_Nr_agg','Agg_region','Agg_region_name','USDA_inc_cat']].copy()
df.columns = ['Country_No','Country_Code','GLORIA_Country','USDA_inc_cat']
output_file = f"{PATH_TEMPLATE}Elasticities\\Countries_inc_cat.xlsx"
df.to_excel(output_file, sheet_name='Countries', index=False)
print(f"✓ Created: {output_file}")

# FileID_CrossPrice.xlsx
print(f"\nCreating FileID_CrossPrice.xlsx...")
df = agg_groups[['Agg_region','Agg_region_name','Energy_CrossPrice_code','Energy_CrossPrice_file']].copy()
df.columns = ['Original Code', 'Country Name', 'Code', 'Filename']
output_file = f"{PATH_TEMPLATE}Elasticities\\FileID_CrossPrice.xlsx"
df.to_excel(output_file, sheet_name='CrossPrices', index=False)
print(f"✓ Created: {output_file}")

# FileID_OwnPrice.xlsx
print(f"\nCreating FileID_OwnPrice.xlsx...")
df = agg_groups[['Agg_region','Agg_region_name','Energy_OwnPrice_code','Energy_OwnPrice_file']].copy()
df.columns = ['Original Code', 'Country Name', 'Code', 'Filename']
output_file = f"{PATH_TEMPLATE}Elasticities\\FileID_OwnPrice.xlsx"
df.to_excel(output_file, sheet_name='OwnPrices', index=False)
print(f"✓ Created: {output_file}")

# Countries_USDAtoGLORIA.xlsx
print(f"\nCreating Countries_USDAtoGLORIA.xlsx...")
df = agg_groups[['Lfd_Nr_agg','Agg_region','Agg_region_name','USDA_Country','Employment_country','Investment_country','Beta_C','Beta_C_Agg']].copy()
df.columns = ['Country_No','Country_Code','GLORIA_Country', 'USDA_Country','Employment_country','Investment_country','Beta_C','Beta_C_Agg']
output_file = f"{PATH_TEMPLATE}modelinputdata\\Countries_USDAtoGLORIA.xlsx"
df.to_excel(output_file, sheet_name='Countries', index=False)
print(f"✓ Created: {output_file}")

#%%

print("\n" + "="*80)
print("STEP 6: Aggregate energy-emissions data")
print("="*80)

# ALL_POLLUTANTS.csv
print(f"\nProcessing ALL_POLLUTANTS.csv...")
input_file = f"{PATH_TEMPLATE}Energy_emissions\\ALL_POLLUTANTS.csv"
if os.path.exists(input_file):
    data = pd.read_csv(input_file)
    data = data[data['POLLUTANT_FRACTION']=='CO2'].copy()

    data = data.merge(reg_conv_use, how='left', left_on='target-country-iso3', right_on='Region_acronyms')
    data = data.drop(columns=['target-country-iso3','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'target-country-iso3'})

    data = data.merge(reg_conv_use, how='left', left_on='origin-country-iso3', right_on='Region_acronyms')
    data = data.drop(columns=['origin-country-iso3','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'origin-country-iso3'})

    data = data.groupby(['target-country-iso3','origin-country-iso3','target-sector','origin-sector','POLLUTANT_FRACTION']).agg('sum').reset_index()
    data.to_csv(input_file, index=False)
    print(f"✓ Updated: {input_file}")
else:
    print(f"⚠ Skipped (file not found): {input_file}")

# ALL_PROCESS_EMISSIONS.csv
print(f"\nProcessing ALL_PROCESS_EMISSIONS.csv...")
input_file = f"{PATH_TEMPLATE}Energy_emissions\\ALL_PROCESS_EMISSIONS.csv"
if os.path.exists(input_file):
    data = pd.read_csv(input_file).pipe(lambda d: d[d['target-country-iso3'] != "DEFAULT"])
    data = data.merge(reg_conv_use, how='left', left_on='target-country-iso3', right_on='Region_acronyms')
    data = data[~data['Agg_region'].isna()]
    data = data.drop(columns=['target-country-iso3','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'target-country-iso3'})
    data = data.groupby(['target-country-iso3','target-sector']).agg('sum').reset_index()
    data['EF_ktCO2_per_kUSD'] = data['Y_2019'] / data['output_kUSD']
    data.to_csv(input_file, index=False)
    print(f"✓ Updated: {input_file}")
else:
    print(f"⚠ Skipped (file not found): {input_file}")

#%%

print("\n" + "="*80)
print("STEP 7: Update Variable_list_MINDSET_SSP.xlsx R sheet")
print("="*80)

df = agg_groups[['Lfd_Nr_agg','Agg_region','Agg_region_name']].copy()
df.columns = ['Lfd_Nr','Region_acronyms','Region_names']

variable_list_file = f'{PATH_TEMPLATE}Variables\\Variable_list_MINDSET_SSP.xlsx'
print(f"\nUpdating: {variable_list_file}")

with pd.ExcelWriter(variable_list_file, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='R', index=False)
print(f"✓ Updated R sheet with {len(df)} aggregated regions")

#%%

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\n✓ Aggregation complete!")
print(f"  Source: {PATH_PICKLE_SOURCE} (164 GLORIA countries)")
print(f"  Destination: {PATH_PICKLE_DEST} (8 aggregated regions)")
print(f"\n  Aggregated regions:")
for i, region in enumerate(sorted(df['Region_acronyms'].unique()), 1):
    name = df[df['Region_acronyms'] == region]['Region_names'].values[0]
    print(f"    {i}. {region} - {name}")

print(f"\n  Files created in {PATH_PICKLE_DEST}:")
print(f"    • cid.pkl, cou.pkl")
print(f"    • IND_sparse.pkl (MRIO table)")
print(f"    • HH.pkl, GOV.pkl, FCF.pkl, INV.pkl, NPISH.pkl, other_FD.pkl")
print(f"    • VA.pkl, labor_data.pkl, empl_data.pkl")

print(f"\n  Template files updated:")
print(f"    • Countries_inc_cat.xlsx")
print(f"    • FileID_CrossPrice.xlsx, FileID_OwnPrice.xlsx")
print(f"    • Countries_USDAtoGLORIA.xlsx")
print(f"    • Variable_list_MINDSET_SSP.xlsx (R sheet)")

print("\n" + "="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Update Variable_list_MINDSET_SSP.xlsx 'variables' sheet:")
print("   Change Location column for .pkl files from:")
print("   • OLD: GLORIA_db\\v57\\2019\\parsed_db_original\\*.pkl")
print("   • NEW: GLORIA_db\\v57\\2019\\SSP\\*.pkl")
print("\n2. Run your MINDSET analysis with the aggregated data")
print("="*80)
