import pandas as pd

var_path = 'GLORIA_template/Variables/Variable_list_MINDSET_SSP.xlsx'
var_data = pd.read_excel(var_path, 'variables')

print("Searching for L_BASE in Variable_list_MINDSET_SSP.xlsx...")
print()

# Check if L_BASE exists
l_base = var_data[var_data['Variable name (new)'] == 'L_BASE']

if len(l_base) > 0:
    print("✓ L_BASE found in configuration:")
    print(f"  Variable: {l_base['Variable name (new)'].values[0]}")
    print(f"  Location: {l_base['Location'].values[0]}")
    print(f"  Type: {l_base['Type'].values[0]}")
    print()
    print(f"Current path: {l_base['Location'].values[0]}")
else:
    print("✗ L_BASE NOT configured in variables sheet")
    print()
    print("All configured variables:")
    print(var_data[['Variable name (new)', 'Location']].head(20))
