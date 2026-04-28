"""
DEBUG: Run a single Bolivia scenario to identify errors.
This is a throwaway debug script - does NOT modify the original batch file.
"""

import sys
import os
import numpy as np
import pandas as pd

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

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

# ============================================================
# STEP 1: Load MRIO data
# ============================================================
print("=" * 60)
print("STEP 1: Loading MRIO Base Data")
print("=" * 60)

MRIO_BASE = exog_vars()

print(f"\nRegions (COU_ID): {MRIO_BASE.COU_ID}")
print(f"Number of sectors: {len(MRIO_BASE.SEC_ID)}")
print(f"Is 'BOL' in COU_ID? {'BOL' in MRIO_BASE.COU_ID}")
print()

# ============================================================
# STEP 2: Check a Bolivia scenario file
# ============================================================
print("=" * 60)
print("STEP 2: Loading a single Bolivia scenario")
print("=" * 60)

scenario_file = os.path.join(os.getcwd(), "GLORIA_template", "Scenarios", "Strategy_1004_BOL.xlsx")
print(f"Scenario file: {scenario_file}")
print(f"File exists: {os.path.exists(scenario_file)}")
print()

try:
    Scenario = scenario(MRIO_BASE, scenario_file, MockLog())
    print("[OK] Scenario object created")
except Exception as e:
    print(f"[ERROR] Creating scenario object: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    Scenario.set_exog_inv()
    print("[OK] set_exog_inv() completed")
    print(f"  inv_exog shape: {Scenario.inv_exog.shape}")
    print(f"  inv_exog columns: {list(Scenario.inv_exog.columns)}")
    print(f"  inv_exog head:\n{Scenario.inv_exog.head(10)}")
    print(f"\n  Investing countries: {Scenario.inv_exog['REG_imp'].unique()}")
    print(f"  Total investment: {Scenario.inv_exog['dk'].sum():,.2f}")
except Exception as e:
    print(f"[ERROR] set_exog_inv(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================
# STEP 3: Investment module
# ============================================================
print("=" * 60)
print("STEP 3: Investment Converter")
print("=" * 60)

try:
    if not hasattr(Scenario, 'inv_spending'):
        Scenario.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])

    INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE)
    print(f"[OK] INV_CONV created, shape: {INV_CONV.shape if hasattr(INV_CONV, 'shape') else type(INV_CONV)}")
except Exception as e:
    print(f"[ERROR] set_inv_conv_adj(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
    print("[OK] invest object created")
except Exception as e:
    print(f"[ERROR] Creating invest object: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    INV_model.build_inv_output_elas()
    print("[OK] build_inv_output_elas()")
except Exception as e:
    print(f"[ERROR] build_inv_output_elas(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    INV_model.calc_inv_share()
    print("[OK] calc_inv_share()")
except Exception as e:
    print(f"[ERROR] calc_inv_share(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    INV_model.calc_dy_inv_exog(Scenario.inv_exog)
    print(f"[OK] calc_dy_inv_exog()")
    print(f"  dy_inv_exog shape: {INV_model.dy_inv_exog.shape}")
    print(f"  dy_inv_exog columns: {list(INV_model.dy_inv_exog.columns)}")
    print(f"  dy_inv_exog head:\n{INV_model.dy_inv_exog.head()}")
    print(f"  Total dy: {INV_model.dy_inv_exog['dy'].sum():,.2f}")
except Exception as e:
    print(f"[ERROR] calc_dy_inv_exog(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================
# STEP 4: Convert to vector
# ============================================================
print("=" * 60)
print("STEP 4: Convert dy_inv_exog to vector")
print("=" * 60)

try:
    regions_list = MRIO_BASE.R['Region_acronyms'].to_list()
    sectors_list = MRIO_BASE.P['Lfd_Nr'].to_list()
    print(f"  Regions for vector: {regions_list}")
    print(f"  Number of sectors: {len(sectors_list)}")

    # Check if dy_inv_exog regions are in the regions list
    dy_regions = INV_model.dy_inv_exog['REG_imp'].unique()
    print(f"  Regions in dy_inv_exog: {list(dy_regions)}")
    missing_regions = [r for r in dy_regions if r not in regions_list]
    if missing_regions:
        print(f"  [WARNING] Regions in dy_inv_exog NOT in MRIO regions: {missing_regions}")

    dy_inv_exog = MRIO_df_to_vec(
        INV_model.dy_inv_exog,
        'REG_imp', 'TRAD_COMM', 'dy',
        regions_list,
        sectors_list
    )
    print(f"[OK] Vector created, shape: {dy_inv_exog.shape}")
    print(f"  Sum: {dy_inv_exog.sum():,.2f}")
    print(f"  Non-zero elements: {np.count_nonzero(dy_inv_exog)}")
except Exception as e:
    print(f"[ERROR] MRIO_df_to_vec(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================
# STEP 5: IO model
# ============================================================
print("=" * 60)
print("STEP 5: IO Model - Calculate output changes")
print("=" * 60)

try:
    IO_model = IO(MRIO_BASE)
    IO_model.initialize()
    print("[OK] IO model initialized")
except Exception as e:
    print(f"[ERROR] IO initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    dq_total = IO_model.calc_dq_exog(dy_inv_exog)
    print(f"[OK] dq_total calculated, shape: {dq_total.shape}")
    print(f"  Sum: {dq_total.sum():,.2f}")
    print(f"  Non-zero elements: {np.count_nonzero(dq_total)}")
except Exception as e:
    print(f"[ERROR] calc_dq_exog(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================
# STEP 6: Employment calculation
# ============================================================
print("=" * 60)
print("STEP 6: Employment calculation")
print("=" * 60)

try:
    # Employment baseline
    empl_base_df = MRIO_BASE.LABOR_BASE.copy()
    print(f"  LABOR_BASE shape: {empl_base_df.shape}")
    print(f"  LABOR_BASE columns: {list(empl_base_df.columns)}")

    # Check if BOL is in LABOR_BASE
    if 'REG_imp' in empl_base_df.columns:
        labor_countries = empl_base_df['REG_imp'].unique()
        print(f"  Countries in LABOR_BASE: {list(labor_countries)}")
        print(f"  Is 'BOL' in LABOR_BASE? {'BOL' in labor_countries}")

    empl_base_df["vol_low"] = empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"]
    empl_base_df["vol_high"] = empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
    empl_base_df["vol_total"] = empl_base_df["vol_low"] + empl_base_df["vol_high"]

    empl_base = MRIO_df_to_vec(
        empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]],
        "REG_imp", "PROD_COMM", "vol_total",
        regions_list,
        sectors_list
    )
    print(f"[OK] empl_base vector created, shape: {empl_base.shape}")
except Exception as e:
    print(f"[ERROR] Employment baseline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    Empl_model = empl(MRIO_BASE)
    Empl_model.build_empl_coef()
    print("[OK] Employment model built")
except Exception as e:
    print(f"[ERROR] build_empl_coef(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)
    print("[OK] calc_empl_multiplier()")
except Exception as e:
    print(f"[ERROR] calc_empl_multiplier(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    dempl = Empl_model.calc_dempl(dq_total)
    print(f"[OK] calc_dempl() completed")
    print(f"  dempl type: {type(dempl)}")
    if hasattr(dempl, 'shape'):
        print(f"  dempl shape: {dempl.shape}")
    elif isinstance(dempl, (list, tuple)):
        print(f"  dempl length: {len(dempl)}")
        if len(dempl) > 0 and hasattr(dempl[0], 'shape'):
            print(f"  dempl[0] shape: {dempl[0].shape}")
    print(f"  Total employment change: {np.sum(dempl):,.2f}")
except Exception as e:
    print(f"[ERROR] calc_dempl(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================
# STEP 7: Extract Bolivia results
# ============================================================
print("=" * 60)
print("STEP 7: Extract Bolivia-specific results")
print("=" * 60)

try:
    country_idx = {country: i for i, country in enumerate(MRIO_BASE.COU_ID)}
    print(f"  Country index mapping: {country_idx}")

    if 'BOL' in country_idx:
        c_idx = country_idx['BOL']
        c_start = c_idx * 120
        c_end = c_start + 120
        print(f"  BOL index: {c_idx}, range: [{c_start}, {c_end})")

        if isinstance(dempl, np.ndarray):
            bol_jobs = dempl[c_start:c_end]
        elif isinstance(dempl, (list, tuple)):
            bol_jobs = dempl[0][c_start:c_end] if hasattr(dempl[0], '__getitem__') else None
        else:
            bol_jobs = None

        if bol_jobs is not None:
            print(f"  BOL total jobs: {bol_jobs.sum():,.2f}")
            print(f"  BOL non-zero sectors: {np.count_nonzero(bol_jobs)}")
        else:
            print(f"  [WARNING] Could not extract BOL results from dempl")
    else:
        print(f"  [ERROR] 'BOL' not found in country_idx!")
except Exception as e:
    print(f"[ERROR] Extracting results: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================
# STEP 8: Check dimensions of pre-computed data
# ============================================================
print("=" * 60)
print("STEP 8: Check dimensions of pre-computed MRIO data")
print("=" * 60)

import scipy.io
import pickle

ssp_data_path = os.path.join(mindset_root, "GLORIA_db", "v57", "2019", "SSP")

# Check L_BASE dimensions
L_path = os.path.join(ssp_data_path, "GLORIA_L_Base_2019.mat")
if os.path.exists(L_path):
    L_data = scipy.io.loadmat(L_path)
    for key in L_data:
        if not key.startswith('_'):
            print(f"  L_BASE['{key}'] shape: {L_data[key].shape}")
else:
    print(f"  L_BASE file not found: {L_path}")

# Check IND_sparse
IND_path = os.path.join(ssp_data_path, "IND_sparse.pkl")
if os.path.exists(IND_path):
    IND = pd.read_pickle(IND_path)
    print(f"\n  IND_sparse shape: {IND.shape}")
    print(f"  IND_sparse columns: {list(IND.columns)}")
    if 'REG_imp' in IND.columns:
        print(f"  IND countries: {sorted(IND['REG_imp'].unique())}")
    if 'REG_exp' in IND.columns:
        print(f"  IND REG_exp: {sorted(IND['REG_exp'].unique())}")

# Check cid.pkl
cid_path = os.path.join(ssp_data_path, "cid.pkl")
if os.path.exists(cid_path):
    with open(cid_path, 'rb') as f:
        cid = pickle.load(f)
    print(f"\n  cid.pkl: {cid}")

# Check INV_CONV from GLORIA_template
inv_conv_path = os.path.join(mindset_root, "GLORIA_template", "Investment converter", "INV_CONV.xlsx")
if os.path.exists(inv_conv_path):
    inv_conv_raw = pd.read_excel(inv_conv_path)
    print(f"\n  INV_CONV.xlsx shape: {inv_conv_raw.shape}")
    print(f"  INV_CONV.xlsx columns: {list(inv_conv_raw.columns)}")
    if 'REG_imp' in inv_conv_raw.columns:
        print(f"  INV_CONV countries: {sorted(inv_conv_raw['REG_imp'].unique())}")
else:
    # Try other possible paths
    inv_conv_paths = [
        os.path.join(mindset_root, "GLORIA_template", "Investment converter"),
        os.path.join(mindset_root, "GLORIA_template"),
    ]
    for p in inv_conv_paths:
        if os.path.exists(p):
            print(f"\n  Files in {p}:")
            for f in os.listdir(p):
                print(f"    {f}")

# Check labor_data.pkl
labor_path = os.path.join(ssp_data_path, "labor_data.pkl")
if os.path.exists(labor_path):
    labor = pd.read_pickle(labor_path)
    print(f"\n  labor_data.pkl shape: {labor.shape}")
    if 'REG_imp' in labor.columns:
        print(f"  labor_data countries: {sorted(labor['REG_imp'].unique())}")

print()
print("=" * 60)
print("DIAGNOSIS SUMMARY")
print("=" * 60)
print()
print(f"Variable_list regions (R sheet): 9 regions including BOL")
print(f"L_BASE matrix: 960x960 = 8 regions x 120 sectors")
print(f"dy_inv_exog vector: 1080 = 9 regions x 120 sectors")
print()
print("ROOT CAUSE: The pre-computed SSP data (L_BASE, IND_sparse, etc.)")
print("was generated for 8 regions only. Bolivia was added to the Variable")
print("list but the underlying data was NOT re-aggregated to include it.")
print()
print("SOLUTION: Re-run the MRIO collapse/aggregation script to include")
print("Bolivia as its own region (extract from ROW) and regenerate:")
print("  - GLORIA_L_Base_2019.mat")
print("  - IND_sparse.pkl")
print("  - All other SSP data files")
print("  - INV_CONV (investment converter) for BOL")
print()
print("=" * 60)
