# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 15:51:43 2023

@author: meime
"""

import numpy as np
import pandas as pd
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df

class invest:
    """
    InvestmentModel class processes investment data.

    Inputs:
    - IO_Data: Path to the input-output data folder
    - countries: DataFrame containing country information

    Output:
    - inv_output: DataFrame containing investment output data
    - inv_conv: DataFrame containing investment conversion data
    - y_fcf_prop: DataFrame containing investment-propensity-adjusted input-output data
    """

    def __init__(self, exog_vars, INV_CONV, scenario):
        self.IO_PATH = exog_vars.IO_PATH
        self.HH_CONS_COU = exog_vars.HH_CONS_COU
        
        self.FCF = exog_vars.FCF_BASE
        self.INV_OUTPUT_ELAS = exog_vars.INV_OUTPUT_ELAS

        self.REGIONS = exog_vars.R
        self.REGIONS_list = exog_vars.COU_ID

        self.MULTIYEAR = exog_vars.MULTIYEAR

        # this is now by country such as
        # REG_imp | PROD_COMM | TRAD_COMM | input_coeff
        # columns wise == 1; ie groupby(REG_imp.PROD_COMM) sum should be 1.0
        self.INV_CONV = INV_CONV
        
        self.output = exog_vars.output
        
        self.inv_spending = scenario.inv_spending
        
    def build_inv_output_elas(self):
        INV_OUTPUT_ELAS = self.INV_OUTPUT_ELAS.set_index("Unnamed: 0")
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.drop(columns=["Unnamed: 1"])
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.transpose()
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.reset_index()
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.melt(id_vars='index',
                                               value_vars=INV_OUTPUT_ELAS.columns[1:])
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.rename(
            columns={"index": "GLORIA_Country", "Unnamed: 0": "PROD_COMM", "value": "inv_output"})
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.merge((self.HH_CONS_COU.loc[:,['Country_Code','Investment_country']]).rename(columns={'Investment_country':'GLORIA_Country'}), how='left', on=["GLORIA_Country"])
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.rename(columns={"Country_Code": "REG_imp"})
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS.loc[:,["REG_imp","PROD_COMM","inv_output"]]
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS[~INV_OUTPUT_ELAS['REG_imp'].isna()].copy()
        # Filter to only regions in REGIONS_list before sorting
        INV_OUTPUT_ELAS = INV_OUTPUT_ELAS[INV_OUTPUT_ELAS['REG_imp'].isin(self.REGIONS_list)].copy()
        INV_OUTPUT_ELAS.sort_values(by="REG_imp", key= lambda col: col.map(lambda e: self.REGIONS_list.index(e)), inplace=True)
        
        self.INV_OUTPUT_ELAS = INV_OUTPUT_ELAS
        
        return self.INV_OUTPUT_ELAS
    
    def adjust_INV_CONV_AGRI(self):        
        # REG_imp | PROD_COMM | TRAD_COMM | input_coeff
        # columns wise == 1; ie groupby(REG_imp.PROD_COMM) sum should be 1.0
        agri_output = self.output[self.output['PROD_COMM'].isin(np.arange(1,24).tolist())].copy()
        
        # calculate output shares
        agri_output['share'] = agri_output['output'] / agri_output.groupby(['REG_imp',"PROD_COMM"])["output"].transform('sum')

        # assign to investment shares
        agri_output = agri_output.astype({'PROD_COMM':'str'})
        INV_CONV = self.INV_CONV.merge(agri_output.rename(columns={'PROD_COMM':'TRAD_COMM'}),
                                        how='left', on=['REG_imp','TRAD_COMM'])
        
        sel = INV_CONV['share'].isna()
        # treat agri sectors
        INV_CONV.loc[~sel, 'input_coeff'] = INV_CONV[~sel]['share'] * INV_CONV[~sel].groupby(['REG_imp','PROD_COMM'])['input_coeff'].transform('sum')

        INV_CONV = INV_CONV.drop(columns=['share', 'output'])

        self.INV_CONV = INV_CONV
        
    def calc_inv_share(self):
        FCF = self.FCF.reset_index(drop=False)

        y_fcf_wide = FCF.loc[:,["REG_exp","TRAD_COMM","REG_imp","VDFA"]]
        y_fcf_wide["EXP_SEC"] = list(zip(y_fcf_wide["REG_exp"], y_fcf_wide["TRAD_COMM"]))
        y_fcf_wide = y_fcf_wide.loc[:,["EXP_SEC","REG_imp","VDFA"]]
        y_fcf_wide = y_fcf_wide.pivot(index="EXP_SEC", columns="REG_imp", values="VDFA")

        fcf_share = y_fcf_wide.reset_index().melt(
            id_vars='EXP_SEC', value_vars=y_fcf_wide.columns)
        fcf_share[["REG_exp", "TRAD_COMM"]] = pd.DataFrame(fcf_share["EXP_SEC"].tolist())
        fcf_share = fcf_share.rename(columns={"value":"FCF"})
        fcf_share = fcf_share.loc[:,["REG_exp","TRAD_COMM","REG_imp","FCF"]]
        fcf_share = fcf_share.dropna()

        fcf_total = fcf_share.groupby(["TRAD_COMM","REG_imp"])["FCF"].sum()
        fcf_total = fcf_total.to_frame()
        fcf_total = fcf_total.rename(columns={"FCF": "FCF_total"})

        fcf_share = fcf_share.merge(fcf_total, how="left", on=["TRAD_COMM","REG_imp"])
        fcf_share["FCF_share"] = fcf_share["FCF"] / fcf_share["FCF_total"]
        
        self.fcf_share = fcf_share

        # ? fcf_share has dimensions of: | TRAD_COMM | REG_imp | FCF_share (value)
        # ? FCF_share is FCF/FCF_total
        # ? FCF_total is FCF aggregated with groupby(TRAD_COMM, REG_imp), meaning
        # ? summed across REG_exp and PROD_COMM
        # ? so FCF_total captures investment goods of a certain type (TRAD_COMM)
        # ? being demanded in an economy (REG_imp), disregarding geo origin (REG_exp)
        # ? (not there is no PROD_COMM in FD)
        # ? this means that FCF_shares tells us how much belongs to a certain
        # ? REG_exp from what is demanded in a REG_impXTRAD_COMM
        
    def calc_dy_inv_induced(self, IO_model, others):
        # import pdb; pdb.set_trace()
        dq_hh_inc = IO_model.dq_hh_inc
        dq_hh_price = IO_model.dq_hh_price
        dq_gov_recyc = IO_model.dq_gov_recyc
        dq_trade_eff = IO_model.dq_trade
        dq_tech_eff = IO_model.dq_energy
        dq_supply_constraint = IO_model.dq_supply_constraint
        dq_inv_exog = IO_model.dq_inv_exog
        dq_inv_recyc = IO_model.dq_inv_recyc
        
        if self.MULTIYEAR:
            # this is lagged here
            dq_inv_induced = IO_model.dq_inv_induced
        else:
            dq_inv_induced = np.zeros_like(dq_hh_inc)

        dq_others = sum(others)
        # gov_recyc was there twice
        dq_total = dq_hh_inc + dq_hh_price + dq_gov_recyc + dq_trade_eff + dq_tech_eff + dq_supply_constraint + dq_others + dq_inv_exog + dq_inv_induced # + dq_gov_recyc 

        # ? dq_total structure: target-country target-country-iso3 target-sector dq_total
        dq_total = MRIO_vec_to_df(dq_total, 'dq_total', self.REGIONS)
        dq_total = dq_total.rename(columns={'target-country-iso3':'REG_imp','target-sector':'PROD_COMM'})
        dq_total = dq_total[['REG_imp','PROD_COMM','dq_total']]
        
        # bring in output to investment elasticity
        # basically output delta (dq) creates new investment
        # ? INV_OUTPUT_ELAS structure is: REG_imp | PROD_COMM | inv_output
        y_fcf_prop = dq_total.merge(self.INV_OUTPUT_ELAS, how='left', on=['REG_imp','PROD_COMM'])
        y_fcf_prop['dy'] = y_fcf_prop['dq_total'] * y_fcf_prop['inv_output']
        # at this point dy is dy GENERATED BY THAT SECTOR [PROD_COMM] towards investment goods

        del dq_total

        # ? y_fcf_prop is demand for investment goods
        # ? new INV_CONV is: REG_imp | PROD_COMM | TRAD_COMM | input_coeff
        y_fcf_prop = y_fcf_prop.merge(self.INV_CONV.astype({'PROD_COMM':'int16','TRAD_COMM':'int16'}), how='left', on=['REG_imp','PROD_COMM'])
        y_fcf_prop = y_fcf_prop.fillna(0)
        
        dy_fcf_prd = y_fcf_prop.copy()
        del y_fcf_prop
        dy_fcf_prd['dy'] = dy_fcf_prd['dy'] * dy_fcf_prd['input_coeff']
        # dy now is DEMAND FOR INVESTMENT GOOD in sector [TRAD_COMM] from PROD_COMM
        # ? dy_fcf_prd: REG_imp | PROD_COMM | TRAD_COMM | input_coeff | dy
        # ? we still need to allocate to REG_exp by fcf_share
        
        # ? fcf_share is merged on dy_fcf_prd, on TRAD_COMM and REG_imp
        # ? fcf_share tells us the share of a single REG_exp in a
        # ? REG_impXTRAD_COMM pair, so with this we re-allocate
        # ? investment goods to the original trade structure
        FCF_ind = self.fcf_share.merge(dy_fcf_prd, how="left",
                                      on=["TRAD_COMM","REG_imp"])
        FCF_ind["dy"] = FCF_ind["FCF_share"] * FCF_ind["dy"]
        FCF_ind = FCF_ind.groupby(['REG_exp','TRAD_COMM','REG_imp']).agg({'dy':'sum'}).reset_index()
        
        self.dy_inv_induced = FCF_ind.fillna(0)

    def calc_dy_inv_recyc(self, recyc_rev):
        recyc_inv = recyc_rev.loc[:,"recyc_inv"]
        
        if len(recyc_inv) > 0:
            # iii) Compute changes in Government Spending
            recyc_inv = self.inv_spending[['REG_imp','PROD_COMM','inv_spend']].merge(recyc_inv, how='left', on=["REG_imp"])
            recyc_inv["dk"] = recyc_inv["inv_spend"] * recyc_inv["recyc_inv"]

            # self.INV_CONV is 120x120
            # sum(column) = 1
            # REG_imp | PROD_COMM | TRAD_COMM | input_coeff
            inv_conv = self.INV_CONV
            inv_conv = inv_conv.astype({'PROD_COMM':'int16'})
            
            recyc_inv = recyc_inv.merge(inv_conv, how='left', on=['PROD_COMM','REG_imp'])
            recyc_inv['dk'] = recyc_inv['dk'] * recyc_inv['input_coeff']
            # ? this leads to
            # ? REG_imp | PROD_COMM | investment_good | dk | input_coef
            recyc_inv = recyc_inv.drop(columns=['input_coeff'])
            recyc_inv = recyc_inv[~recyc_inv['TRAD_COMM'].isna()]

            # ? disaggregate across export partners (incl. domestic)
            fcf_share = self.fcf_share.astype({'TRAD_COMM':'str'})[['REG_exp','TRAD_COMM','REG_imp','FCF_share']]
            recyc_inv = recyc_inv.astype({'TRAD_COMM':'int'}).astype({'TRAD_COMM':'str'})
            recyc_inv = recyc_inv.merge(fcf_share, how='inner', on=['TRAD_COMM','REG_imp'])
            # ? REG_imp | REG_exp | PROD_COMM | investment_good | dk | FCF_share
            recyc_inv['dy'] = recyc_inv['dk'] * recyc_inv['FCF_share']
            recyc_inv = recyc_inv.drop(columns=['FCF_share','dk']).fillna(0)

            # ? discard REG_imp and PROD_COMM, i.e. where and which industry invests
            recyc_inv = recyc_inv.groupby(['REG_exp','TRAD_COMM']).agg({'dy':'sum'}).reset_index()
            recyc_inv = recyc_inv.rename(columns={'REG_exp':'REG_imp'})
            
            self.dy_inv_recyc = recyc_inv
        
        else:
            self.dy_inv_recyc = pd.DataFrame(columns=['REG_imp','TRAD_COMM','dy'])
            
    def calc_dy_inv_exog(self, exog_inv:pd.DataFrame):
        # ? exog_inv has dimensions of
        # ? REG_imp | PROD_COMM | dk
        exog_inv = exog_inv.loc[:,["REG_imp","PROD_COMM","dk"]]
        exog_inv["PROD_COMM"] = exog_inv['PROD_COMM'].astype(float).astype(int).astype(str)

        if len(exog_inv) > 0:
            # self.INV_CONV is 120x120
            # sum(column) = 1
            inv_conv = self.INV_CONV

            # ! PROD_COMM -> investment by
            # ! TRAD_COMM -> investment goods sector

            exog_inv = exog_inv.merge(inv_conv, how='left', on=['PROD_COMM','REG_imp'])
            exog_inv['dk'] = exog_inv['dk'] * exog_inv['input_coeff']
            # ? this leads to
            # ? REG_imp | PROD_COMM | investment_good | dk | input_coef
            exog_inv = exog_inv.drop(columns=['input_coeff'])

            # ? disaggregate across export partners (incl. domestic)
            fcf_share = self.fcf_share.astype({'TRAD_COMM':'str'})[['REG_exp','TRAD_COMM','REG_imp','FCF_share']]
            exog_inv = exog_inv.astype({'TRAD_COMM':'str'})
            exog_inv = exog_inv.merge(fcf_share, how='inner', on=['TRAD_COMM','REG_imp'])
            # ? REG_imp | REG_exp | PROD_COMM | investment_good | dk | FCF_share
            exog_inv['dy'] = exog_inv['dk'] * exog_inv['FCF_share']
            exog_inv = exog_inv.drop(columns=['FCF_share','dk']).fillna(0)

            # ? discard REG_imp and PROD_COMM, i.e. where and which industry invests
            exog_inv = exog_inv.groupby(['REG_exp','TRAD_COMM']).agg({'dy':'sum'}).reset_index()
            exog_inv = exog_inv.rename(columns={'REG_exp':'REG_imp'})
            
            self.dy_inv_exog = exog_inv
        
        else:
            self.dy_inv_exog = pd.DataFrame(columns=['REG_imp','TRAD_COMM','dy'])
