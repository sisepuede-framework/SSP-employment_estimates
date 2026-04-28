# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 17:35:19 2024

@author: xinru
"""

import os
import glob
import re
import pandas as pd
import numpy as np

def converter():
    # Define the mappings
    sector_ranges = {
        "Agriculture & Forestry": list(range(1, 24)),
        "Energy & Extraction": list(range(24, 41)) + list(range(62, 64))+ list(range(93, 95)),
        "Basic Manufacturing": list(range(41, 57)) + list(range(66, 69)) + list(range(73, 85)),
        "Advanced Manufacturing": list(range(57, 62)) + list(range(64, 66)) + list(range(69, 73)) + list(range(85, 93)) + [97],
        "Public Services": list(range(95, 97)) + list(range(116, 119)),
        "Construction": list(range(98, 100)),
        "Private Services": list(range(100, 116)) + list(range(119, 121))}
   
    # Flatten the detailed sector numbers and sort them
    detailed_sectors = sorted(set([num for nums in sector_ranges.values() for num in nums]))
    # Initialize the matrix with zeros
    matrix = np.zeros((len(sector_ranges), len(detailed_sectors)), dtype=int)
    # Fill the matrix
    for i, (sector, nums) in enumerate(sector_ranges.items()):
        indices = [detailed_sectors.index(num) for num in nums if num in detailed_sectors]
        matrix[i, indices] = 1
    return matrix

# Function to get list of Excel files matching pattern
def find_excel_files(directory, pattern):
    return glob.glob(os.path.join(directory, pattern))

# Function to process data from Excel files
def process_data(files, countries, agg_sector):
    for country in countries:
        list_of_dfs = {}
        for file in files:
            # Extract sheets from Excel file
            excel_file = pd.ExcelFile(file)
            sheets = excel_file.sheet_names
            
            for sheet in sheets:
                if sheet == 'emissions':
                    continue
                
                # Read data from sheet and filter by country
                df = pd.read_excel(file, sheet_name=sheet)
                df_filtered = df[df['Reg_ID'] == country]
                df_filtered = df_filtered.drop(['Unnamed: 0'], axis=1)
                
                # Add a new tab for aggregated sector results for GDP
                if sheet == 'gdp':
                    col = df_filtered.columns
                    df_aggsec = pd.DataFrame(converter().dot(df_filtered),index=agg_sector,columns=col)
                    df_aggsec = df_aggsec.loc[:, 'Sector':'dgdp_total']
                    df_aggsec['Sector'] = agg_sector
                if sheet == 'employment':
                    col = df_filtered.columns
                    df_agg = pd.DataFrame(converter().dot(df_filtered),index=agg_sector,columns=col)
                    df_agg = df_agg.loc[:, 'Sector':'dempl_total']
                    df_agg['Sector'] = agg_sector
                if sheet == 'output':
                    col = df_filtered.columns
                    df_aggoutput = pd.DataFrame(converter().dot(df_filtered),index=agg_sector,columns=col)
                    df_aggoutput = df_aggoutput.loc[:, 'Sector':'dq_total']
                    df_aggoutput['Sector'] = agg_sector

                # Store filtered dataframe
                list_of_dfs[sheet] = df_filtered
            
            list_of_dfs['gdp_agg_sector'] = df_aggsec
            list_of_dfs['emp_agg_sector'] = df_agg
            list_of_dfs['output_agg_sector'] = df_aggoutput
            # Write to Excel file
            output_filename = re.sub(r'FullResults', f'Results', os.path.basename(file))
            output_filename = os.path.join(os.path.dirname(file), output_filename)
            with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
                for sheet_name, df in list_of_dfs.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    

if __name__ == "__main__":
    
    # Specify directory and pattern for Excel files
    
    directory = os.getcwd()  # Current working directory
    pattern = 'FullResults_GEO*.xlsx'
    # pattern = 'FullResults_LAO_Adaptation*.xlsx'
    # Find matching Excel files
    files = find_excel_files(directory, pattern)
    
    # Define countries
    countries = ['GEO']
    
    agg_sector = ['Agriculture & Foresty','Energy & extraction','Basic manufacturing',
              'Advanced Manufacturing','Public services','Construction','Private services']

    # Filter data from FUll to Result
    process_data(files, countries, agg_sector)
    
    
    
    