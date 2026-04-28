"""
Examine INV_CONV and write results to file
"""
import sys
import os
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
mindset_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, mindset_root)
os.chdir(mindset_root)

output_file = "Claude Code/temp/INV_CONV_analysis.txt"

with open(output_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("EXAMINING INV_CONV MATRIX\n")
    f.write("="*80 + "\n\n")

    try:
        from SourceCode.exog_vars_SSP import exog_vars
        MRIO_BASE = exog_vars()

        f.write(f"INV_CONV type: {type(MRIO_BASE.INV_CONV)}\n")
        f.write(f"INV_CONV shape: {MRIO_BASE.INV_CONV.shape if hasattr(MRIO_BASE.INV_CONV, 'shape') else 'N/A'}\n\n")

        if isinstance(MRIO_BASE.INV_CONV, pd.DataFrame):
            f.write("Columns: " + str(list(MRIO_BASE.INV_CONV.columns)) + "\n\n")
            f.write("First 20 rows:\n")
            f.write(MRIO_BASE.INV_CONV.head(20).to_string() + "\n\n")

            if 'input_coeff' in MRIO_BASE.INV_CONV.columns:
                nonzero = (MRIO_BASE.INV_CONV['input_coeff'] > 0).sum()
                total = len(MRIO_BASE.INV_CONV)
                f.write(f"Non-zero entries: {nonzero}/{total} ({nonzero/total*100:.1f}%)\n\n")

                # Check diagonal
                diagonal_values = []
                for sector in range(1, 121):
                    sector_data = MRIO_BASE.INV_CONV[
                        (MRIO_BASE.INV_CONV['PROD_COMM'] == str(sector)) &
                        (MRIO_BASE.INV_CONV['TRAD_COMM'] == str(sector))
                    ]
                    if len(sector_data) > 0:
                        coeff = sector_data['input_coeff'].iloc[0]
                        diagonal_values.append((sector, coeff))

                f.write("Diagonal entries (sector → same product):\n")
                for sector, coeff in diagonal_values[:20]:
                    f.write(f"  Sector {sector:3d} → Product {sector:3d}: {coeff:.6f}\n")
                f.write(f"  ... ({len(diagonal_values)} total)\n\n")

                diag_array = np.array([v[1] for v in diagonal_values])
                f.write(f"Diagonal statistics:\n")
                f.write(f"  Mean: {diag_array.mean():.6f}\n")
                f.write(f"  Std:  {diag_array.std():.6f}\n")
                f.write(f"  Min:  {diag_array.min():.6f}\n")
                f.write(f"  Max:  {diag_array.max():.6f}\n\n")

                near_one = (np.abs(diag_array - 1.0) < 0.01).sum()
                f.write(f"Entries very close to 1.0 (±0.01): {near_one}/{len(diag_array)}\n\n")

        f.write("="*80 + "\n")
        f.write("SUCCESS: Analysis complete\n")

    except Exception as e:
        f.write(f"ERROR: {str(e)}\n")
        import traceback
        f.write(traceback.format_exc())

print(f"Output written to: {output_file}")
