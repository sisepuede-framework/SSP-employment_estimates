"""
Read-only verification: does the production Variable_list point INV_CONV at an
identity matrix, and is the loaded matrix actually diagonal?

Writes findings to VERIFY_INV_CONV_OUTPUT.txt. Modifies nothing.
"""
import os
import numpy as np
import pandas as pd

ROOT = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\SSP-employment_estimates\MINDSET_module-main"
VARLIST = os.path.join(ROOT, "GLORIA_template", "Variables", "Variable_list_MINDSET_SSP.xlsx")
OUT = os.path.join(ROOT, "Claude Code", "temp", "VERIFY_INV_CONV_OUTPUT.txt")

lines = []
def w(s): lines.append(str(s))

try:
    var = pd.read_excel(VARLIST, "variables")
    w("=== variables sheet columns ===")
    w(list(var.columns))
    row = var[var["Variable name (new)"].astype(str).str.strip() == "INV_CONV"]
    if len(row) == 0:
        w("\n[!] No INV_CONV row found in variable list.")
    else:
        loc = str(row.iloc[0]["Location"])
        typ = str(row.iloc[0].get("Type", "n/a"))
        w(f"\nINV_CONV Location: {loc}")
        w(f"INV_CONV Type:     {typ}")

        full = os.path.join(ROOT, loc.replace("/", os.sep).replace("\\", os.sep))
        w(f"Resolved path:     {full}")
        w(f"Exists:            {os.path.exists(full)}")

        if os.path.exists(full):
            if full.lower().endswith(".csv"):
                m = pd.read_csv(full)
            else:
                m = pd.read_excel(full)
            w(f"\nLoaded shape: {m.shape}")
            # Drop a leading label column if present (e.g. 'Unnamed: 0')
            num = m.copy()
            first = num.columns[0]
            if num[first].dtype == object or str(first).startswith("Unnamed"):
                num = num.iloc[:, 1:]
            arr = num.to_numpy(dtype=float)
            w(f"Numeric block shape: {arr.shape}")
            if arr.shape[0] == arr.shape[1]:
                diag = np.diag(arr)
                offdiag_sum = arr.sum() - diag.sum()
                w(f"Diagonal: min={diag.min():.4f} max={diag.max():.4f} mean={diag.mean():.4f}")
                w(f"Off-diagonal absolute sum: {np.abs(arr - np.diag(diag)).sum():.6f}")
                is_ident = np.allclose(arr, np.eye(arr.shape[0]), atol=1e-6)
                w(f"IS IDENTITY: {is_ident}")
            else:
                # non-square: column-sum check (converter columns should sum to 1)
                w(f"Non-square. Column sums sample: {arr.sum(axis=0)[:5]}")
                w(f"Max off-diagonal-ish mass per col (1 - max): "
                  f"{(1 - np.max(arr, axis=0))[:5]}")
except Exception as e:
    w(f"[ERROR] {type(e).__name__}: {e}")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("done")
