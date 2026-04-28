# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 16:55:53 2023

@author: wb582890
"""

class gov:
    def __init__(self, exog_vars, scenario_data):
        self.GOV = exog_vars.GOV_BASE
        self.R = exog_vars.R
        self.P = exog_vars.P
        self.R_list = exog_vars.R['Region_acronyms'].to_list()
        
        self.rev_proportion = scenario_data.rev_proportion
        self.govt_spending = scenario_data.govt_spending
    
    def calc_trade_share(self):
        GOV = self.GOV.reset_index(drop=False)

        VIGA_prod = GOV.groupby(["REG_imp","TRAD_COMM"])["VIGA"].sum()
        VIGA_prod = VIGA_prod.to_frame()
        VIGA_prod = VIGA_prod.rename(columns={"VIGA": "VIGA_prod"})

        GOV = GOV.merge(VIGA_prod, how='left', on=["REG_imp","TRAD_COMM"])
        GOV["VIGA_tradeshare"] = GOV["VIGA"] / GOV["VIGA_prod"]

        VIGA_total = GOV.groupby(["REG_imp"])["VIGA"].sum()
        VIGA_total = VIGA_total.to_frame()
        VIGA_total = VIGA_total.rename(columns={"VIGA": "VIGA_total"})

        GOV = GOV.merge(VIGA_total, how='left', on=["REG_imp"])
        GOV["VIGA_defaultshare"] = GOV["VIGA"] / GOV["VIGA_total"]
        
        self.GOV = GOV
        
    def calc_gov_demand_change(self, recyc_rev):
        
        govt_spending = self.govt_spending[['REG_imp','TRAD_COMM','govt_spend']].pipe(lambda d: d[(~d['REG_imp'].isna()) & (d['REG_imp'].isin(self.R_list))])
        GOV = govt_spending.merge(recyc_rev["recyc_govt"], how='left', on=['REG_imp'])
        GOV = GOV.merge(self.GOV, how='left', on=['REG_imp','TRAD_COMM']).fillna(0)
        
        # if no GOV consumption towards the sector in GLORIA (i.e. VIGA == 0), then assume
        # 100% domestic production
        GOV.loc[GOV['REG_exp']==0,'VIGA_tradeshare'] = 1.0
        GOV.loc[GOV['REG_exp']==0,'REG_exp'] = GOV.loc[GOV['REG_exp']==0,'REG_imp']

        GOV["delta_y_gov_default"] = GOV["recyc_govt"] * GOV["VIGA_defaultshare"]
        # recyc_govt [this is the amount recycled] x govt_spend [spending share (from total) towards the sector] x VIGA_tradeshare [share of REG_exp in sectoral supply]
        GOV["delta_y_gov_user"] = GOV["recyc_govt"] * GOV["govt_spend"] * GOV["VIGA_tradeshare"]
        
        GOV = GOV.set_index(["REG_imp", "REG_exp", "TRAD_COMM"])
        
        if self.rev_proportion["govt_spending"][0] == 0:
            dGOV = GOV.loc[:, ["delta_y_gov_user"]]
            dGOV = dGOV.rename(columns={"delta_y_gov_user": "delta_y_gov"})
        else:
            dGOV = GOV.loc[:, ["delta_y_gov_default"]]
            dGOV = dGOV.rename(columns={"delta_y_gov_default": "delta_y_gov"})
        
        self.dGOV = dGOV
        
        return self.dGOV

