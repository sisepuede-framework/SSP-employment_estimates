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

HOW THIS DIFFERS FROM BATCH (documented, agreed with Fernando 2026-07-26):
  BATCH feeds the scenario vector through MINDSET's investment module
  (INV_CONV capital-formation converter + fcf_share). That machinery answers a
  DIFFERENT question -- "when a sector invests, which capital goods does it buy
  and from where" -- and, via an inner join on capital-formation flows, silently
  ZEROED any product with no capital-formation (products 18/29/115 came out dead).
  Our cost structures are a BILL OF MATERIALS in final-demand space
  ("$x is spent buying product g"), so that module does not apply.

  We therefore DROP the investment module entirely and book demand directly:
      dq = L_BASE @ f_domestic ;  dempl = empl_multiplier * dq ;  keep MAR rows.

  IMPORT HAIRCUT (prevents inflating the multiplier with money that flows
  abroad): a $ of final demand for product p in MAR is only partly met by
  domestic producers. We keep the domestically-sourced share s_p:
      f_domestic[p] = f[p] * s_p
      s_p = domestic_MAR_final_demand(p) / total_MAR_final_demand(p)
  s_p is computed from the MRIO base's OWN final-demand tables (HH + GOV + FCF
  + NPISH), pooled by origin (REG_exp==MAR vs all). This mirrors the logic
  MINDSET already uses in invest.calc_inv_share, but on TOTAL final demand
  rather than capital formation only. Upstream intermediate imports still leak
  abroad through the inverse (foreign output rows are dropped), so BOTH import
  margins are handled.

  Two deliberate rules for s_p (verified against the MAR base 2026-07-26):
    - INV_BASE (inventory changes) is EXCLUDED: it carries legitimately negative
      entries that produce nonsensical shares (observed range -1.49..1.0). The
      other four categories are all non-negative.
    - product imported 100% (domestic supply missing but demand>0) -> s_p = 0
      (5 MAR products, e.g. Hard coal, Petroleum extraction). A pure 0/0 product
      (no final demand at all) would fall back to s_p = 1; none exist for MAR.

  Net operator:
      L = keep_domestic( diag(empl_multiplier) @ L_BASE @ diag(s) )

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
from SourceCode.InputOutput_SSP import IO
from SourceCode.employment import empl
from SourceCode.utils import MRIO_df_to_vec


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
# STEP 2: Domestic-source share s_p from the MRIO base's final-demand tables
# ---------------------------------------------------------------------------
# s_p = domestic_MAR_final_demand(p) / total_MAR_final_demand(p), pooling
#       HH + GOV + FCF + NPISH by origin (REG_exp==TARGET vs all).
# INV_BASE (inventory changes) is excluded: it has legitimately negative entries
# that produce nonsensical (<0 or >1) shares. See header for the full rationale.
print("STEP 2: Building domestic-source share s_p (import haircut)")
print("-" * 80)
prod_str = [str(p) for p in sector_list]

_FD_TABLES = [('HH_BASE', 'VIPA'), ('GOV_BASE', 'VIGA'),
              ('FCF_BASE', 'VDFA'), ('NPISH_BASE', 'NPISH')]  # INV_BASE excluded


def _fd_long(name, val):
    """Return final-demand table as REG_imp | REG_exp | TRAD_COMM | v (or empty)."""
    tbl = getattr(MRIO_BASE, name, None)
    if tbl is None or len(tbl) == 0:
        return pd.DataFrame(columns=['REG_imp', 'REG_exp', 'TRAD_COMM', 'v'])
    t = tbl.reset_index()
    if val not in t.columns:
        return pd.DataFrame(columns=['REG_imp', 'REG_exp', 'TRAD_COMM', 'v'])
    return t.rename(columns={val: 'v'})[['REG_imp', 'REG_exp', 'TRAD_COMM', 'v']]


fd = pd.concat([_fd_long(n, v) for n, v in _FD_TABLES], ignore_index=True)
fd = fd[fd['REG_imp'] == TARGET_ISO].copy()
fd['TRAD_COMM'] = fd['TRAD_COMM'].astype(int)

idx = list(range(1, len(sector_list) + 1))
tot = fd.groupby('TRAD_COMM')['v'].sum().reindex(idx, fill_value=0.0)
dom = (fd[fd['REG_exp'] == TARGET_ISO]
       .groupby('TRAD_COMM')['v'].sum().reindex(idx, fill_value=0.0))

# s_p: domestic share where demand exists; 0/0 (no final demand at all) -> 1.
with np.errstate(divide='ignore', invalid='ignore'):
    s_vals = np.where(tot.values > 0, dom.values / tot.values, 1.0)
s_p = np.clip(s_vals, 0.0, 1.0)   # guard rounding; INV already excluded

n_full_import = int(np.sum((tot.values > 0) & (s_p == 0.0)))
n_full_dom = int(np.sum(s_p == 1.0))
n_no_fd = int(np.sum(tot.values == 0))
print(f"[OK] s_p built: median={np.median(s_p):.3f}, "
      f"range [{s_p.min():.3f}, {s_p.max():.3f}]")
print(f"  fully imported (s_p=0, demand>0): {n_full_import} products")
print(f"  fully domestic  (s_p=1):          {n_full_dom} products")
print(f"  no final demand -> s_p=1 fallback: {n_no_fd} products")
print()


# ---------------------------------------------------------------------------
# Per-vector chain: f -> domestic haircut -> Leontief -> employment
# ---------------------------------------------------------------------------
def demand_to_dempl(dk_vector_120):
    """Full linear chain for a 120-vector of $ final demand booked to each
    product in TARGET_ISO. Applies the domestic-source haircut s_p, routes
    through the Leontief inverse, then employment multipliers. Returns the
    full stacked dempl vector (length N_VEC)."""
    f_dom = np.asarray(dk_vector_120, dtype=float) * s_p     # import haircut
    dy_vec = np.zeros(N_VEC)
    dy_vec[dom_start:dom_end] = f_dom                        # book to TARGET block
    dq = IO_model.calc_dq_exog(dy_vec)
    dempl = Empl_model.calc_dempl(dq)
    return np.asarray(dempl, dtype=float)


def demand_to_dempl_direct(dk_vector_120):
    """DIRECT-only jobs (S25): employment to produce the final-demand goods
    THEMSELVES, with NO supply-chain (indirect) rounds. Identical to
    demand_to_dempl but SKIPPING the Leontief inverse: dq = dy instead of
    dq = L_BASE @ dy. calc_dq_exog is dq = L_BASE @ dy (InputOutput.py:421),
    so dropping it leaves the direct output = final demand. INDIRECT = total -
    direct downstream. Same import haircut s_p as the total chain."""
    f_dom = np.asarray(dk_vector_120, dtype=float) * s_p     # same import haircut
    dy_vec = np.zeros(N_VEC)
    dy_vec[dom_start:dom_end] = f_dom
    dempl = Empl_model.calc_dempl(dy_vec)                    # dq = dy (no inverse)
    return np.asarray(dempl, dtype=float)


# ---------------------------------------------------------------------------
# STEP 3: Extract L column by column via unit vectors
# ---------------------------------------------------------------------------
print("STEP 3: Extracting L column-by-column (120 unit vectors)")
print("-" * 80)
c_idx = COU_ID.index(TARGET_ISO)
dom_start, dom_end = c_idx * len(sector_list), c_idx * len(sector_list) + len(sector_list)

L_full = np.zeros((N_VEC, len(sector_list)))     # full output rows x 120 demand cols
L_full_dir = np.zeros((N_VEC, len(sector_list)))  # DIRECT-only counterpart (S25)
t0 = time.time()
for j in range(len(sector_list)):
    unit = np.zeros(len(sector_list)); unit[j] = 1.0
    L_full[:, j] = demand_to_dempl(unit)
    L_full_dir[:, j] = demand_to_dempl_direct(unit)   # no Leontief inverse
    if (j + 1) % 30 == 0:
        print(f"  {j + 1}/{len(sector_list)} columns")
L_dom = L_full[dom_start:dom_end, :]             # domestic output rows only (120 x 120)
L_dom_dir = L_full_dir[dom_start:dom_end, :]     # direct-only (should be ~diagonal)
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

# DIRECT matrix checks (S25): must reproduce the direct chain, and INDIRECT =
# total - direct must be non-negative (indirect rounds only add employment).
max_err_dir = 0.0
for k in range(5):
    f = rng.random(len(sector_list)) * 1000.0
    chain_dir = demand_to_dempl_direct(f)[dom_start:dom_end]
    err = np.max(np.abs(chain_dir - L_dom_dir @ f))
    max_err_dir = max(max_err_dir, err)
print(f"  max |L_dir@f - direct_chain(f)|: {max_err_dir:.3e}  "
      f"{'[PASS]' if max_err_dir < VALIDATE_TOL else '[FAIL]'}")
L_indirect = L_dom - L_dom_dir
if (L_indirect < -VALIDATE_TOL).any():
    print(f"  [WARN] {(L_indirect < -VALIDATE_TOL).sum()} negative indirect entries "
          f"(min {L_indirect.min():.3e}) -> direct exceeds total somewhere.")
else:
    print("  [OK] indirect (total - direct) >= 0 everywhere.")
off_diag = L_dom_dir.copy(); np.fill_diagonal(off_diag, 0.0)
print(f"  direct matrix off-diagonal max = {np.abs(off_diag).max():.3e} (expect ~0: "
      f"direct jobs land only in the demanded product's own sector).")
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

# DIRECT matrix (S25): same shape/index, direct-only jobs per $1 of final demand.
L_dir_df = pd.DataFrame(L_dom_dir, index=sector_list, columns=sector_list)
L_dir_df.index.name = "output_product"
L_dir_df.columns.name = "demand_product"
L_dir_path = os.path.join(out_dir, f"L_matrix_direct_{TARGET_ISO}.csv")
L_dir_df.to_csv(L_dir_path)

idx_df = pd.DataFrame({"product_code": sector_list, "product_name": prod_names})
idx_df.to_csv(os.path.join(out_dir, f"L_matrix_{TARGET_ISO}_rowindex.csv"), index=False)
idx_df.to_csv(os.path.join(out_dir, f"L_matrix_{TARGET_ISO}_colindex.csv"), index=False)

print(f"[OK] SAVED: {os.path.abspath(L_path)}")
print(f"[OK] SAVED: {os.path.abspath(L_dir_path)}  (direct-only; total-direct=indirect)")
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
