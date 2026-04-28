"""
Check the GLORIA country code to full name mapping
"""
import pandas as pd
import pickle

# Load GLORIA country codes and names
with open("GLORIA_db/v57/2019/parsed_db_original/cid.pkl", 'rb') as f:
    cid = pickle.load(f)  # 3-letter codes

with open("GLORIA_db/v57/2019/parsed_db_original/cou.pkl", 'rb') as f:
    cou = pickle.load(f)  # Full country names

print("GLORIA Country Mapping")
print("="*80)
print(f"Total countries: {len(cid)}")
print()

# Create mapping
code_to_name = dict(zip(cid, cou))

# Show our 8 countries
our_countries = ['BGR', 'BLZ', 'EGY', 'LBY', 'MAR', 'MEX', 'ROW', 'UGA']

print("Our 8 countries:")
print("-"*80)
for code in our_countries:
    if code in code_to_name:
        print(f"{code} → {code_to_name[code]}")
    else:
        print(f"{code} → NOT FOUND")
print()

# Check which codes exist
print("All GLORIA codes (first 20):")
print(sorted(cid)[:20])
