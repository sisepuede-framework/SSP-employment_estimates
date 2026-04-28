# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 09:59:11 2023

@author: wb582890
"""

import pandas as pd
from SourceCode.utils import MRIO_vec_to_df

class income:
    def __init__(self, MRIO_BASE, Prod_cost):
        self.mrio_id = MRIO_BASE.mrio_id
        self.output_base = MRIO_BASE.output
        self.output_id = MRIO_BASE.output.index

        self.REGIONS = MRIO_BASE.R
        self.REGIONS_list = MRIO_BASE.R['Region_acronyms'].to_list()
        
        self.empl_base = Prod_cost.empl_base
        self.labor_comp = Prod_cost.labor_comp
        
    def calc_output(self, dq_total):
        delta_output = pd.concat([self.mrio_id, pd.DataFrame(
            dq_total, columns=["output_change"])], axis=1)
        
        output = self.output_base.merge(delta_output, how="left",
                                        on=['REG_imp','PROD_COMM'])
        output["output"] = output["output"] + output["output_change"]
        output = output.set_index(['REG_imp','PROD_COMM'])
        
        self.output = output["output"]
        
        return self.output
        
    def collect_ener_flow(self, ind_trade, tax_cou, tax_rate,
                          fuel_sec = [24, 25, 26, 27, 62, 63, 93, 94]):
        
        ener_flow = ind_trade.loc[pd.IndexSlice[:, :, :, fuel_sec], :]
        ener_flow = ener_flow.sort_values(["REG_imp","PROD_COMM","TRAD_COMM","REG_exp"])
        ener_flow_idx = ener_flow.index
        
        ener_flow = ener_flow.merge(self.output, how="left", on=["REG_imp","PROD_COMM"])
        ener_flow["z_bp_ener"] = ener_flow["IO_coef_trade"] * ener_flow["output"]
        ener_flow = ener_flow.set_index(ener_flow_idx)
        
        self.ener_flow = pd.DataFrame(ener_flow["z_bp_ener"])
        
        return self.ener_flow
        
    def collect_ener_flow_hh(self, HH_module, tax_cou, tax_rate_hh,
                             fuel_sec = [24, 25, 26, 27, 62, 63, 93, 94]):
        HH_iter = HH_module.HH.loc[:,:,fuel_sec].merge(
            HH_module.dHH_price, how="left", on=["REG_imp","REG_exp","TRAD_COMM"])
        HH_iter = HH_iter.merge(HH_module.dHH_inc, how="left",
                                on=["REG_imp","REG_exp","TRAD_COMM"])
        HH_iter["VIPA"] = HH_iter["VIPA"] + HH_iter["delta_y_price"] + HH_iter["delta_y_inc"]
        self.HH_iter = HH_iter.loc[:,"VIPA"]
        
        return self.HH_iter
        
    def calc_labor_nat_base(self):
        labor_nat_base = self.labor_comp.groupby(["REG_imp"])["labor"].sum()
        self.labor_nat_base = labor_nat_base
        
        return self.labor_nat_base
    
    def calc_labor_comp_change(self, dempl_total):
        dlabor_sec = self.empl_base.rename(columns={"vol_total":"empl_base"}).reset_index()
        dempl_total_df = MRIO_vec_to_df(dempl_total, 'dempl_total', self.REGIONS).rename(columns={'target-country-iso3':'REG_imp','target-sector':'PROD_COMM'})

        dlabor_sec = dlabor_sec.merge(dempl_total_df, how='left', on=['REG_imp','PROD_COMM'])
        # adding in wages, stored in 'labor' variable
        dlabor_sec = dlabor_sec.merge(self.labor_comp, on=["REG_imp", "PROD_COMM"])
        # dlabor_sec["dlabor"] = (
            # dlabor_sec['dempl_total'] / dlabor_sec['empl_base'] * dlabor_sec['labor'])
        dlabor_sec["dlabor"] = (dlabor_sec["dempl_total"] / dlabor_sec['empl_base']) * dlabor_sec['labor']
        
        self.dlabor_sec = dlabor_sec[["REG_imp","PROD_COMM","dlabor"]]
        # dlabor_sec.loc[dlabor_sec['REG_imp']=='MNG', ["PROD_COMM","dlabor","dempl_total","empl_base","labor"]].to_csv("int/dlabor_sec_{}.csv".format(time.time()))
        
        return self.dlabor_sec
        
    def calc_labor_iter_cond(self, dlabor_sec, dlabor_nat):
        # Iter_comment:
        # Collect additional labor income
        labor_nat = dlabor_sec.groupby(["REG_imp"])["dlabor"].sum()
        
        if type(dlabor_nat) != pd.DataFrame:
            dlabor_nat = pd.DataFrame(labor_nat)
            dlabor_nat.loc[:, "dlabor_before"] = 0
        else:
            dlabor_nat["dlabor_before"] = dlabor_nat["dlabor"]
            dlabor_nat["dlabor"] = labor_nat #["dlabor"]
        # dlabor_nat.to_csv("int/dlabor_nat_{}.csv".format(time.time()))
            
        return dlabor_nat
    