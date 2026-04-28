"""
Check if LABOR_BASE exists in SSP aggregated data
"""
import pandas as pd
import os
import sys

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

output_file = "Claude Code/temp/labor_base_check.txt"

with open(output_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("CHECKING FOR LABOR_BASE IN SSP DATA\n")
    f.write("="*80 + "\n\n")

    # Check Variable_list
    f.write("1. Variable_list_MINDSET_SSP.xlsx:\n")
    f.write("-"*80 + "\n")
    vlist = pd.read_excel('GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx')
    labor = vlist[vlist['Variable name'].str.contains('LABOR', na=False, case=False)]
    if len(labor) > 0:
        f.write(labor[['Variable name', 'Path', 'Type']].to_string(index=False))
        f.write("\n\n")
    else:
        f.write("LABOR_BASE NOT in Variable_list\n\n")

    # Check SSP folder
    f.write("2. Files in SSP folder:\n")
    f.write("-"*80 + "\n")
    ssp_folder = 'GLORIA_db/v57/2019/SSP'
    if os.path.exists(ssp_folder):
        all_files = os.listdir(ssp_folder)
        labor_files = [f for f in all_files if 'labor' in f.lower() or 'empl' in f.lower()]
        if labor_files:
            for f in labor_files:
                f.write(f"  {f}\n")
        else:
            f.write("  No labor/employment files found\n")
        f.write("\n")
    else:
        f.write("SSP folder not found!\n\n")

    # Check if we can load LABOR_BASE
    f.write("3. Attempting to load LABOR_BASE:\n")
    f.write("-"*80 + "\n")
    try:
        sys.path.insert(0, '.')
        from SourceCode.exog_vars_SSP import exog_vars
        MRIO = exog_vars()

        if hasattr(MRIO, 'LABOR_BASE'):
            f.write(f"✓ LABOR_BASE loaded successfully\n")
            f.write(f"  Shape: {MRIO.LABOR_BASE.shape}\n")
            f.write(f"  Columns: {list(MRIO.LABOR_BASE.columns)}\n\n")
            f.write("First 10 rows:\n")
            f.write(MRIO.LABOR_BASE.head(10).to_string() + "\n\n")

            # Check for required columns
            required_cols = ['vol_Fem_low', 'vol_Male_low', 'vol_Fem_high', 'vol_Male_high']
            missing = [c for c in required_cols if c not in MRIO.LABOR_BASE.columns]
            if missing:
                f.write(f"⚠ Missing required columns: {missing}\n")
            else:
                f.write("✓ All required columns present\n")
                # Calculate vol_total
                vol_total = (MRIO.LABOR_BASE['vol_Fem_low'] +
                           MRIO.LABOR_BASE['vol_Male_low'] +
                           MRIO.LABOR_BASE['vol_Fem_high'] +
                           MRIO.LABOR_BASE['vol_Male_high']).sum()
                f.write(f"  Total employment: {vol_total:,.0f}\n")
        else:
            f.write("✗ LABOR_BASE not found in MRIO_BASE\n")
    except Exception as e:
        f.write(f"✗ Error loading: {str(e)}\n")

    f.write("\n" + "="*80 + "\n")
    f.write("CONCLUSION\n")
    f.write("="*80 + "\n")

print(f"Output written to: {output_file}")
