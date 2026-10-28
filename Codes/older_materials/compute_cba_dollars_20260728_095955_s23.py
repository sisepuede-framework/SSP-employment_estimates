"""
compute_cba_dollars.py  (Session 17, 2026-07-27)

Replicates the SISEPUEDE CBA engine (costs_benefits_ssp/cb_calculate.py) for the
decomposed-computable transformation-cost lines, emitting one dollar figure per
(output_variable_name, time_period) for the Morocco run.

WHY THIS EXISTS: R segfaults on the 4119-col decomposed file; and Python->Python
transcription from the engine minimizes divergence. Engine is NEVER run here
(locked rule); its formulas are re-implemented from source, verified line-by-line.

MERGE KEY: decomposed_ssp_output.csv has ONLY primary_id/region/time_period
(no strategy_code, no future_id). Both runs have future_id=0 and region=morocco,
so merging on time_period ALONE == engine's [region,time_period,future_id] merge.

RUNS: primary_id 72072 = BAU (base), 73073 = LEDS (tx). Delta = tx - base.

FORMULA SOURCES (cb_calculate.py line numbers, verified S17):
  cb_difference_between_two_strategies  : 1083  value=(var_tx-var_base)*mult*ac^max(0,t-8)
  cb_scale_variable_in_strategy         : 1143  value=var_TX*mult*ac^max(0,t-8)  (TX LEVEL, baseline 0)
  cb_fraction_change                    : 1212  value=effect_TX*(1-frac_tx/frac_base)*mult*ac^max(0,t-8); NaN->0
  cb_manure_management_cost             : 1946  value=tlu_TX*implementation*mult (TX LEVEL; positional ramp)
  cb_ippu_clinker                       : 1327  EXCLUDED (unit bug, see below)
Wrapper (decorators/cb_wrappers.py:71-119): difference_variable resolved as
  re.compile(pat.replace("*",".*")).match(col)  -> PREFIX match (no $).
  Multiple matches: sum==1 -> sum; sum==0 -> append. Either way the per-line
  dollar TOTAL = sum across matched columns (same mult & ac^t factor), so we sum.
Constants (config/cb_config.py): TIME_PERIOD_2023=8, TIME_PERIODS=36.
"""

import re
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Paths (anchored on THIS script's location, so CWD does not matter)
# ----------------------------------------------------------------------------
# This script lives in  SSP-employment_estimates/Codes/  (admin: Fernando).
#   REPO       = ..            (the SSP-employment_estimates repo root)
#   REPOS_ROOT = ../..         (the container folder that also holds ssp_morocco)
# Outputs go INSIDE this repo so the Rmd never needs ssp_morocco; this producer is
# the ONLY step that reads ssp_morocco (run by Fernando, who has both repos synced).
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.path.normpath(_os.path.join(_HERE, ".."))
REPOS_ROOT = _os.path.normpath(_os.path.join(_HERE, "..", ".."))

# Authoritative config (in the separate ssp_morocco repo). If locked open in Excel
# (PermissionError), fall back to a temp copy at REPOS_ROOT (_cbp_tmp.xlsx).
CFG = _os.path.join(REPOS_ROOT,
                    "ssp_morocco/ssp_modeling/cost-benefits/cb_config_files/cb_config_params.xlsx")
CFG_FALLBACK = _os.path.join(REPOS_ROOT, "_cbp_tmp.xlsx")
DEC = _os.path.join(REPO, "Data/CBA/sisepuede_results/"
                    "sisepuede_results_sisepuede_run_2026-07-16/decomposed_ssp_output.csv")
OUT = _os.path.join(REPO, "Data/CBA/cba_dollars_by_line.csv")
# Accounting CSV: one row per config line (all 55) + its disposition, so the Rmd
# can reproduce the full silent-drop log without reading cb_config_params.xlsx.
OUT_ACCT = _os.path.join(REPO, "Data/CBA/cba_line_accounting.csv")

BASE_ID, TX_ID = 72072, 73073          # BAU, LEDS
TIME_PERIOD_2023 = 8
TIME_PERIODS = 36
TX_START = 10                          # SSP_GLOBAL_TIME_PERIOD_TX_START
ISO = "MAR"

# Families computable from the decomposed output alone.
COMPUTABLE = {
    "cb_difference_between_two_strategies",
    "cb_scale_variable_in_strategy",
    "cb_fraction_change",
    "cb_manure_management_cost",
    # Session 20: external-table lines whose cache tables HAVE Morocco data:
    "cb_agrc_rice_mgmt",               # agrc_rice_mgmt_tx (time-indexed, country-agnostic)
    "cb_lvst_enteric",                 # LVST_enteric_fermentation_tx (country-agnostic)
    # NOT added (MAR ABSENT from their iso-keyed cache -> engine yields nothing for
    # Morocco, verified S20): cb_entc_reduce_losses (entc_reduce_losses_cost_file has
    # no MAR row), cb_agrc_lvst_productivity (agrc_lvst_productivity_costgdp has no MAR
    # row). These stay deferred with a corrected reason below.
}

# --- external cache tables (read from cb_config_params.xlsx sheets, Session 20) ---
# rice: level_of_implementation(tp) = (1 - ef(tp)) / 0.45 ; value = area_rice_tx * loi * mult
RICE_SHEET = "agrc_rice_mgmt_tx"
# enteric: per affected livestock var, application_in_year(tp) =
#   application/(TIME_PERIODS-TX_START) * (tp-TX_START+1), 0 for tp<=TX_START-1;
#   value = sum_v pop_v_tx(tp) * application_in_year_v(tp) * mult
ENTERIC_SHEET = "LVST_enteric_fermentation_tx"
# Excluded WITH a logged reason (not silent). See advisor table, Session 17.
EXCLUDE_REASON = {
    "cb:ippu:technical_cost:clinker:X":
        "CONFIG/UNIT BUG: 1/(1-d) needs a fraction but diff_var=prod_ippu_cement_tonne "
        "feeds tonnes -> collapses to ~ -cement_tx = -$20.4B. Correct var frac_ippu_cement_clinker "
        "exists but is not wired. DEFERRED pending advisor (fix in config).",
    "cb:ippu:technical_cost:industrial_ccs:X":
        "CONFIG BUG: annual_change=0 -> 0^(t-8) zeroes the line post-2023. Should be 1. "
        "Also needs external ippu_ccs_cost_factors table. DEFERRED pending advisor.",
    "cb:entc:technical_cost:loss_reduction:electricity":
        "MISSING COUNTRY DATA: entc_reduce_losses_cost_file has NO MAR row (annual_investment_USD "
        "is iso-keyed, merges on region). Engine yields nothing for Morocco. Verified S20.",
    "cb:agrc:technical_cost:increase_productivity:X":
        "MISSING COUNTRY DATA: agrc_lvst_productivity_costgdp has NO MAR row (cost_frac is "
        "iso-keyed, merges on region). Engine yields nothing for Morocco. Verified S20.",
    "cb:lvst:technical_cost:increase_productivity:X":
        "MISSING COUNTRY DATA: agrc_lvst_productivity_costgdp has NO MAR row (cost_frac is "
        "iso-keyed, merges on region). Engine yields nothing for Morocco. Verified S20.",
}


def resolve_cols(pattern, headers):
    """Engine wildcard: re.compile(pat.replace('*','.*')).match(col) -> PREFIX match."""
    rx = re.compile(str(pattern).replace("*", ".*"))
    return [c for c in headers if rx.match(c)]


def main():
    import os
    cfg_path = CFG
    try:
        tc = pd.read_excel(cfg_path, sheet_name="transformation_costs")
    except PermissionError:
        if not os.path.exists(CFG_FALLBACK):
            raise
        print(f"[WARN] {CFG} locked; reading fallback copy {CFG_FALLBACK}")
        cfg_path = CFG_FALLBACK
        tc = pd.read_excel(cfg_path, sheet_name="transformation_costs")
    headers = list(pd.read_csv(DEC, nrows=0).columns)

    # external cache sheets (same workbook)
    rice_tx = pd.read_excel(cfg_path, sheet_name=RICE_SHEET)
    rice_tx["level_of_implementation"] = (1 - rice_tx["ef_agrc_anaerobicdom_rice_kg_ch4_ha"]) / 0.45
    enteric_tx = pd.read_excel(cfg_path, sheet_name=ENTERIC_SHEET)
    enteric_aff = enteric_tx[enteric_tx["application"] > 0].copy()   # affected livestock only

    # Collect every column any computable line needs (diff_var matches + arg1), read once.
    need = {"primary_id", "time_period"}
    need |= set(enteric_aff["variable"].tolist())                    # enteric livestock pop cols
    for _, r in tc.iterrows():
        if r["cb_function"] not in COMPUTABLE:
            continue
        need |= set(resolve_cols(r["difference_variable"], headers))
        if isinstance(r["arg1"], str) and r["arg1"] != "ND":
            need |= set(resolve_cols(r["arg1"], headers))
    d = pd.read_csv(DEC, usecols=lambda c: c in need)

    # Base/tx indexed by time_period (single row per period; future_id=0, region=morocco).
    base = d[d["primary_id"] == BASE_ID].set_index("time_period").sort_index()
    tx = d[d["primary_id"] == TX_ID].set_index("time_period").sort_index()
    periods = tx.index                              # tp 3..35 (33 periods), ascending
    tpmc = np.maximum(0, periods.to_series() - TIME_PERIOD_2023)  # max(0, t-8)

    out_rows = []
    log = {"live": [], "zero": [], "excluded": [], "skipped_include_false": [],
           "deferred_external": []}

    for _, r in tc.iterrows():
        ov = r["output_variable_name"]
        fn = r["cb_function"]
        mult = float(r["multiplier"])
        ac = float(r["annual_change"])
        sm = bool(r["sum"])

        # include==False -> engine would not book it; log, skip.
        if not bool(r["include"]):
            log["skipped_include_false"].append(ov)
            continue

        # Explicit exclusions (config bugs) -> log, skip. Do NOT emit garbage.
        if ov in EXCLUDE_REASON:
            log["excluded"].append((ov, EXCLUDE_REASON[ov]))
            continue

        # Non-computable families (external cache tables) -> deferred, log.
        if fn not in COMPUTABLE:
            log["deferred_external"].append((ov, fn))
            continue

        cols = resolve_cols(r["difference_variable"], headers)

        if fn == "cb_difference_between_two_strategies":
            # value = (tx - base) summed over matched cols, * mult * ac^max(0,t-8)
            delta = (tx[cols].sum(axis=1) - base[cols].sum(axis=1))
            val = delta * mult * (ac ** tpmc)

        elif fn == "cb_scale_variable_in_strategy":
            # TX LEVEL only (baseline 0). value = var_tx * mult * ac^max(0,t-8)
            val = tx[cols].sum(axis=1) * mult * (ac ** tpmc)

        elif fn == "cb_fraction_change":
            fv = r["arg1"]
            invert = r["arg2"]
            ft = tx[fv].astype(float).copy()
            fb = base[fv].astype(float).copy()
            if invert == 1:
                ft = 1.0 / ft
                fb = 1.0 / fb
            fmult = 1.0 - (ft / fb)                 # (1 - frac_tx/frac_base)
            effect = tx[cols].sum(axis=1)           # effect from TX run, summed over cols
            val = effect * fmult * mult * (ac ** tpmc)
            val = val.replace([np.inf, -np.inf], np.nan).fillna(0.0)  # engine: NaN->0 (guard inf too)

        elif fn == "cb_manure_management_cost":
            # TX LEVEL * positional adoption ramp * mult. Ramp assumes rows are tp0..35;
            # our file is tp3..35, so it lands ~3 periods early (replicates engine as-is).
            impl = [0] * 11 + list(np.linspace(0, 0.95, TIME_PERIODS - 11))  # len 36
            tlu = tx[cols].sum(axis=1).reset_index(drop=True)               # file row order
            n = len(tlu)
            impl_aligned = pd.Series(impl[:n])       # positional; extra ramp tail dropped
            val_pos = tlu * impl_aligned * mult      # NaN where impl ran short -> engine .dropna()
            val = pd.Series(val_pos.values, index=periods)

        elif fn == "cb_agrc_rice_mgmt":
            # value = area_rice_tx(tp) * level_of_implementation(tp) * mult ; baseline 0.
            loi = rice_tx.set_index("time_period")["level_of_implementation"]
            area = tx[cols].sum(axis=1)              # area_agrc_crops_rice, TX run
            loi_al = loi.reindex(periods)
            val = area * loi_al * mult

        elif fn == "cb_lvst_enteric":
            # value = sum_v pop_v_tx(tp) * application_in_year_v(tp) * mult.
            # application_in_year = application/(TIME_PERIODS-TX_START)*(tp-TX_START+1),
            # 0 for tp <= TX_START-1. (Ramp identical shape for all affected livestock.)
            ramp = np.where(periods.to_numpy() <= TX_START - 1, 0.0,
                            (periods.to_numpy() - TX_START + 1) / (TIME_PERIODS - TX_START))
            ramp = pd.Series(ramp, index=periods)
            val = pd.Series(0.0, index=periods)
            for _, lr in enteric_aff.iterrows():
                v = lr["variable"]
                if v not in tx.columns:
                    continue
                val = val + tx[v].astype(float) * (lr["application"] * ramp) * mult

        else:
            continue

        total = float(np.nansum(val.values))
        for tp, v in zip(periods, val.values):
            out_rows.append({"output_variable_name": ov,
                             "time_period": int(tp),
                             "cba_dollars": float(v)})

        # A line is "zero" only if it computed to ~0 across all periods (option b: keep visible).
        if abs(total) <= 1e-6:
            log["zero"].append((ov, fn))
        else:
            log["live"].append((ov, total))

    res = pd.DataFrame(out_rows)
    res.to_csv(OUT, index=False)

    # ---- accounting CSV: one row per config line (all 55) + disposition -------
    # Lets the Rmd reproduce the full silent-drop log with NO ssp_morocco read.
    acct = []
    for ov, t in log["live"]:
        acct.append({"output_variable_name": ov, "disposition": "live",
                     "total_dollars": t, "reason": ""})
    for ov, fn in log["zero"]:
        acct.append({"output_variable_name": ov, "disposition": "visible_zero",
                     "total_dollars": 0.0,
                     "reason": f"computed ~0 across all periods [{fn}] (kept visible, option b)"})
    for ov, why in log["excluded"]:
        acct.append({"output_variable_name": ov, "disposition": "excluded_config_bug",
                     "total_dollars": float("nan"), "reason": why})
    for ov in log["skipped_include_false"]:
        acct.append({"output_variable_name": ov, "disposition": "include_false",
                     "total_dollars": float("nan"), "reason": "include==FALSE in config"})
    for ov, fn in log["deferred_external"]:
        acct.append({"output_variable_name": ov, "disposition": "deferred_external_table",
                     "total_dollars": float("nan"),
                     "reason": f"needs external cache table [{fn}]"})
    acct_df = pd.DataFrame(acct, columns=["output_variable_name", "disposition",
                                          "total_dollars", "reason"])
    acct_df.to_csv(OUT_ACCT, index=False)
    print(f"WROTE {OUT_ACCT}: {len(acct_df)} config lines accounted "
          f"(live/visible_zero/excluded/include_false/deferred).\n")

    # ---- report -----------------------------------------------------------
    print(f"WROTE {OUT}: {len(res)} rows, "
          f"{res['output_variable_name'].nunique()} lines x {res['time_period'].nunique()} periods\n")

    print(f"LIVE lines (nonzero $): {len(log['live'])}")
    for ov, t in sorted(log["live"], key=lambda x: abs(x[1]), reverse=True):
        print(f"    {t:+.4e}  {ov}")

    print(f"\nVISIBLE $0 rows (kept, option b): {len(log['zero'])}")
    for ov, fn in log["zero"]:
        print(f"    0   {ov}  [{fn}]")

    print(f"\nEXCLUDED + logged (config bugs): {len(log['excluded'])}")
    for ov, why in log["excluded"]:
        print(f"    {ov}\n        {why}")

    print(f"\nSKIPPED include==False: {len(log['skipped_include_false'])}")
    for ov in log["skipped_include_false"]:
        print(f"    {ov}")

    print(f"\nDEFERRED external-table lines: {len(log['deferred_external'])}")
    for ov, fn in log["deferred_external"]:
        print(f"    {ov}  [{fn}]")

    # ---- acceptance check -------------------------------------------------
    hi = res[res["output_variable_name"] == "cb:inen:technical_cost:fuel_switch:hi_heat"]["cba_dollars"].sum()
    print(f"\nACCEPTANCE  INEN hi_heat total = {hi:.4e}  (target -3.48e9)  "
          f"{'PASS' if abs(hi - (-3.48e9)) < 0.02e9 else 'FAIL'}")


if __name__ == "__main__":
    main()
