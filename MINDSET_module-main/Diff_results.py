# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 18:09:10 2024

@author: xinru
"""

import os
import pandas as pd
import re

def subtract_files(file_pattern1, file_pattern2, subtract_from_first=True):
    # # Find files matching patterns
    files1 = [f for f in os.listdir() if f.startswith(file_pattern1)]    
    files2 = [f for f in os.listdir() if f.startswith(file_pattern2)]
    
    if len(files1) == 0 or len(files2) == 0:
        print(f"Error: {files1} or {files2} not found.")
        return
    
    # Iterate through each pair of files
    for file1, file2 in zip(files1, files2):
        print(f"Processing {file1} and {file2}...")
        
        # Read both Excel files into separate DataFrames
        xls1 = pd.ExcelFile(file1)
        xls2 = pd.ExcelFile(file2)
        
        # Get sheet names (assuming same sheets in both files)
        sheet_names = xls1.sheet_names
        
        df_output = {}
        # Process each sheet
        for sheet_name in sheet_names:
            print(f"   Processing sheet: {sheet_name}")
            
            # Load data from both files for the current sheet
            df1 = pd.read_excel(xls1, sheet_name=sheet_name)
            df2 = pd.read_excel(xls2, sheet_name=sheet_name)
            
            # Determine columns for subtraction
            subtract_from_col = [col for col in df1.columns if col.endswith('_base')]
            if not subtract_from_col:
                subtract_from_col = 'Sector_ID'
            # Perform subtraction
            try:
                df_result = df1.copy()
                df_result.iloc[:, df_result.columns.get_loc(subtract_from_col[0])+1:] -= df2.iloc[:, df2.columns.get_loc(subtract_from_col[0])+1:]
                
            except KeyError:
                print(f"   Skipping sheet '{sheet_name}' as subtraction columns not found.")
                continue
            
            df_output[sheet_name] = df_result
            
            # Write subtracted results to new Excel file
            output_filename = re.sub(r'Results_', f'Results_Diff', os.path.basename(file1))
            output_filename = os.path.join(os.path.dirname(file1), output_filename)
            with pd.ExcelWriter(f'DIFF/{output_filename}') as writer:
                for sheet_name, df in df_output.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"   Subtracted data written to '{output_filename}'")
        print("Processing complete.")
        
if __name__ == "__main__":

    countries = ['MYS']
    scenario = ['NETR', 'ARE']
    year = [2030, 2050]
    
    for cou in countries:
        for scen in scenario:
            for y in year:
                file_pattern1 = f"Results_{cou}_Mitigation_{scen}_{y}"  # Adjust pattern as needed
                file_pattern2 = f"Results_{cou}_Mitigation_BASE_{y}"   # Adjust pattern as needed
                # file_pattern1 = f"Results_{cou}_climate_development_scen_ambition"  # Adjust pattern as needed
                # file_pattern2 = f"Results_{cou}_climate_development_bau"   # Adjust pattern as needed
                # file_pattern1 = f"Results_{cou}_adaptation_{y}_tax"  # Adjust pattern as needed
                # file_pattern2 = f"Results_{cou}_climate_{y}"   # Adjust pattern as needed
                # subtract from first -> pattern1 - pattern2 -> S2-S1
                subtract_files(file_pattern1, file_pattern2, subtract_from_first=True)
