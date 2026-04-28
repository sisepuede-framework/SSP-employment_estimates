# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 16:54:26 2023

@author: wb582890
"""

import pandas as pd
import numpy as np
import time

from SourceCode.InputOutput import IO
from SourceCode.scenario import scenario

class household:
    def __init__(self, exog_vars):
        
        self.HH = exog_vars.HH_BASE
        self.HH_OP_ELAS = exog_vars.HH_OP_ELAS
        self.HH_CONS_COU = exog_vars.HH_CONS_COU
        self.HH_CONS_SEC = exog_vars.HH_CONS_SEC
        self.HH_CP_ELAS_LOW = exog_vars.HH_CP_ELAS_LOW
        self.HH_CP_ELAS_MID = exog_vars.HH_CP_ELAS_MID
        self.HH_CP_ELAS_HIGH = exog_vars.HH_CP_ELAS_HIGH
        self.HH_INC_COU_MAP = exog_vars.HH_INC_COU_MAP
        self.HH_INC_ELAS = exog_vars.HH_INC_ELAS

        self.multiyear = exog_vars.MULTIYEAR
        
        self.cons_sec = [
            "Food_beverages_tobacco","Clothing_footwear", "Housing",
            "House_furnishing", "Medical_health", "Transport_communication",
            "Recreation", "Education", "Other"]
        self.COU_ID = exog_vars.COU_ID
    
    def build_hh_elas(self, hh_cp_elas_list = [
            "HH_CP_ELAS_LOW", "HH_CP_ELAS_MID", "HH_CP_ELAS_HIGH"]):
        
        # convert to long form (ela_op=Elasticity: Own price)
        HH_OP_ELAS = self.HH_OP_ELAS.melt(
            id_vars = self.HH_OP_ELAS.columns[0:2], value_vars = self.HH_OP_ELAS.columns[2:])
        HH_OP_ELAS = HH_OP_ELAS.rename(columns={"variable":"USDA_Group", "value":"ela_op"})

        # Merge Data with countries
        HH_OP_ELAS = HH_OP_ELAS.merge(self.HH_CONS_COU.drop(columns=['Employment_country','Investment_country']), how="inner",
                                      on=["USDA_Country"])

        # Merge da with sectors
        HH_OP_ELAS = HH_OP_ELAS.merge(self.HH_CONS_SEC, how="inner", left_on=["USDA_Group"],
                                      right_on=["USDA_description"])
        HH_OP_ELAS = HH_OP_ELAS.drop(columns=["USDA_description"])

        # deletes columns no longer needed
        HH_OP_ELAS = HH_OP_ELAS.drop(columns=["Per_capita_Income"])
        
        self.HH_OP_ELAS = HH_OP_ELAS
        
        # iii) Load and Process Cross-price Elasticities -------------------------------

        # convert to long form (ela_op=Elasticity: Cross price)
        HH_CP_ELAS_LOW = self.HH_CP_ELAS_LOW.melt(
            id_vars="Sector_1", value_vars=self.HH_CP_ELAS_LOW.columns[1:])
        HH_CP_ELAS_LOW = HH_CP_ELAS_LOW.rename(
            columns={"variable":"Sector_2", "value":"ela_cp"})
        
        HH_CP_ELAS_MID = self.HH_CP_ELAS_MID.melt(
            id_vars="Sector_1", value_vars=self.HH_CP_ELAS_MID.columns[1:])
        HH_CP_ELAS_MID = HH_CP_ELAS_MID.rename(
            columns={"variable":"Sector_2", "value":"ela_cp"})
        
        HH_CP_ELAS_HIGH = self.HH_CP_ELAS_HIGH.melt(
            id_vars="Sector_1", value_vars=self.HH_CP_ELAS_HIGH.columns[1:])
        HH_CP_ELAS_HIGH = HH_CP_ELAS_HIGH.rename(
            columns={"variable":"Sector_2", "value":"ela_cp"})
        
        # add column indicating income category
        HH_CP_ELAS_LOW["USDA_inc_cat"] = "Low-income"
        HH_CP_ELAS_MID["USDA_inc_cat"] = "Middle-income"
        HH_CP_ELAS_HIGH["USDA_inc_cat"] = "High-income"

        # combine all income categories in one dataframe
        HH_CP_ELAS = pd.concat([HH_CP_ELAS_LOW, HH_CP_ELAS_MID, HH_CP_ELAS_HIGH])

        # assert elasticities to countries
        HH_CP_ELAS = self.HH_INC_COU_MAP.merge(
            HH_CP_ELAS, how='outer', on=["USDA_inc_cat"])
        HH_CP_ELAS = HH_CP_ELAS.pivot(index=HH_CP_ELAS.columns[:-2], columns="Sector_2",
                                values="ela_cp")
        HH_CP_ELAS = HH_CP_ELAS.reset_index(drop=False)

        self.HH_CP_ELAS = HH_CP_ELAS
        
        # iv) Load and Process Income Elasticities ----------------------------------
        # convert to long form (ela_op=Elasticity: Own price)
        
        HH_INC_ELAS = self.HH_INC_ELAS.melt(
            id_vars = self.HH_INC_ELAS.columns[0:2], value_vars = self.HH_INC_ELAS.columns[2:])
        HH_INC_ELAS = HH_INC_ELAS.rename(columns={"variable":"USDA_Group", "value":"ela_inc"})

        # Merge Data with countries
        HH_INC_ELAS = HH_INC_ELAS.merge(self.HH_CONS_COU.drop(columns=['Employment_country','Investment_country']), how="inner",
                                        on=["USDA_Country"])

        # Merge da with sectors
        HH_INC_ELAS = HH_INC_ELAS.merge(self.HH_CONS_SEC, how="inner", left_on=["USDA_Group"],
                                        right_on=["USDA_description"])
        HH_INC_ELAS = HH_INC_ELAS.drop(columns=["USDA_description"])

        # deletes columns no longer needed
        HH_INC_ELAS = HH_INC_ELAS.drop(columns=["Per_capita_Income"])
        
        self.HH_INC_ELAS = HH_INC_ELAS
        
    def build_hh_price(self, dp_pre_trade, tax_rate_hh):
        # import pdb; pdb.set_trace()

        # import pdb; pdb.set_trace()
        dp_pre_trade = dp_pre_trade.set_index(["REG_imp","TRAD_COMM","REG_exp"])
        
        # import pdb; pdb.set_trace()
        HH_elas = self.HH.reset_index().merge(dp_pre_trade, how='left', on=['REG_imp','REG_exp','TRAD_COMM'])
        HH_elas = HH_elas.astype({'TRAD_COMM':'str'})

        tax_rate_hh = tax_rate_hh[tax_rate_hh['PROD_COMM']=='FD_1'].drop(columns=['PROD_COMM'])
        tax_rate_hh = tax_rate_hh.astype({'TRAD_COMM':'str'})

        HH_elas = HH_elas.merge(tax_rate_hh, how='left', on=['REG_imp','REG_exp','TRAD_COMM'])

        # For energy sectors (where delta_tax_hh is not NA) take tax scenario data
        # rather than IO price model results

        dp_hh = HH_elas[HH_elas["delta_tax_hh"].isna()]
        dp_hh = dp_hh.assign(delta_tax_hh = dp_hh["delta_p"])

        dp_hh_ener = HH_elas.dropna()
        dp_hh_ener = dp_hh_ener.assign(delta_tax_hh = dp_hh_ener["delta_tax_hh"] / 100)
        # import pdb; pdb.set_trace()        

        # calculate VIPA sum for REG_imp x TRAD_COMM 
        VIPA_prod = HH_elas.groupby(["REG_imp","TRAD_COMM"]).agg({'VIPA':'sum'}).reset_index()
        VIPA_prod = VIPA_prod.rename(columns={"VIPA": "VIPA_prod"})

        dp_hh = pd.concat([dp_hh, dp_hh_ener]) 
        # dp_hh = dp_hh.loc[:,["REG_exp","delta_tax_hh"]]
        dp_hh = dp_hh.drop(columns=['delta_p','VIPA'])
        dp_hh = dp_hh.rename(columns={"delta_tax_hh": "delta_p"})
        # dp_hh = dp_hh.reset_index()

        HH_elas = HH_elas.merge(VIPA_prod, how="left", on=['REG_imp','TRAD_COMM'])
        HH_elas = HH_elas.drop(columns=["delta_p", "delta_tax_hh"])
        # HH_elas = HH_elas.reset_index()        

        HH_elas = HH_elas.merge(dp_hh, how="left", on=["REG_imp","TRAD_COMM","REG_exp"])
        HH_elas["delta_p_avg"] = HH_elas["delta_p"] * HH_elas["VIPA"] / HH_elas["VIPA_prod"]

        dp_avg = HH_elas.groupby(["REG_imp","TRAD_COMM"]).agg({"delta_p_avg":'sum'}).reset_index()
        
        # import pdb; pdb.set_trace()
        
        VIPA_prod = VIPA_prod.astype({'TRAD_COMM':'str'})
        dp_avg = dp_avg.astype({'TRAD_COMM':'str'})
        HH_price = VIPA_prod.merge(dp_avg, how="left", on=['REG_imp','TRAD_COMM'])

        # TODO
        # HH_price['delta_p_avg'] = HH_price['delta_p_avg']

        # import pdb; pdb.set_trace()
        
        return HH_price
        
    def calc_hh_demand_change(self, HH_price, recyc_rev, dlabor_inc_nat=None):
        # import pdb; pdb.set_trace()

        HH_price = HH_price.merge(
            self.HH_OP_ELAS, how='left', left_on=["TRAD_COMM","REG_imp"], 
            right_on=["Sector_Code","Country_Code"])
        HH_price = HH_price.drop(columns=["Sector_Code","Country_Code"])
        
        HH_price = HH_price.merge(
            self.HH_CP_ELAS, how='left', left_on=["USDA_Group","REG_imp"],
            right_on=["Sector_1","Country_Code"])
        HH_price = HH_price.drop(columns=["Sector_1","Country_Code"])
        
        HH_price = HH_price.merge(
            self.HH_INC_ELAS, how='left',
            left_on=["TRAD_COMM","REG_imp","USDA_Group","USDA_Country"],
            right_on=["Sector_Code","Country_Code","USDA_Group","USDA_Country"])
        HH_price = HH_price[['REG_imp','TRAD_COMM','VIPA_prod','delta_p_avg','USDA_Group','ela_inc','ela_op'] + self.cons_sec]
        
        if type(dlabor_inc_nat) == pd.DataFrame:
            if sum(recyc_rev["recyc_payr"]) != 0:
                recyc_rev["recyc_inc"] = recyc_rev["recyc_payr"] * 0.5
                
            HH_price = HH_price.merge(dlabor_inc_nat["dlabor"], how='left', on=["REG_imp"])
            HH_price = HH_price.merge(recyc_rev["recyc_inc"], how='left', on=["REG_imp"])
            HH_price = HH_price.fillna(0)
            # ! set how much of income to take into account in multiyear
            if self.multiyear:
                HH_price["recyc_inc"] = HH_price["recyc_inc"] + HH_price["dlabor"] * 1.0
            else:
                HH_price["recyc_inc"] = HH_price["recyc_inc"] + HH_price["dlabor"]
            # import pdb; pdb.set_trace()
            # pd.DataFrame(HH_price[HH_price['REG_imp']=='MNG']).to_csv("int/hh_price_{}.csv".format(time.time()))
            HH_price = HH_price.drop(columns=["dlabor"])
        else:
            if sum(recyc_rev["recyc_payr"]) != 0:
                recyc_rev["recyc_inc"] = recyc_rev["recyc_payr"] * 0.5
                
            HH_price = HH_price.merge(recyc_rev["recyc_inc"], how='left', on=["REG_imp"])

        VIPA_USDA = HH_price.groupby(["REG_imp","USDA_Group"])["VIPA_prod"].sum()
        VIPA_USDA = VIPA_USDA.to_frame()
        VIPA_USDA = VIPA_USDA.rename(columns={"VIPA_prod": "VIPA_USDA"})

        HH_price = HH_price.merge(VIPA_USDA, how="left", on=["REG_imp","USDA_Group"])
        HH_price["delta_p_USDA"] = HH_price["delta_p_avg"] * HH_price["VIPA_prod"] / HH_price["VIPA_USDA"]

        delta_p_USDA = HH_price.groupby(["REG_imp","USDA_Group"])["delta_p_USDA"].sum()
        delta_p_USDA = delta_p_USDA.to_frame()

        HH_price_agg = VIPA_USDA.merge(delta_p_USDA, how="left", on=["REG_imp","USDA_Group"])
        HH_price_agg = HH_price_agg.reset_index(drop=False)

        # ! MEAN because same value for multiple rows (single value / country)
        delta_inc = HH_price.groupby(["REG_imp","USDA_Group"])["recyc_inc"].mean()
        HH_price_agg = HH_price_agg.merge(delta_inc, how="left", on=["REG_imp","USDA_Group"])
        HH_price_agg = HH_price_agg.rename(columns={'recyc_inc':'delta_inc'})
        HH_price_agg["delta_inc"] = HH_price_agg["delta_inc"].fillna(0)
        
        VIPA_nat = HH_price_agg.groupby(["REG_imp"])["VIPA_USDA"].sum()
        VIPA_nat = VIPA_nat.to_frame()
        VIPA_nat = VIPA_nat.rename(columns={"VIPA_USDA": "VIPA_nat"})
        HH_price_agg = HH_price_agg.merge(VIPA_nat, how='left', on=["REG_imp"])
        
        wm = lambda x: np.average(x, weights=HH_price.loc[x.index, "VIPA_prod"])
        ela_inc = HH_price.groupby(["REG_imp","USDA_Group"])["ela_inc"].agg(wm)
        ela_op = HH_price.groupby(["REG_imp","USDA_Group"])["ela_op"].agg(wm)
        
        HH_price_agg = HH_price_agg.merge(ela_inc, how="left", on=["REG_imp","USDA_Group"])
        HH_price_agg = HH_price_agg.merge(ela_op, how="left", on=["REG_imp","USDA_Group"])
        
        HH_price_agg["delta_inc_rel"] = HH_price_agg["delta_inc"] / HH_price_agg["VIPA_nat"]
        HH_price_agg["effect_ela_inc"] = (1 + HH_price_agg["delta_inc_rel"]) ** (HH_price_agg["ela_inc"])
        HH_price_agg["effect_ela_op"] = (1 + HH_price_agg["delta_p_USDA"]) ** (HH_price_agg["ela_op"])
        
        HH_CP_elas_agg = {}
        effect_CP_elas = {}
        
        for col in self.cons_sec:
            # 1) attach the cross-price elasticity for destination group = col
             HH_CP_elas_agg[col] = HH_price.groupby(["REG_imp","USDA_Group"])[col].mean()
             HH_price_agg = HH_price_agg.merge(HH_CP_elas_agg[col], how="left", on=["REG_imp","USDA_Group"])
             # 2) compute pairwise effect for each substituted group g (row's USDA_Group) by country
             HH_price_agg["effect_cp_ela_" + col] = (
                 (1 + HH_price_agg["delta_p_USDA"]) ** (HH_price_agg[col]))
             # 3) ***AVERAGE OVER ALL substitutable GROUPS g*** (unweighted mean) -> one factor per (country, consumption col)
             effect_CP_elas[col] = HH_price_agg.groupby(["REG_imp"])["effect_cp_ela_" + col].mean()
             # 4) shape it back so the averaged factor is tagged to the destination group = col
             effect_CP_elas[col] = effect_CP_elas[col].to_frame()
             effect_CP_elas[col] = effect_CP_elas[col].reset_index()
             effect_CP_elas[col]["USDA_Group"] = col
             effect_CP_elas[col] = effect_CP_elas[col].rename(
                 columns={"effect_cp_ela_" + col: "effect_ela_cp"})
                 
        # import pdb; pdb.set_trace()     
        # Calculate delta_a_tech based on cross elasticies and own price elasticities
        effect_CP_elas = pd.concat(effect_CP_elas.values())
        
        HH_price_agg = HH_price_agg.merge(effect_CP_elas, how='left', on=["REG_imp","USDA_Group"])

        HH_price_agg["effect_ela_price"] = HH_price_agg["effect_ela_op"] * HH_price_agg["effect_ela_cp"]
        HH_price_agg["VIPA_price_effect"] = HH_price_agg["VIPA_USDA"] * HH_price_agg["effect_ela_price"]
        HH_price_agg["VIPA_inc_effect"] = HH_price_agg["VIPA_USDA"] * HH_price_agg["effect_ela_inc"]

        exp_change_inc = HH_price_agg.groupby(["REG_imp"])["VIPA_inc_effect"].sum()
        exp_change_inc = exp_change_inc.to_frame()
        exp_change_inc = exp_change_inc.rename(columns={"VIPA_inc_effect": "exp_change_inc"})

        exp_change_USDA = HH_price_agg.groupby(["REG_imp"])["VIPA_USDA"].sum()
        exp_change_USDA = exp_change_USDA.to_frame()
        exp_change_USDA = exp_change_USDA.rename(columns={"VIPA_USDA": "exp_change_USDA"})

        HH_price_agg = HH_price_agg.merge(exp_change_inc, how='left', on=["REG_imp"])
        HH_price_agg = HH_price_agg.merge(exp_change_USDA, how='left', on=["REG_imp"])

        HH_price_agg["exp_change"] = HH_price_agg["exp_change_inc"] - HH_price_agg["exp_change_USDA"]

        HH_price_agg.loc[HH_price_agg["exp_change"] != 0, "VIPA_inc_effect"] = (
            HH_price_agg["VIPA_USDA"] + (HH_price_agg["VIPA_inc_effect"] - HH_price_agg["VIPA_USDA"]) / 
                HH_price_agg["exp_change"] * HH_price_agg["delta_inc"])
        HH_price_agg.loc[HH_price_agg["exp_change"] == 0, "VIPA_inc_effect"] = (
            HH_price_agg["VIPA_USDA"] * HH_price_agg["effect_ela_inc"])

        HH_price_agg = HH_price_agg.loc[:,["REG_imp","USDA_Group","VIPA_price_effect",
                                         "VIPA_inc_effect","effect_ela_inc","delta_inc"]]

        HH_price = HH_price.merge(HH_price_agg, how='left', on=["REG_imp","USDA_Group"])
        HH_price["VIPA_new_price"] = (
            HH_price["VIPA_price_effect"] * HH_price["VIPA_prod"] / HH_price["VIPA_USDA"])
        HH_price["VIPA_new_inc"] = (
            HH_price["VIPA_inc_effect"] * HH_price["VIPA_prod"] / HH_price["VIPA_USDA"])

        HH_price = HH_price.loc[:,["REG_imp","TRAD_COMM","VIPA_prod","VIPA_new_price","VIPA_new_inc"]]
        HH_price = HH_price.set_index(["REG_imp","TRAD_COMM"])

        # calculation of VIPA after price change
        dHH = self.HH.reset_index("REG_exp", drop=False)
        dHH = dHH.merge(HH_price, how='left', on=["REG_imp","TRAD_COMM"])

        # Compute new demands assuming constant product and origin country structure
        dHH["VIPA_new_price"] = dHH["VIPA_new_price"] * dHH["VIPA"] / dHH["VIPA_prod"]
        dHH["VIPA_new_inc"] = dHH["VIPA_new_inc"] * dHH["VIPA"] / dHH["VIPA_prod"]
        dHH["delta_y_price"] = dHH["VIPA_new_price"] - dHH["VIPA"]
        dHH["delta_y_inc"] = dHH["VIPA_new_inc"] - dHH["VIPA"]
        
        dHH = dHH.set_index('REG_exp', append=True)
        
        dHH = dHH.reorder_levels(['REG_imp', 'REG_exp', 'TRAD_COMM'])
        
        self.dHH_price = dHH.loc[:, ["delta_y_price"]]
        self.dHH_inc = dHH.loc[:, ["delta_y_inc"]]
        
        return self.dHH_price, self.dHH_inc
    
