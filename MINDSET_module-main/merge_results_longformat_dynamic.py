# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import os
import re
from alive_progress import alive_bar

results_path = "C:\\Users\\wb619071\\OneDrive - WBG\\Documents\\MINDSET\\MINDSET\\MINDSET_module\\GLORIA_results"

files = [f for f in os.listdir(results_path) if re.search("^FullResults*.*.xlsx$", f)]

result_dict = {}

with alive_bar(len(files),title="Reading files...") as bar:
    for f in files:
        xl = pd.ExcelFile(results_path + "\\" + f)
        print(results_path + "\\" + f)
        name = f.replace("FullResults_", "").replace(".xlsx", "")
        sheets = xl.sheet_names
        bar()
        
        for s in sheets:
            df = xl.parse(s)
            df['scenario'] = name
            
            if s in result_dict.keys():
                result_dict[s] = pd.concat([result_dict[s], df])
            else:
                result_dict[s] = df

# bar = Bar("Writing sheets...", max=len(result_dict.keys()))

# with pd.ExcelWriter(results_path + '\\all_output.xlsx') as writer:
#     for k in result_dict.keys():
#         bar.next()
#         result_dict[k].to_excel(writer, sheet_name=k)
        
# bar.finish()

merge_on = ['Reg_ID','Sec_ID','scenario','year']

with alive_bar(len(result_dict.keys()), title="Merging tables...") as bar:
    df = None
    for k, v in result_dict.items():
        if k in []:
            pass
        else:
            df_ = v.drop(columns=['Unnamed: 0']).astype({'Sec_ID':'str','Reg_ID':'str'})
            try:
                df_ = df_.drop(columns=['Region','Sector'])
            except KeyError:
                pass
            # df_['year'] = df_['scenario'].str.extract(r'([0-9]{4})')
            df_['scenario'] = df_['scenario'].str.replace('_[0-9]{4}',"", regex=True)
            df = df_ if df is None else df.merge(df_, how='outer', on=merge_on)
            bar()

with alive_bar(monitor=None, stats=None, title="Writing CSV...") as bar:
    df.to_csv(results_path + "\\dynamic_long_form.csv") #type:ignore


        

