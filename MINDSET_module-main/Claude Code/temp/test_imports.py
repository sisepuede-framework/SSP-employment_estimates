"""
Test script to verify that path setup works correctly
Run this before running the full employment script to check for import issues
"""

import sys
import os

# Same path setup as RunMINDSET_EmploymentOnly.py
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

if mindset_root not in sys.path:
    sys.path.insert(0, mindset_root)

os.chdir(mindset_root)

print("="*60)
print("TESTING MINDSET IMPORTS")
print("="*60)
print(f"\n1. Script location: {script_dir}")
print(f"2. MINDSET root: {mindset_root}")
print(f"3. Working directory: {os.getcwd()}")

# Test imports
print("\n" + "-"*60)
print("Testing module imports...")
print("-"*60)

try:
    from SourceCode.exog_vars import exog_vars
    print("✓ Successfully imported: exog_vars")
except ImportError as e:
    print(f"✗ Failed to import exog_vars: {e}")

try:
    from SourceCode.scenario import scenario
    print("✓ Successfully imported: scenario")
except ImportError as e:
    print(f"✗ Failed to import scenario: {e}")

try:
    from SourceCode.InputOutput import IO
    print("✓ Successfully imported: InputOutput (IO)")
except ImportError as e:
    print(f"✗ Failed to import IO: {e}")

try:
    from SourceCode.employment import empl
    print("✓ Successfully imported: employment (empl)")
except ImportError as e:
    print(f"✗ Failed to import empl: {e}")

try:
    from SourceCode.results import results
    print("✓ Successfully imported: results")
except ImportError as e:
    print(f"✗ Failed to import results: {e}")

try:
    from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df
    print("✓ Successfully imported: utils (MRIO_df_to_vec, MRIO_vec_to_df)")
except ImportError as e:
    print(f"✗ Failed to import utils: {e}")

# Test file paths
print("\n" + "-"*60)
print("Testing file paths...")
print("-"*60)

scenario_dir = os.path.join(mindset_root, "GLORIA_template", "Scenarios")
print(f"\nScenario directory: {scenario_dir}")
print(f"Exists: {os.path.exists(scenario_dir)}")

if os.path.exists(scenario_dir):
    scenario_files = [f for f in os.listdir(scenario_dir) if f.endswith('.xlsx')]
    print(f"Found {len(scenario_files)} scenario files:")
    for f in scenario_files[:5]:  # Show first 5
        print(f"  - {f}")
    if len(scenario_files) > 5:
        print(f"  ... and {len(scenario_files) - 5} more")

print("\n" + "="*60)
print("IMPORT TEST COMPLETE")
print("="*60)
print("\nIf all imports show ✓, you're ready to run RunMINDSET_EmploymentOnly.py")
print("If any show ✗, there may be missing dependencies or file issues.\n")
