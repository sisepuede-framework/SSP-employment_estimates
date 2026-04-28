# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:59:53 2023

@author: wb582890
"""

# import numpy as np
import pandas as pd
import scipy.io
import scipy.linalg
import pickle
import os

import time

class exog_vars:
    def __init__(self, IO_PATH = os.getcwd() + "\\"):
        """_This class collects all the exogenous variables: elasticity parameters,
        Input-Output and Final Demand information to be passed on to the modules,
        loads the parsed GLORIA IO and final demand raw data.

        Parameters
        ----------
        IO_PATH : _str_, optional
            _root folder of MINDSET model_, by default current working directory

        """        
        start_time = time.time()
        
        self.IO_PATH = IO_PATH
        self.GLORIAv = 'v57'
        
        var_path = self.IO_PATH + "GLORIA_template\\Variables\\Variable_list_MINDSET.xlsx"
        var_data = pd.read_excel(var_path, "variables")

        path_dict = {key: value for key, value in zip(
            var_data['Variable name (new)'], var_data['Location'])}
        type_dict = {key: value for key, value in zip(
            var_data['Variable name (new)'], var_data['Type'])}
        
        self.R = pd.read_excel(var_path, 'R')
        self.R = self.R.sort_values(by="Lfd_Nr")
        self.P = pd.read_excel(var_path, 'P')
        self.MULTIYEAR = False
        
        for key in path_dict.keys():
            if key.isupper():
                path_value, type_value = path_dict[key], type_dict[key]

                # empty value
                if isinstance(path_value, float):
                    print("WARNING: No input file specified for {}".format(key))
                    pass
                
                elif path_value.endswith('.xlsx'):
                    # Reading Excel files as DataFrame
                    value = pd.read_excel(self.IO_PATH + path_value)
                    
                elif path_value.endswith('.mat'):
                    # Reading mat files as NumPy Matrix
                    try:
                        value = scipy.io.loadmat(self.IO_PATH + path_value)
                    except FileNotFoundError:
                        print(f"{key} file is not found, will be parsed in IO module.")
                                        
                elif (path_value.endswith('.pkl') and type_value == "List"):
                    # Reading pickle files as list
                    with open(self.IO_PATH + path_value, 'rb') as f:
                        value = pickle.load(f)
                    del f
                
                elif (path_value.endswith('.pkl') and type_value == "DataFrame"):
                    # Reading pickle files as DataFrame
                    value = pd.read_pickle(self.IO_PATH + path_value)
                
                elif path_value.endswith('.csv'):
                    # Reading csv files as DataFrame
                    value = pd.read_csv(self.IO_PATH + path_value, engine="python", encoding='ISO-8859-1')

                try:
                    setattr(self, key, value)
                    del key, value
                except NameError:
                    if ((key != "L_BASE") & (key != "Y_BASE")):
                        print(f"{key} file is not found.")
                    else:
                        pass
            
        reg_id = pd.DataFrame([e for e in self.COU_ID for i in range(len(self.SEC_ID))]) #type:ignore
        region = pd.DataFrame([e for e in self.COU_NAME for i in range(len(self.SEC_NAME))]) #type:ignore
        sec_id = pd.DataFrame(list(self.SEC_ID) * len(self.COU_ID)) #type:ignore
        sector = pd.DataFrame(list(self.SEC_NAME) * len(self.COU_ID)) #type:ignore

        mrio_list = pd.concat([reg_id, region, sec_id, sector], axis=1)
        mrio_list.columns = ["Reg_ID", "Region", "Sec_ID", "Sector"]
        
        self.mrio_list = mrio_list

        mrio_id = pd.concat([reg_id, sec_id], axis=1)
        mrio_id.columns = ["REG_imp", "PROD_COMM"]
        
        self.mrio_id = mrio_id

        self.A_id = [(a,b) for a,b in zip(
            self.mrio_id["REG_imp"], self.mrio_id["PROD_COMM"])]
            
        output = self.IND_BASE["output"]
        output = output.reset_index()
        output = output.drop(columns=["REG_exp","TRAD_COMM"])
        output = output.drop_duplicates()
        
        self.output = output
        
        print(f"--- Collected exogenous variables: {round(time.time() - start_time, 1)} s ---")
    
    def pop(self, key):
        self.pop(key, None) #type:ignore
        return True
    
    def set_multiyear(self):
        self.MULTIYEAR = True
        return True
