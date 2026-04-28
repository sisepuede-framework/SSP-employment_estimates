"""
Examine ALL sheets in Investment Scenario - SSP.xlsx template
to understand the intended workflow for Investment by sheet
"""
import pandas as pd
import os

os.chdir("C:\\Users\\festeves\\OneDrive - RAND Corporation\\Courses\\Dissertation\\3rd Paper\\Mindset - WB\\MINDSET_module-main\\MINDSET_module-main")

template = 'GLORIA_template/Scenarios/Investment Scenario - SSP.xlsx'
output_file = 'Claude Code/temp/template_all_sheets.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    xl = pd.ExcelFile(template)

    f.write('='*80 + '\n')
    f.write('Investment Scenario - SSP.xlsx: ALL SHEETS\n')
    f.write('='*80 + '\n\n')

    f.write(f'Total sheets: {len(xl.sheet_names)}\n')
    f.write(f'Sheet names: {xl.sheet_names}\n\n')

    # Focus on Investment-related sheets
    for sheet in ['Overview', 'Investment by', 'Investment converter']:
        if sheet not in xl.sheet_names:
            continue

        f.write('='*80 + '\n')
        f.write(f'SHEET: {sheet}\n')
        f.write('='*80 + '\n\n')

        try:
            # Read without skipping rows to see headers
            df = pd.read_excel(template, sheet_name=sheet, nrows=30)
            f.write(f'Shape: {df.shape}\n')
            f.write(f'Columns: {list(df.columns)}\n\n')
            f.write('First 30 rows:\n')
            f.write(df.to_string() + '\n\n')
        except Exception as e:
            f.write(f'Error reading: {e}\n\n')

print(f'Output written to: {output_file}')
