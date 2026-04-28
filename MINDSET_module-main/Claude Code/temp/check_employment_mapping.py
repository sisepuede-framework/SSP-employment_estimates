"""
Check employment data mapping for selected countries
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

from SourceCode.exog_vars_SSP import exog_vars

print("Loading MRIO data...")
MRIO_BASE = exog_vars()

print("\n" + "=" * 80)
print("CHECKING EMPLOYMENT MAPPING")
print("=" * 80)

print("\nSelected countries (COU_ID):")
print(MRIO_BASE.COU_ID)

print("\n" + "-" * 80)
print("HH_CONS_COU mapping for selected countries:")
print("-" * 80)

for country in MRIO_BASE.COU_ID:
    matches = MRIO_BASE.HH_CONS_COU[MRIO_BASE.HH_CONS_COU['Country_Code'] == country]
    if len(matches) > 0:
        print(f"\n{country}:")
        print(f"  Has {len(matches)} entries")
        print(f"  Employment_country values: {matches['Employment_country'].unique().tolist()}")
    else:
        print(f"\n{country}: NO MAPPING FOUND IN HH_CONS_COU")

print("\n" + "-" * 80)
print("Employment coefficient file columns (countries available):")
print("-" * 80)
print(f"Total columns: {len(MRIO_BASE.EMPL_COEF.columns)}")
print(f"First column: {MRIO_BASE.EMPL_COEF.columns[0]} (sector IDs)")
print(f"Country columns (first 20): {MRIO_BASE.EMPL_COEF.columns[1:21].tolist()}")
print(f"Last 10 columns: {MRIO_BASE.EMPL_COEF.columns[-10:].tolist()}")

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)

# Check if any of our countries exist in employment data
selected_countries_in_empl = []
for country in MRIO_BASE.COU_ID:
    # Check HH_CONS_COU for this country's Employment_country name
    matches = MRIO_BASE.HH_CONS_COU[MRIO_BASE.HH_CONS_COU['Country_Code'] == country]
    if len(matches) > 0:
        empl_country_names = matches['Employment_country'].unique().tolist()
        # Check if any of these names are in EMPL_COEF columns
        for empl_name in empl_country_names:
            if empl_name in MRIO_BASE.EMPL_COEF.columns:
                selected_countries_in_empl.append(country)
                print(f"✓ {country} maps to '{empl_name}' which EXISTS in employment data")
                break
        else:
            print(f"✗ {country} maps to {empl_country_names} which DO NOT exist in employment data")
    else:
        print(f"✗ {country} has NO mapping in HH_CONS_COU")

if len(selected_countries_in_empl) == 0:
    print("\n⚠️  WARNING: None of your 7 selected countries have employment data!")
    print("    This means employment estimates will be zero unless we use proxy data (ROW).")
