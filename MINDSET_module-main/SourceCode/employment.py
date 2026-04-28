# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 11:36:56 2023

@author: wb582890
"""

import numpy as np

class empl:
    def __init__(self, MRIO_BASE):
        # self.LABOR_BASE = MRIO_BASE.LABOR_BASE
        self.EMPL_COEF = MRIO_BASE.EMPL_COEF
        self.HH_CONS_COU = MRIO_BASE.HH_CONS_COU
        
        self.REGIONS_list = MRIO_BASE.COU_ID
    
    def build_empl_coef(self):
        EMPL_COEF = self.EMPL_COEF.set_index("Unnamed: 0")
        EMPL_COEF = EMPL_COEF.drop(columns=["Unnamed: 1"])

        EMPL_COEF = EMPL_COEF.reset_index()
        EMPL_COEF = EMPL_COEF.rename(columns={"Unnamed: 0": "PROD_COMM"})
        EMPL_COEF = EMPL_COEF.melt(id_vars='PROD_COMM', value_vars=EMPL_COEF.columns[1:])
        EMPL_COEF = EMPL_COEF.rename(columns={"variable": "GLORIA_Country",
                                              "value": "empl_coef"})
        EMPL_COEF = EMPL_COEF.merge((self.HH_CONS_COU.loc[:,['Country_Code','Employment_country']]).rename(columns={'Employment_country':'GLORIA_Country'}), how='left', on=["GLORIA_Country"])
        EMPL_COEF = EMPL_COEF.rename(columns={"Country_Code": "REG_imp"})
        EMPL_COEF = EMPL_COEF.loc[:,["REG_imp","PROD_COMM","empl_coef"]]
        EMPL_COEF = EMPL_COEF[~EMPL_COEF['REG_imp'].isna()].copy()
        EMPL_COEF.sort_values(by="PROD_COMM", inplace=True)
        EMPL_COEF.sort_values(by="REG_imp", kind='stable', key= lambda col: col.map(lambda e: self.REGIONS_list.index(e)), inplace=True)
        
        self.EMPL_COEF = EMPL_COEF
    
    def calc_empl_multiplier(self, empl_base, q_base):
        empl_coef = self.EMPL_COEF.loc[:,"empl_coef"].to_numpy()
        
        # Compute employment effects corresponding to effects on gross output
        self.empl_multiplier = empl_coef * (np.divide(
            empl_base, q_base, out=np.zeros_like(empl_base), where=q_base!=0))
        
        return True
    
    def calc_dempl(self, dq):
        if type(dq) != list:
            dempl = self.empl_multiplier * dq 
            return dempl
        else:
            dempl = {}
            for i in range(len(dq)):
                dempl_i = self.empl_multiplier * dq[i]
                dempl[i] = dempl_i
            return dempl.values()
        
