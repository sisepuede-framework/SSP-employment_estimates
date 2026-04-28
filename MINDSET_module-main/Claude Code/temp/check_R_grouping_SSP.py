"""
Check R_grouping_SSP.xlsx to see how ROW is defined
"""
import pandas as pd

grouping_file = "GLORIA_template/Country_groupings/R_grouping_SSP.xlsx"

print("="*80)
print("R_GROUPING_SSP.xlsx - groups sheet")
print("="*80)

# Read the groups sheet
groups = pd.read_excel(grouping_file, sheet_name="groups")

print(f"Shape: {groups.shape}")
print(f"Columns: {list(groups.columns)}")
print(f"\nFirst 10 rows:")
print(groups.head(10))

# Check unique aggregated regions
print(f"\nUnique Agg_region values: {sorted(groups['Agg_region'].unique())}")
print(f"Total aggregated regions: {len(groups['Agg_region'].unique())}")

# Check if ROW exists
if 'ROW' in groups['Agg_region'].values:
    print(f"\n✓ ROW exists in aggregated regions")
    row_countries = groups[groups['Agg_region'] == 'ROW']
    print(f"  Number of GLORIA countries aggregated into ROW: {len(row_countries)}")
    print(f"  First 10 countries in ROW:")
    print(row_countries[['Region_acronyms', 'Agg_region']].head(10))
else:
    print(f"\n✗ ROW does NOT exist in Agg_region")

# Check our 7 countries
our_7 = ['BGR', 'BLZ', 'EGY', 'LBY', 'MAR', 'MEX', 'UGA']
print(f"\nOur 7 countries mapping:")
for country in our_7:
    match = groups[groups['Region_acronyms'] == country]
    if len(match) > 0:
        agg = match['Agg_region'].values[0]
        print(f"  {country} → {agg}")
    else:
        print(f"  {country} → NOT FOUND")
