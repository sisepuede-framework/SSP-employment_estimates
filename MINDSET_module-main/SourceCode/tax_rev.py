# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 16:16:13 2023

@author: meime
"""

import pandas as pd

eu27_list = ["AUT","BEL","BGR","CZE","CYP","DEU","DNK","ESP","EST","FIN","FRA",
             "GRC","HUN","IRL","ITA","LVA","LTU","LUX","MLT","NLD","POL","PRT",
             "ROU","SVK","SVN","SWE"]

class tax_rev:
    def __init__(self, MRIO_BASE, ind_ener_cou, tax_cou,
                 fuel_sec = [24, 25, 26, 27, 62, 63, 93, 94], bta=0):
        self.ind_ener_cou = ind_ener_cou
        self.ind_ener_cou_base = MRIO_BASE.IND_BASE.loc[ind_ener_cou.index]
        self.hh_ener = MRIO_BASE.HH_BASE.loc[:, :, fuel_sec]
        
        self.ind_ener_cou_idx = self.ind_ener_cou.index
        self.hh_ener_idx = self.hh_ener.index
        self.bta = bta
    
    def calc_tax_rev_base(self, tax_rate):
        tax_rate = tax_rate.reset_index().astype({'PROD_COMM':'int64','TRAD_COMM':'int64'})
        tax_rev_base = self.ind_ener_cou_base.merge(tax_rate, how='left', on=["REG_imp", "PROD_COMM", "TRAD_COMM","REG_exp"])
        # import pdb; pdb.set_trace()
        tax_rev_base["tax_rev_base"] = tax_rev_base["z_bp"] * tax_rev_base["delta_tax"] / 100

        self.tax_rev_base = tax_rev_base.reset_index().set_index(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        self.tax_rev_base = self.tax_rev_base[['tax_rev_base']]
        
        return self.tax_rev_base
    
    def calc_tax_rev(self, tax_rate, ind_ener_cou):
        ind_ener_cou_idx = ind_ener_cou.index
        
        tax_rate = tax_rate.reset_index().astype({'PROD_COMM':'int64','TRAD_COMM':'int64'})
        tax_rev = ind_ener_cou.merge(tax_rate, how='left', on=["REG_imp", "PROD_COMM", "TRAD_COMM","REG_exp"])
        tax_rev["tax_rev"] = tax_rev["z_bp_ener"] * tax_rev["delta_tax"] / 100

        self.tax_rev = tax_rev.reset_index().set_index(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        self.tax_rev = self.tax_rev[['tax_rev']]
        
        return self.tax_rev
    
    def calc_tax_rev_prod_base(self, tax_rev_base):
        tax_rev_prod_base = tax_rev_base.groupby(["REG_imp","PROD_COMM"])["tax_rev_base"].sum()
        tax_rev_prod_base = tax_rev_prod_base.to_frame()
        tax_rev_prod_base = tax_rev_prod_base.rename(
            columns={"tax_rev_base": "tax_rev_prod_base"})

        self.tax_rev_prod_base = tax_rev_prod_base
        
        return self.tax_rev_prod_base
    
    def calc_tax_rev_prod(self, tax_rev):
        tax_rev_prod = tax_rev.groupby(["REG_imp","PROD_COMM"])["tax_rev"].sum()
        tax_rev_prod = tax_rev_prod.to_frame()
        tax_rev_prod = tax_rev_prod.rename(
            columns={"tax_rev": "tax_rev_prod"})
        
        self.tax_rev_prod = tax_rev_prod
        
        return self.tax_rev_prod
    
    def calc_tax_rev_hh_base(self, tax_rate_hh):
        tax_rate_hh = tax_rate_hh.astype({'TRAD_COMM':'str'})
        hh_ener = self.hh_ener.reset_index().astype({'TRAD_COMM':'str'})

        tax_rev_hh_base = hh_ener.merge(tax_rate_hh[tax_rate_hh['PROD_COMM']=='FD_1'].drop(columns=['PROD_COMM']), how='left', on=["REG_imp", "TRAD_COMM", "REG_exp"])
        
        tax_rev_hh_base["tax_rev_hh_base"] = tax_rev_hh_base["VIPA"] * tax_rev_hh_base["delta_tax_hh"] / 100
        
        self.tax_rev_hh_base = tax_rev_hh_base.loc[:,["tax_rev_hh_base"]]
        self.tax_rev_hh_base = self.tax_rev_hh_base.set_index(self.hh_ener_idx)
        
        return self.tax_rev_hh_base
    
    def calc_tax_rev_hh(self, tax_rate_hh, hh_ener=None):
        if type(hh_ener) != pd.DataFrame:
            hh_ener = self.hh_ener
            hh_ener_idx = self.hh_ener_idx
        else:
            hh_ener_idx = hh_ener.index

        tax_rate_hh = tax_rate_hh.astype({'TRAD_COMM':'str'})
        hh_ener = hh_ener.reset_index().astype({'TRAD_COMM':'str'})
            
        tax_rev_hh = hh_ener.merge(tax_rate_hh[tax_rate_hh['PROD_COMM']=='FD_1'].drop(columns=['PROD_COMM']), how='left', on=["REG_imp", "TRAD_COMM", "REG_exp"])
        
        tax_rev_hh["tax_rev_hh"] = tax_rev_hh["VIPA"] * tax_rev_hh["delta_tax_hh"] / 100
        
        self.tax_rev_hh = tax_rev_hh.loc[:,["tax_rev_hh"]]
        self.tax_rev_hh = self.tax_rev_hh.set_index(hh_ener_idx)
        
        return self.tax_rev_hh
    
    def calc_recyc_rev_base(self, tax_rev_prod_base, tax_rev_hh_base, rev_subtract_exp_base, rev_split):
        # tax_rev_prod_base = self.tax_rev_prod_base
        tax_rev_prod_base = tax_rev_prod_base.reset_index(level="PROD_COMM", drop=False)
        
        tax_rev_nat_base = tax_rev_prod_base.groupby(
            ["REG_imp"])["tax_rev_prod_base"].sum().to_frame().rename(
                columns={"tax_rev_prod_base": "tax_rev_nat_base"})
        
        tax_rev_hh_nat_base = tax_rev_hh_base.groupby(
            ["REG_imp"])["tax_rev_hh_base"].sum().to_frame()
        
        rev_subtract_exp_base = rev_subtract_exp_base.reset_index(
            level=["REG_exp","TRAD_COMM"], drop=True)
        rev_subtract_exp_base = rev_subtract_exp_base.reset_index(level="PROD_COMM", drop=False)
        
        rev_subtract_exp_nat_base = rev_subtract_exp_base.groupby(
            ["REG_imp"])["rev_subtract_exp_base"].sum().to_frame().rename(
                columns={"rev_subtract_exp_base": "rev_subtract_exp_nat_base"})

        recyc_rev_base = tax_rev_nat_base.merge(rev_subtract_exp_nat_base, how="left", on=["REG_imp"])
        # recyc_rev_base = tax_rev_nat_base.copy()
        recyc_rev_base = recyc_rev_base.merge(tax_rev_hh_nat_base, how="left", on=["REG_imp"])
        recyc_rev_base = recyc_rev_base.merge(rev_split, how="left", on=["REG_imp"])
        
        recyc_rev_base["net_tax_rev_nat_base"] = (
            recyc_rev_base["tax_rev_nat_base"].fillna(0) + recyc_rev_base["tax_rev_hh_base"].fillna(0) - recyc_rev_base["rev_subtract_exp_nat_base"].fillna(0))

        recyc_rev_base["recyc_govt_base"] = recyc_rev_base["net_tax_rev_nat_base"] * recyc_rev_base["govt_spend"]
        recyc_rev_base["recyc_inc_base"] = recyc_rev_base["net_tax_rev_nat_base"] * recyc_rev_base["inc_tax"]
        recyc_rev_base["recyc_payr_base"] = recyc_rev_base["net_tax_rev_nat_base"] * recyc_rev_base["payr_tax"]
        recyc_rev_base["recyc_inv_base"] = recyc_rev_base["net_tax_rev_nat_base"] * recyc_rev_base["pub_inv"]
        
        recyc_rev_base = recyc_rev_base.set_index(["REG_imp"])
        
        self.recyc_rev_base = recyc_rev_base.loc[
            :, ["recyc_govt_base", "recyc_inc_base", "recyc_payr_base", "recyc_inv_base"]]
        
        return self.recyc_rev_base
        
    def calc_recyc_rev(self, tax_rev_prod, tax_rev_hh, rev_subtract_exp, rev_split):
        # tax_rev_prod = self.tax_rev_prod
        tax_rev_prod = tax_rev_prod.reset_index(level="PROD_COMM", drop=False)
        
        tax_rev_nat = tax_rev_prod.groupby(
            ["REG_imp"])["tax_rev_prod"].sum().to_frame().rename(
                columns={"tax_rev_prod": "tax_rev_nat"})
        
        tax_rev_hh_nat = tax_rev_hh.groupby(
            ["REG_imp"])["tax_rev_hh"].sum().to_frame()
        
        rev_subtract_exp = rev_subtract_exp.reset_index(
            level=["REG_exp","TRAD_COMM"], drop=True)
        rev_subtract_exp = rev_subtract_exp.reset_index(level="PROD_COMM", drop=False)
        
        rev_subtract_exp_nat = rev_subtract_exp.groupby(
            ["REG_imp"])["rev_subtract_exp"].sum().to_frame().rename(
                columns={"rev_subtract_exp": "rev_subtract_exp_nat"})

        recyc_rev = tax_rev_nat.merge(rev_subtract_exp_nat, how="left", on=["REG_imp"])
        # recyc_rev = tax_rev_nat.copy()
        recyc_rev = recyc_rev.merge(tax_rev_hh_nat, how="left", on=["REG_imp"])
        recyc_rev = recyc_rev.merge(rev_split, how="left", on=["REG_imp"])
        
        recyc_rev["net_tax_rev_nat"] = (
            recyc_rev["tax_rev_nat"].fillna(0) + recyc_rev["tax_rev_hh"].fillna(0) - recyc_rev["rev_subtract_exp_nat"].fillna(0))
        
        recyc_rev["recyc_govt"] = recyc_rev["net_tax_rev_nat"] * recyc_rev["govt_spend"]
        recyc_rev["recyc_inc"] = recyc_rev["net_tax_rev_nat"] * recyc_rev["inc_tax"]
        recyc_rev["recyc_payr"] = recyc_rev["net_tax_rev_nat"] * recyc_rev["payr_tax"]
        recyc_rev["recyc_inv"] = recyc_rev["net_tax_rev_nat"] * recyc_rev["pub_inv"]
        
        recyc_rev = recyc_rev.set_index(["REG_imp"])
        
        self.recyc_rev = recyc_rev.loc[
            :, ["recyc_govt", "recyc_inc", "recyc_payr", "recyc_inv"]]
        
        return self.recyc_rev
        
    def calc_tax_iter_cond(self, tax_rev_prod, dtax_rev):
        # Iter_comment:
        # Collect additional labor income
        if type(dtax_rev) != pd.DataFrame:
            dtax_rev = pd.DataFrame(tax_rev_prod["tax_rev_prod"])
            dtax_rev.loc["tax_rev_before"] = 0
        else:
            dtax_rev["tax_rev_before"] = dtax_rev["tax_rev_prod"]
            dtax_rev["tax_rev_prod"] = tax_rev_prod["tax_rev_prod"]
            
        return dtax_rev
    
    def build_tax_rev_result(self, tax_rev_prod, tax_rev_hh):
        tax_rev_hh_final = tax_rev_hh.groupby(["REG_imp"])["tax_rev_hh"].sum().to_frame()
        tax_rev_hh_final["PROD_COMM"] = "finalhhdemand"
        tax_rev_hh_final = tax_rev_hh_final.set_index("PROD_COMM", append=True)
        tax_rev_hh_final.columns = ["tax_rev_prod"]

        tax_revenue = pd.concat([tax_rev_prod, tax_rev_hh_final])
        tax_revenue = tax_revenue.reset_index(drop=False)
        
        return tax_revenue
