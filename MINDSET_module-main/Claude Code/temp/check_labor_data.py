import sys
sys.path.insert(0, '.')
from SourceCode.exog_vars_SSP import exog_vars

MRIO = exog_vars()

output_file = 'Claude Code/temp/labor_data_check.txt'

with open(output_file, 'w') as f:
    f.write('Checking employment data in MRIO_BASE:\n')
    f.write('='*80 + '\n\n')

    if hasattr(MRIO, 'LABOR_BASE'):
        f.write('LABOR_BASE found:\n')
        f.write(f'  Shape: {MRIO.LABOR_BASE.shape}\n')
        f.write(f'  Columns: {list(MRIO.LABOR_BASE.columns)}\n\n')
        f.write('First 10 rows:\n')
        f.write(MRIO.LABOR_BASE.head(10).to_string() + '\n\n')

        # Check if we have employment column
        if 'empl' in MRIO.LABOR_BASE.columns:
            f.write('Employment column found!\n')
            total = MRIO.LABOR_BASE['empl'].sum()
            f.write(f'Total employment: {total:,.0f}\n')
    else:
        f.write('LABOR_BASE not found\n')

    f.write('\n' + '='*80 + '\n')

print(f'Output written to {output_file}')
