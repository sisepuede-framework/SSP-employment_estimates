# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 17:11:57 2023

@author: wb582890
"""

import pandas as pd
import time

class trade:
    def __init__(self, exog_vars):
        self.trade_elas = exog_vars.TRADE_ELAS
        self.ind_trade_idx = exog_vars.IND_BASE.index
        
    def build_trade_elas(self):
        trade_elas = self.trade_elas.loc[:,["Code", "Elas"]]
        trade_elas = trade_elas.rename(
            columns={"Code":"PROD_COMM","Elas":"ces_elas"})
        
        self.trade_elas = trade_elas

    def calc_IO_coef(self, ind_ener_glo, dp_pre_trade):
        test_time = time.time()
        
        ind_trade = ind_ener_glo.loc[:,["IO_coef_ener","tech_coef_ener"]]

        ind_trade["trade_share"] = ind_trade["IO_coef_ener"] / ind_trade["tech_coef_ener"]
        ind_trade["trade_share"] = ind_trade["trade_share"].fillna(0)
        ind_trade.loc[ind_trade["trade_share"] < 0, "trade_share"] = 0

        ind_trade = ind_trade.reset_index(drop=False)

        ind_trade["trade_share"] = ind_trade["trade_share"].fillna(0)

        ind_trade = ind_trade.merge(self.trade_elas, how='left', on=["PROD_COMM"])
        ind_trade = ind_trade.merge(dp_pre_trade, how='left', on=["TRAD_COMM","REG_imp","REG_exp"])

        # ind_trade here:
        # 	REG_imp	PROD_COMM	REG_exp	TRAD_COMM	IO_coef_ener	
        # tech_coef_ener	trade_share	ces_elas	delta_p
        # where:
        # ces_elas is EXOG
        # delta_p is NA
        #
        # trade_share is sum=1 with groupby REG_imp PROD_COMM TRAD_COMM across REG_exp
        # trade_share is the share of X REG_exp in TRAD_COMM Y within inputs for Z REG_imp-PROD_COMM pair
        #
        # tech_coef_ener is the SAME with gby REG_imp PROD_COMM TRAD_COMM across REG_exp
        # tech_coef_ener is the share of X TRAD_COMM in Y PROD_COMM disregarding (in REG_imp)
        # disregarding REG_exp

        # import pdb; pdb.set_trace()

        ind_trade["delta_p"] = ind_trade["delta_p"].fillna(0)

        # delta_p_total is a weighted component of overall price

        ind_trade["delta_p_total"] = ind_trade["trade_share"] * (
            1+ind_trade["delta_p"]) ** (1-ind_trade["ces_elas"]/2)
        
        # delta_p_total then is only defined as an overall price for the PROD_COMM-TRAD_COMM-REG_imp
        # flow across all REG_exp; nevertheless, this already tries to capture 
        # demand response to individual prices (thus the ces_elas part)

        ind_trade["delta_p_total"] = ind_trade.groupby(
            ["REG_imp","PROD_COMM","TRAD_COMM"])["delta_p_total"].transform('sum')

        # this then calculates the overall response to the aggregated price change

        ind_trade["delta_p_total"] = ind_trade["delta_p_total"] ** (
            1/(1-ind_trade["ces_elas"]/2))
        
        ind_trade["delta_P"] = (1+ind_trade["delta_p"]) ** (1-ind_trade["ces_elas"]/2)
        #the line below should NOT read 1+ since p_total is at this point already 1+delta p...
        ind_trade["delta_P_total"] = (1+ind_trade["delta_p_total"]) ** (
            ind_trade["ces_elas"]/2-1)
        
        ind_trade["subst_effect"] = (ind_trade["trade_share"] * ind_trade["delta_P"] *
                                     ind_trade["delta_P_total"])

        ind_trade["subst_effect_total"] = ind_trade.groupby(
            ["REG_imp","PROD_COMM","TRAD_COMM"])["subst_effect"].transform('sum')

        ind_trade["trade_share_new"] = (
            ind_trade["subst_effect"] / ind_trade["subst_effect_total"])
        
        ind_trade["IO_coef_trade"] = ind_trade["tech_coef_ener"] * ind_trade["trade_share_new"]
        ind_trade["IO_coef_trade"] = ind_trade["IO_coef_trade"].fillna(0)
        
        ind_trade = pd.DataFrame(ind_trade["IO_coef_trade"])

        self.ind_trade = ind_trade.set_index(self.ind_trade_idx)
        
        print("--- Calculate IO trade: %s s ---" % round(time.time() - test_time, 1))
       
        return self.ind_trade
