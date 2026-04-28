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
    """
    
    This class collects all the exogenous variables: elasticity parameters,
    Input-Output and Final Demand information to be passed on to the modules,
    loads the parsed GLORIA IO and final demand raw data.
    
    Input variables:
    - IO_PATH: Location of MRIO dataset and MINDSET code
    - IND_BASE: Inter-industry flow
    - VA_BASE: Value-added (Consumption of Capital and Labor)
    - HH_BASE: Household Final Demand
    - GOV_BASE: Government Final Demand
    - FCF_BASE: Fixed Capital Formation
        
    Output variables:
    - mrio_list: Dataframe of MRIO indices containing regions and sectors
    - mrio_id: Dataframe of MRIO indices containing regions and sectors (ID only)
    - A_id: List of A matrix indices containing regions and sectors (ID only)
    - output: Gross output for each region (REG_imp) and sector (PROD_COMM)
    
    """
    def __init__(self, country, year=2019, IO_PATH = os.getcwd() + "\\", build_LBASE=False,
                 IO_FD_change=None, output_change=None):
        start_time = time.time()
        
        self.IO_PATH = IO_PATH
        self.year = year
        
        var_path = self.IO_PATH + "GLORIA_template\\Variables\\Variable_list_MINDSET.xlsx"
        var_data = pd.read_excel(var_path, "variables")

        path_dict = {key: value for key, value in zip(
            var_data['Variable name (new)'], var_data['Location'])}
        type_dict = {key: value for key, value in zip(
            var_data['Variable name (new)'], var_data['Type'])}
        
        path_dict["SCENARIO"] = path_dict["SCENARIO"][:-15] + country + "_Gloria.xlsx"
        
        if self.year != 2019:
            for key in path_dict.keys():
                if "2019" in path_dict[key]:
                    value = path_dict[key]
                    value = value.replace("2019", str(self.year))
                    path_dict[key] = value
                else:
                    pass
        
        for key in path_dict.keys():
            if key.isupper():
                path_value, type_value = path_dict[key], type_dict[key]
                
                if path_value.endswith('.xlsx'):
                    # Reading Excel files as DataFrame
                    if key == "RE_INVEST_OECD":
                        value = pd.read_excel(self.IO_PATH + path_value, sheet_name="OECD plus China")
                    elif key == "RE_INVEST_ROW":
                        value = pd.read_excel(self.IO_PATH + path_value, sheet_name="ROW")
                    else:
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
                    value = pd.read_csv(self.IO_PATH + path_value, engine="python",
                                        skiprows = [0], encoding='ISO-8859-1')
                try:
                    setattr(self, key, value)
                    del key, value
                except NameError:
                    if ((key != "L_BASE") & (key != "Y_BASE")):
                        print(f"{key} file is not found.")
                    else:
                        pass
            
        if build_LBASE==True:
            del self.L_BASE
        
        self.scenario_path = self.IO_PATH + path_dict["SCENARIO"]
        
        self.FD_BASE = pd.concat([self.HH_BASE, self.GOV_BASE, self.FCF_BASE], axis=1)
        self.FD_BASE["FD"] = self.FD_BASE.sum(axis=1)
        self.FD_BASE = self.FD_BASE[["FD"]]
        
        FD_BASE_TOTAL = self.FD_BASE.groupby(["REG_imp","TRAD_COMM"]).sum()
        FD_BASE_TOTAL.columns = ["FD_total"]
        self.FD_BASE = self.FD_BASE.merge(FD_BASE_TOTAL, left_index=True, right_index=True)
        
        reg_id = pd.DataFrame([e for e in self.COU_ID for i in range(len(self.SEC_ID))])
        region = pd.DataFrame([e for e in self.COU_NAME for i in range(len(self.SEC_NAME))])
        sec_id = pd.DataFrame(list(self.SEC_ID) * len(self.COU_ID))
        sector = pd.DataFrame(list(self.SEC_NAME) * len(self.COU_ID))

        mrio_list = pd.concat([reg_id, region, sec_id, sector], axis=1)
        mrio_list.columns = ["Reg_ID", "Region", "Sec_ID", "Sector"]
        
        self.mrio_list = mrio_list

        mrio_id = pd.concat([reg_id, sec_id], axis=1)
        mrio_id.columns = ["REG_imp", "PROD_COMM"]
        
        self.mrio_id = mrio_id

        self.A_id = [(a,b) for a,b in zip(
            self.mrio_id["REG_imp"], self.mrio_id["PROD_COMM"])]

        if type(IO_FD_change) == dict:
            ind_change = IO_FD_change["ind_trade_rel"]
            # hh_change = IO_FD_change["hh_rel"]
            
            self.IND_BASE = self.IND_BASE.merge(
                ind_change, how="left", left_index=True, right_index=True)
            # self.HH_BASE =  self.HH_BASE.merge(
            #     hh_change, how="left", left_index=True, right_index=True)
            
            # self.IND_BASE["a_bp_ori"] = self.IND_BASE["a_bp"].copy()
            # self.HH_BASE["VIPA_ori"] = self.HH_BASE["VIPA_ori"].copy()
            
            self.IND_BASE["a_bp"] = self.IND_BASE["a_bp"] * self.IND_BASE["IO_coef_rel"]
            # self.HH_BASE["VIPA"] = self.HH_BASE["VIPA"] * self.HH_BASE["hh_rel"]
            
            self.IND_BASE = self.IND_BASE.drop(columns=["IO_coef_rel"])
            # self.HH_BASE = self.HH_BASE.drop(columns=["dHH_rel"])
            
            self.IND_BASE["a_tech"] = self.IND_BASE.groupby(
                ["REG_imp","PROD_COMM","TRAD_COMM"])["a_bp"].transform('sum')
            
            # GOV_recyc = IO_FD_change["GOV_recyc"]
            # INV_induced = IO_FD_change["INV_induced"]
            # INV_recyc = IO_FD_change["INV_recyc"]
        else:
            pass
                                   
        if type(output_change) == pd.DataFrame:
            output_change = output_change.set_index(["REG_imp", "PROD_COMM"])
            output_change["dq_rel"] = output_change["dq_total"] / output_change["q_base"]
            
            output_change["dq_rel"] = output_change["dq_rel"].fillna(0)
            
            output_change = output_change[["dq_rel"]]
            
            self.IND_BASE = self.IND_BASE.merge(
                output_change, how="left", left_index=True, right_index=True)
            # self.IND_BASE["output_ori"] = self.IND_BASE["output"].copy()
            
            self.IND_BASE["output"] = self.IND_BASE["output"] * (1 + self.IND_BASE["dq_rel"])
            self.IND_BASE = self.IND_BASE.drop(columns=["dq_rel"])
            
            self.IND_BASE["z_bp"] = self.IND_BASE["a_bp"] * self.IND_BASE["output"]
        else:
            pass
            # output_change = output_change
            
        output = self.IND_BASE["output"]
        output = output.reset_index()
        output = output.drop(columns=["REG_exp","TRAD_COMM"])
        output = output.drop_duplicates()
        
        self.output = output
        
        print(f"--- Collected exogenous variables: {round(time.time() - start_time, 1)} s ---")
        
    def scenario_file(self):
        return self.scenario_path
    
