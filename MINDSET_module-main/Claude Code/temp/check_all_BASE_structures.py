"""
Check structure of all _BASE DataFrames to understand proper format
"""
import pickle
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

base_files = ['HH.pkl', 'GOV.pkl', 'FCF.pkl', 'inv.pkl', 'npish.pkl']

print("="*80)
print("SSP _BASE DataFrame Structures")
print("="*80)

for filename in base_files:
    filepath = f"GLORIA_db/v57/2019/SSP/{filename}"
    print(f"\n{filename}:")
    print("-"*80)

    if os.path.exists(filepath):
        df = pickle.load(open(filepath, 'rb'))
        print(f"  Type: {type(df)}")
        print(f"  Shape: {df.shape}")
        print(f"  Index names: {df.index.names}")
        print(f"  Columns: {list(df.columns)}")

        # Check if index can be used for groupby
        if isinstance(df.index.names, list) and len(df.index.names) > 1:
            print(f"  → Has MultiIndex - need reset_index() for groupby")
        else:
            print(f"  → Regular index - ready for groupby")

        # Show first row
        print(f"  First row:")
        print(f"    {df.head(1)}")
    else:
        print(f"  ✗ File not found")

print("\n" + "="*80)
print("Checking ORIGINAL parsed_db_original structures")
print("="*80)

for filename in ['HH.pkl', 'GOV.pkl', 'FCF.pkl']:
    filepath = f"GLORIA_db/v57/2019/parsed_db_original/{filename}"
    print(f"\n{filename} (original):")
    print("-"*80)

    try:
        df = pickle.load(open(filepath, 'rb'))
        print(f"  Index names: {df.index.names}")
        print(f"  Columns: {list(df.columns)}")

        # Try the groupby that InputOutput.py does
        if filename == 'HH.pkl':
            col = 'VIPA'
        elif filename == 'GOV.pkl':
            col = 'VIGA'
        else:  # FCF
            col = 'VDFA'

        try:
            result = df.groupby(['REG_exp','TRAD_COMM']).agg({col:'sum'}).reset_index()
            print(f"  ✓ groupby(['REG_exp','TRAD_COMM']) works!")
            print(f"    Result columns: {list(result.columns)}")
        except Exception as e:
            print(f"  ✗ groupby failed: {e}")
    except Exception as e:
        print(f"  Error loading: {e}")
