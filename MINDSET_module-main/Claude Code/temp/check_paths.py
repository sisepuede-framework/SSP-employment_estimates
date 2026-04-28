"""
Diagnostic script to check MINDSET paths and data files
Run this to verify all necessary files can be found
"""

import sys
import os
import pandas as pd

# Same path setup as RunMINDSET_EmploymentOnly.py
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)

os.chdir(mindset_root)

print("="*70)
print("MINDSET PATH DIAGNOSTIC")
print("="*70)

print(f"\n1. MINDSET Root Directory: {mindset_root}")
print(f"2. Current Working Directory: {os.getcwd()}")
print(f"3. Script Directory: {script_dir}")

# Check key directories
print("\n" + "-"*70)
print("Checking Key Directories:")
print("-"*70)

dirs_to_check = {
    "SourceCode": "SourceCode",
    "GLORIA Template": "GLORIA_template",
    "GLORIA Database": "GLORIA_db/v57/2019/parsed_db_original",
    "Scenarios": "GLORIA_template/Scenarios",
    "Variables": "GLORIA_template/Variables"
}

for name, path in dirs_to_check.items():
    full_path = os.path.join(mindset_root, path)
    exists = os.path.exists(full_path)
    print(f"  {'✓' if exists else '✗'} {name:20s}: {path}")
    if exists and name in ["GLORIA Database", "Scenarios"]:
        # List some files
        try:
            files = os.listdir(full_path)
            print(f"      Found {len(files)} files/folders")
        except:
            pass

# Check Variable list file
print("\n" + "-"*70)
print("Checking Variable List File:")
print("-"*70)

var_path = os.path.join(mindset_root, "GLORIA_template", "Variables", "Variable_list_MINDSET.xlsx")
if os.path.exists(var_path):
    print(f"  ✓ Variable list exists: {var_path}")
    try:
        var_data = pd.read_excel(var_path, "variables")
        print(f"  ✓ Successfully read Excel file")
        print(f"  ✓ Found {len(var_data)} variables defined")

        # Show first few data file paths
        print("\n  Key data file locations specified in Variable_list_MINDSET.xlsx:")
        important_vars = ['L_BASE', 'EMPL_COEF', 'COU_ID', 'SEC_ID', 'COU_NAME', 'SEC_NAME']
        for var in important_vars:
            if var in var_data['Variable name (new)'].values:
                location = var_data[var_data['Variable name (new)'] == var]['Location'].values[0]
                if pd.notna(location):
                    file_path = os.path.join(mindset_root, location)
                    exists = os.path.exists(file_path)
                    print(f"    {'✓' if exists else '✗'} {var:15s}: {location}")
                else:
                    print(f"    ? {var:15s}: <not specified>")
    except Exception as e:
        print(f"  ✗ Error reading Variable list: {e}")
else:
    print(f"  ✗ Variable list NOT found: {var_path}")

# Check GLORIA database files
print("\n" + "-"*70)
print("Checking GLORIA Database Files:")
print("-"*70)

db_path = os.path.join(mindset_root, "GLORIA_db", "v57", "2019", "parsed_db_original")
if os.path.exists(db_path):
    print(f"  ✓ Database directory exists: {db_path}")

    critical_files = [
        'empl_data.pkl',  # Employment coefficients
        'labor_data.pkl',  # Labor data
        'IND_sparse.pkl',  # Input-Output matrix
        'cou.pkl',         # Country list
        'sec.pkl',         # Sector list
        'HH.pkl',          # Household final demand
        'INV.pkl',         # Investment
        'GOV.pkl'          # Government spending
    ]

    print("\n  Critical files for employment analysis:")
    for filename in critical_files:
        file_path = os.path.join(db_path, filename)
        exists = os.path.exists(file_path)
        size = os.path.getsize(file_path) if exists else 0
        print(f"    {'✓' if exists else '✗'} {filename:20s} {f'({size/1024:.1f} KB)' if exists else ''}")
else:
    print(f"  ✗ Database directory NOT found: {db_path}")

# Check scenario files
print("\n" + "-"*70)
print("Checking Scenario Files:")
print("-"*70)

scenario_dir = os.path.join(mindset_root, "GLORIA_template", "Scenarios")
if os.path.exists(scenario_dir):
    print(f"  ✓ Scenario directory exists: {scenario_dir}")
    try:
        scenario_files = [f for f in os.listdir(scenario_dir) if f.endswith('.xlsx')]
        print(f"  ✓ Found {len(scenario_files)} scenario file(s):")
        for f in scenario_files[:10]:  # Show first 10
            print(f"    - {f}")
        if len(scenario_files) > 10:
            print(f"    ... and {len(scenario_files) - 10} more")
    except Exception as e:
        print(f"  ✗ Error listing scenarios: {e}")
else:
    print(f"  ✗ Scenario directory NOT found: {scenario_dir}")

# Test imports
print("\n" + "-"*70)
print("Testing Module Imports:")
print("-"*70)

modules_to_test = [
    ('SourceCode.exog_vars', 'exog_vars'),
    ('SourceCode.scenario', 'scenario'),
    ('SourceCode.InputOutput', 'IO'),
    ('SourceCode.employment', 'empl'),
    ('SourceCode.results', 'results'),
    ('SourceCode.utils', 'MRIO_df_to_vec')
]

for module_path, item_name in modules_to_test:
    try:
        exec(f"from {module_path} import {item_name}")
        print(f"  ✓ {module_path}")
    except ImportError as e:
        print(f"  ✗ {module_path}: {e}")
    except Exception as e:
        print(f"  ? {module_path}: {e}")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
print("\nIf you see all ✓ marks, the paths are configured correctly!")
print("If you see ✗ marks, those files/directories need to be checked.\n")
