"""
Compare MINDSET template structure with your Strategy_1004_MEX file
to understand if your file follows MINDSET's expected format
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

print("="*80)
print("COMPARE: MINDSET Template vs Your Strategy File")
print("="*80)
print()

#==============================================================================
# Check MINDSET Template
#==============================================================================
print("1. MINDSET Template (Investment Scenario - SSP.xlsx):")
print("-"*80)

template_file = "GLORIA_template/Scenarios/Investment Scenario - SSP.xlsx"
if os.path.exists(template_file):
    xl = pd.ExcelFile(template_file)
    print(f"Sheets: {xl.sheet_names}")

    if 'Investment by' in xl.sheet_names:
        inv_template = pd.read_excel(template_file, 'Investment by')
        print(f"\n'Investment by' sheet columns:")
        print(f"  {list(inv_template.columns)}")
        print(f"\nFirst 5 rows of template:")
        print(inv_template.head())
else:
    print("Template file not found")

print("\n" + "="*80)
print("2. Your Strategy_1004_MEX.xlsx:")
print("-"*80)

your_file = "GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx"
inv_yours = pd.read_excel(your_file, 'Investment by')
print(f"'Investment by' sheet columns:")
print(f"  {list(inv_yours.columns)}")
print(f"\nFirst 5 rows of your file:")
print(inv_yours.head())

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print()
print("According to MINDSET investment.py line 230-231:")
print("  PROD_COMM = 'Sector investing code' = WHO is investing")
print("  TRAD_COMM = Investment goods = WHAT they purchase")
print()
print("The INV_CONV matrix converts from WHO (sector) to WHAT (products)")
print()
print("Your file puts PRODUCT codes in 'Sector investing code*'")
print("This means INV_CONV tries to convert products-as-sectors,")
print("which produces wrong results.")
print()
print("="*80)
print("QUESTION:")
print("="*80)
print()
print("Does the template show:")
print("A) SECTOR codes in 'Sector investing code*' column?")
print("   → Standard MINDSET usage, needs INV_CONV conversion")
print()
print("B) PRODUCT codes in 'Sector investing code*' column?")
print("   → Non-standard usage, your interpretation")
