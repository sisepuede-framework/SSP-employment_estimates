"""
EXTRACT_L_MATRIX.py
===================================================================
Extracts the STATIC employment-per-final-demand matrix L for a country,
so that jobs = L @ f can be computed in R for the CBA demand vectors and
every RDM draw WITHOUT ever re-running MINDSET.

    L[i, p] = domestic jobs in product i  per $1 of final demand
              booked to product p   (both i, p in 1..120, country = target)

WHAT IT REUSES FROM BATCH_EMPLOYMENT_ALL_STRATEGIES.py (unchanged):
  - exog_vars() MRIO base load
  - IO_model.initialize()            (Leontief inverse L_BASE, built once)
  - Empl_model.build_empl_coef() + calc_empl_multiplier()   (2019 coeffs)
  - the calc_dy_inv_exog -> calc_dq_exog -> calc_dempl chain

THE ONE DELIBERATE DIFFERENCE FROM BATCH (documented, agreed with Fernando):
  BATCH feeds the scenario vector through the *default* investment converter
  INV_CONV, which re-bundles "who invests" into a capital-good basket
  (PROD_COMM -> TRAD_COMM). That step is correct only if the input vector is
  an *investing-sector* vector. Our cost structures are already a
  BILL OF MATERIALS in final-demand space ("$x bought from product g"),
  so re-bundling would DOUBLE-PROCESS them. We therefore set INV_CONV to
  IDENTITY. We KEEP the FCF import-origin split (fcf_share): a $ of demand
  for product g is sourced partly domestically, partly imported; only the
  domestic share creates domestic jobs. Foreign output rows are dropped.

  Net operator:
      L = keep_domestic( diag(empl_multiplier) @ L_BASE @ FCF_origin_split )
  with the capital-formation converter neutralised.

VALIDATION (mode A, always run): rebuild the matrix column-by-column, then
  confirm  L @ f  reproduces the full per-vector chain for random f to ~1e-9.
  This proves the extraction is exact (the chain is fully linear).

OUTPUT (in "SSP - Results"):
  - L_matrix_<ISO>.csv          120 x 120, rows=output product, cols=demand product
  - L_matrix_<ISO>_rowindex.csv product code + name (output side, domestic)
  - L_matrix_<ISO>_colindex.csv product code + name (final-demand side)

RUN FROM: MINDSET_module-main root, or from "SSP - Codes" (auto-detected).
Author: Claude Code  |  Date: 2026-07-25
"""

import sys
import os
import time
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
TARGET_ISO = "MAR"          # v1 = Morocco only; loop-ready (see COUNTRY_NAMES)
N_PRODUCTS = 120
VALIDATE_TOL = 1e-8

COUNTRY_NAMES = {
    'BGR': 'Bulgaria', 'BLZ': 'Belize', 'EGY': 'Egypt', 'LBY': 'Libya',
    'MAR': 'Morocco', 'MEX': 'Mexico', 'UGA': 'Uganda', 'BOL': 'Bolivia'
}

# ---------------------------------------------------------------------------
# PATH SETUP (identical logic to BATCH so it runs from either location)
# ---------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(script_dir) == 'SSP - Codes':
    mindset_root = os.path.abspath(os.path.join(script_dir, ".."))
elif os.path.basename(script_dir) == 'temp':
    mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
else:
    mindset_root = script_dir

sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

print("=" * 80)
print("EXTRACT L MATRIX (employment per final demand)  ->  target:", TARGET_ISO)
print("=" * 80)
print("Working directory:", os.getcwd())
print()

# ---------------------------------------------------------------------------
# IMPORTS from MINDSET (same modules BATCH uses)
# ---------------------------------------------------------------------------
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.investment import invest
from SourceCode.InputOutput_SSP import IO
from SourceCode.employment import empl
from SourceCode.utils import MRIO_df_to_vec


class MockScenario:
    """invest.__init__ only needs .inv_spending; we build M from unit vectors,
    so no scenario file is read for the extraction itself."""
    def __init__(self):
        self.inv_spending = pd.DataFrame(columns=['REG_imp', 'PROD_COMM', 'inv_spend'])


# ---------------------------------------------------------------------------
# STEP 1: Load MRIO base + build static core ONCE (verbatim from BATCH 172-203)
# ---------------------------------------------------------------------------
print("STEP 1: Loading MRIO base and building static core (once)")
print("-" * 80)
t0 = time.time()
MRIO_BASE = exog_vars()
print(f"[OK] MRIO base loaded in {time.time() - t0:.1f}s")

COU_ID = MRIO_BASE.COU_ID
print(f"  Regions ({len(COU_ID)}): {', '.join(COU_ID)}")
if TARGET_ISO not in COU_ID:
    print(f"[ERROR] target {TARGET_ISO} not in regions.")
    sys.exit(1)

sector_list = MRIO_BASE.P['Lfd_Nr'].to_list()
if len(sector_list) != N_PRODUCTS:
    print(f"[WARN] expected {N_PRODUCTS} products, found {len(sector_list)}")

R_list = MRIO_BASE.R['Region_acronyms'].to_list()
N_VEC = len(R_list) * len(sector_list)   # full stacked-vector length

# employment baseline (BATCH lines 180-190)
empl_base_df = MRIO_BASE.LABOR_BASE.copy()
empl_base_df["vol_low"] = empl_base_df["vol_Fem_low"] + empl_base_df["vol_Male_low"]
empl_base_df["vol_high"] = empl_base_df["vol_Fem_high"] + empl_base_df["vol_Male_high"]
empl_base_df["vol_total"] = empl_base_df["vol_low"] + empl_base_df["vol_high"]
empl_base = MRIO_df_to_vec(
    empl_base_df[["REG_imp", "PROD_COMM", "vol_total"]],
    "REG_imp", "PROD_COMM", "vol_total",
    R_list, sector_list)

IO_model = IO(MRIO_BASE)
IO_model.initialize()
print("[OK] IO model initialized (Leontief inverse ready)")

Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(empl_base, IO_model.q_base)
print("[OK] Employment model ready")
print()

# ---------------------------------------------------------------------------
# STEP 2: Build IDENTITY investment converter (kills capital-formation re-bundle)
# ---------------------------------------------------------------------------
# INV_CONV schema expected by calc_dy_inv_exog: REG_imp | PROD_COMM | TRAD_COMM | input_coeff
# Identity => a $ booked to product p stays as demand for product p (final-demand semantics).
print("STEP 2: Building identity investment converter + FCF origin split")
print("-" * 80)
prod_str = [str(p) for p in sector_list]
identity_conv = pd.DataFrame({
    'REG_imp': np.repeat(R_list, len(sector_list)),
    'PROD_COMM': np.tile(prod_str, len(R_list)),
})
identity_conv['TRAD_COMM'] = identity_conv['PROD_COMM']
identity_conv['input_coeff'] = 1.0

INV_model = invest(MRIO_BASE, identity_conv, MockScenario())
INV_model.calc_inv_share()   # builds fcf_share (import-origin split); FCF base only
print("[OK] Converter = identity; FCF origin split retained")
print()


# ---------------------------------------------------------------------------
# Per-vector chain (mirrors BATCH 259-273 with identity converter)
# ---------------------------------------------------------------------------
def demand_to_dempl(dk_vector_120):
    """Full linear chain for a 120-vector of $ final demand booked to each
    product in TARGET_ISO. Returns the full stacked dempl vector (length N_VEC)."""
    exog_inv = pd.DataFrame({
        'REG_imp': TARGET_ISO,
        'PROD_COMM': prod_str,
        'dk': np.asarray(dk_vector_120, dtype=float),
    })
    INV_model.calc_dy_inv_exog(exog_inv)
    dy_vec = MRIO_df_to_vec(
        INV_model.dy_inv_exog, 'REG_imp', 'TRAD_COMM', 'dy',
        R_list, sector_list)
    dq = IO_model.calc_dq_exog(dy_vec)
    dempl = Empl_model.calc_dempl(dq)
    return np.asarray(dempl, dtype=float)


# ---------------------------------------------------------------------------
# STEP 3: Extract L column by column via unit vectors
# ---------------------------------------------------------------------------
print("STEP 3: Extracting L column-by-column (120 unit vectors)")
print("-" * 80)
c_idx = COU_ID.index(TARGET_ISO)
dom_start, dom_end = c_idx * len(sector_list), c_idx * len(sector_list) + len(sector_list)

L_full = np.zeros((N_VEC, len(sector_list)))     # full output rows x 120 demand cols
t0 = time.time()
for j in range(len(sector_list)):
    unit = np.zeros(len(sector_list)); unit[j] = 1.0
    L_full[:, j] = demand_to_dempl(unit)
    if (j + 1) % 30 == 0:
        print(f"  {j + 1}/{len(sector_list)} columns")
L_dom = L_full[dom_start:dom_end, :]             # domestic output rows only (120 x 120)
print(f"[OK] L extracted in {time.time() - t0:.1f}s   shape L_dom = {L_dom.shape}")
print(f"  domestic jobs per $1 (col sums) range: "
      f"{L_dom.sum(axis=0).min():.4g} .. {L_dom.sum(axis=0).max():.4g}")
print()

# ---------------------------------------------------------------------------
# STEP 4: VALIDATION - matrix must reproduce the per-vector chain exactly
# ---------------------------------------------------------------------------
print("STEP 4: Validation (linearity / extraction exactness)")
print("-" * 80)
rng = np.random.default_rng(0)
max_err = 0.0
for k in range(5):
    f = rng.random(len(sector_list)) * 1000.0
    chain_full = demand_to_dempl(f)
    chain_dom = chain_full[dom_start:dom_end]
    matrix_dom = L_dom @ f
    err = np.max(np.abs(chain_dom - matrix_dom))
    max_err = max(max_err, err)
print(f"  max |L@f - chain(f)| over 5 random vectors: {max_err:.3e}")
if max_err < VALIDATE_TOL:
    print("  [PASS] L reproduces the per-vector chain -> extraction is exact.")
else:
    print("  [FAIL] mismatch exceeds tolerance; do NOT use L. Investigate.")
    sys.exit(1)
if (L_dom < -VALIDATE_TOL).any():
    print("  [WARN] negative entries in L (unexpected for +demand).")
else:
    print("  [OK] all L entries >= 0.")
print()

# ---------------------------------------------------------------------------
# STEP 5: Save
# ---------------------------------------------------------------------------
print("STEP 5: Saving")
print("-" * 80)
out_dir = "SSP - Results"
os.makedirs(out_dir, exist_ok=True)

# product names for indices
if 'Sector' in MRIO_BASE.P.columns:
    prod_names = MRIO_BASE.P['Sector'].to_list()
elif 'Product' in MRIO_BASE.P.columns:
    prod_names = MRIO_BASE.P['Product'].to_list()
else:
    prod_names = MRIO_BASE.P.iloc[:, 1].to_list()

L_df = pd.DataFrame(L_dom, index=sector_list, columns=sector_list)
L_df.index.name = "output_product"      # jobs land here (domestic)
L_df.columns.name = "demand_product"    # $ booked here
L_path = os.path.join(out_dir, f"L_matrix_{TARGET_ISO}.csv")
L_df.to_csv(L_path)

idx_df = pd.DataFrame({"product_code": sector_list, "product_name": prod_names})
idx_df.to_csv(os.path.join(out_dir, f"L_matrix_{TARGET_ISO}_rowindex.csv"), index=False)
idx_df.to_csv(os.path.join(out_dir, f"L_matrix_{TARGET_ISO}_colindex.csv"), index=False)

print(f"[OK] SAVED: {os.path.abspath(L_path)}")
print(f"  rows (output products, domestic {TARGET_ISO}): {L_dom.shape[0]}")
print(f"  cols (final-demand products):                  {L_dom.shape[1]}")
print()
print("HOW TO USE IN R:")
print(f"  L <- as.matrix(read.csv('{L_path}', row.names=1, check.names=FALSE))")
print("  jobs <- L %*% f            # f = 120-vector of signed CBA $ by product")
print("  # jobs[i] = domestic jobs in product i; sum(jobs) = total domestic jobs")
print()
print("=" * 80)
print("DONE")
print("=" * 80)
