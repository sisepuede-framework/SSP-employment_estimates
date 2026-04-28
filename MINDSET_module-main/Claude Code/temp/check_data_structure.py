import pandas as pd
import os

data_path = r"C:\Users\festeves\OneDrive - RAND Corporation\Courses\Dissertation\3rd Paper\Data"

# Check ATTRIBUTE_STRATEGY.csv structure
print('=== ATTRIBUTE_STRATEGY.csv ===')
df_attr = pd.read_csv(os.path.join(data_path, 'ATTRIBUTE_STRATEGY.csv'))
print('Shape:', df_attr.shape)
print('Columns:', list(df_attr.columns))
print()
print('First 5 rows:')
print(df_attr.head())
print()

# Check crosswalk sheet names
print('=== GLORIA-Eora26 - Crosswalk.xlsx ===')
xls = pd.ExcelFile(os.path.join(data_path, 'GLORIA-Eora26 - Crosswalk.xlsx'))
print('Sheet names:', xls.sheet_names)
print()

# Check ISIC concordance sheet structure
print('=== GLORIA (v60) - ISIC concordance ===')
df_isic = pd.read_excel(os.path.join(data_path, 'GLORIA-Eora26 - Crosswalk.xlsx'),
                         sheet_name='GLORIA (v60) - ISIC concordance')
print('Shape:', df_isic.shape)
print('Columns:', list(df_isic.columns))
print()
print('First 10 rows:')
print(df_isic.head(10))
print()
print('Unique ISIC sectors:', df_isic['ISIC_Section'].unique() if 'ISIC_Section' in df_isic.columns else 'Column not found')
