# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 16:53:55 2023

@author: wb582890
"""

class prod_cost:
    def __init__(self, MRIO_BASE, scenario):
        self.LABOR_BASE = MRIO_BASE.LABOR_BASE
        self.VA_BASE = MRIO_BASE.VA_BASE
        self.output = MRIO_BASE.output
        
        self.payr_tax_split = scenario.payr_tax_split
        self.rev_proportion = scenario.rev_proportion
        
    def prod_cost_impact(self, cost_shock, exog_prod_cost):

        cost_shock_ = cost_shock[~cost_shock['Type'].str.contains("tax")].copy()

        # relative
        # TODO need to implement others + decide to house it here or in the scenario module
        cost_shock_ = cost_shock_[cost_shock_['Type'].str.contains("rel")].copy()

        # ! currently only applies to PROD_COMM + REG_imp, so get rid of other dimensions if there
        # ! are any 
        cost_shock_ = cost_shock_[(cost_shock_['REG_exp'] == 'nan') & (cost_shock_['TRAD_COMM'] == 'nan')].copy()
        cost_shock_ = cost_shock_.groupby(['REG_imp','PROD_COMM']).agg({'Value':'sum'}).reset_index()
        cost_shock_ = cost_shock_.astype({'PROD_COMM':'int16'})

        exog_prod_cost = exog_prod_cost.merge(cost_shock_, how='outer', on=['REG_imp','PROD_COMM'])
        exog_prod_cost['Value'] = exog_prod_cost['Value'].fillna(0)
        exog_prod_cost['prod_cost_rel'] = exog_prod_cost['prod_cost_rel'].fillna(1)
        exog_prod_cost['prod_cost_rel'] = exog_prod_cost['prod_cost_rel'] * (1 + exog_prod_cost['Value'])
        exog_prod_cost = exog_prod_cost.drop(columns=['Value'])
        
        return exog_prod_cost
        
    def calc_wage_share(self):
        wage_share = self.LABOR_BASE.copy()
        
        # Load labor data and compute shares of labor by skill-level in total labor inputs
        wage_share["wage_low"] = wage_share["wage_Fem_low"] * wage_share["vol_Fem_low"] + (
            wage_share["wage_Male_low"] * wage_share["vol_Male_low"])
        wage_share["wage_high"] = wage_share["wage_Fem_high"] * wage_share["vol_Fem_high"] + (
            wage_share["wage_Male_high"] * wage_share["vol_Male_high"])
        wage_share["wage_total"] = wage_share["wage_low"] + wage_share["wage_high"]

        wage_share["wage_share_low"] = wage_share["wage_low"] / wage_share["wage_total"]
        wage_share["wage_share_high"] = 1 - wage_share["wage_share_low"]
        
        self.wage_share = wage_share.loc[:,["REG_imp", "PROD_COMM", "wage_share_low", "wage_share_high"]]
        
        return self.wage_share
        
    def calc_empl_share(self):
        empl_share = self.LABOR_BASE.copy()
        
        empl_share["vol_low"] = empl_share["vol_Fem_low"] + empl_share["vol_Male_low"]
        empl_share["vol_high"] = empl_share["vol_Fem_high"] + empl_share["vol_Male_high"]
        empl_share["vol_total"] = empl_share["vol_low"] + empl_share["vol_high"]

        empl_share["vol_share_low"] = empl_share["vol_low"] / empl_share["vol_total"]
        empl_share["vol_share_high"] = 1 - empl_share["vol_share_low"]
        
        self.empl_base = empl_share.loc[:,["REG_imp","PROD_COMM","vol_total"]]
        
        self.empl_share = empl_share.loc[:,["REG_imp", "PROD_COMM", "vol_share_low", "vol_share_high"]]
        
        return self.empl_share

    def calc_labor_share(self):
        VA = self.VA_BASE.melt(id_vars=["REG_imp", "PROD_COMM"], value_vars=self.VA_BASE.columns[2:])
        VA = VA.rename(columns={"variable": "ENDW_COMM", "value": "EVFA"})
        VA = VA.set_index(["REG_imp", "PROD_COMM"])

        labor_comp = VA[(VA["ENDW_COMM"] == "Compensation of employees")]
        labor_comp = labor_comp.loc[:, ["EVFA"]]

        labor_comp = labor_comp.rename(columns={"EVFA": "labor"})
        self.labor_comp = labor_comp.copy()
        
        labor_share = self.wage_share.merge(
            labor_comp, how='left', on=["REG_imp", "PROD_COMM"])
        
        # Compute changes in cost of production
        labor_share["low_skilled_labor"] = labor_share["wage_share_low"] * labor_share["labor"]
        labor_share["high_skilled_labor"] = labor_share["wage_share_high"] * labor_share["labor"]

        low_skilled_labor_total = labor_share.groupby(["REG_imp"])["low_skilled_labor"].sum()
        low_skilled_labor_total = low_skilled_labor_total.to_frame()
        low_skilled_labor_total = low_skilled_labor_total.rename(
            columns={"low_skilled_labor": "low_skilled_labor_total"})

        high_skilled_labor_total = labor_share.groupby(["REG_imp"])["high_skilled_labor"].sum()
        high_skilled_labor_total = high_skilled_labor_total.to_frame()
        high_skilled_labor_total = high_skilled_labor_total.rename(
            columns={"high_skilled_labor": "high_skilled_labor_total"})
        
        labor_share = labor_share.merge(
            low_skilled_labor_total, how="left", on=["REG_imp"])
        labor_share = labor_share.merge(
            high_skilled_labor_total, how="left", on=["REG_imp"])
        
        labor_share["labor_share_low"] = (
            labor_share["low_skilled_labor"] / labor_share["low_skilled_labor_total"])
        labor_share["labor_share_high"] = (
            labor_share["high_skilled_labor"] / labor_share["high_skilled_labor_total"])
        
        self.labor_share = labor_share
        
        return self.labor_share
    
    def calc_shares(self):
        self.calc_wage_share()
        self.calc_empl_share()
        self.calc_labor_share()
        
        return self.wage_share, self.empl_share, self.labor_share
    
    def calc_prod_cost_base(self, tax_rev_prod_base, recyc_rev_base):
        self.tax_rev_prod_base = tax_rev_prod_base
        
        exog_prod_cost_base = self.tax_rev_prod_base.merge(
            self.labor_share, how='left', on=["REG_imp", "PROD_COMM"])
        exog_prod_cost_base = exog_prod_cost_base.merge(
            self.output, how='left', on=["REG_imp", "PROD_COMM"])
        exog_prod_cost_base = exog_prod_cost_base.merge(
            recyc_rev_base, how='left', on=["REG_imp"])
    
        # Additional code starts here
        if self.rev_proportion["payr_tax"][0] == 1:
            # compute low skilled labor share in country
            exog_prod_cost_base["payr_tax_low"] = exog_prod_cost_base["low_skilled_labor_total"] / (
                exog_prod_cost_base["low_skilled_labor_total"] + exog_prod_cost_base["high_skilled_labor_total"])
            # compute high skilled labor share in country
            exog_prod_cost_base["payr_tax_high"] = 1 - exog_prod_cost_base["payr_tax_low"]
        else:
            exog_prod_cost_base = exog_prod_cost_base.merge(
                self.payr_tax_split, how='left', on=["REG_imp"])

        exog_prod_cost_base["tax_rev_nat_low_base"] = (
            exog_prod_cost_base["recyc_payr_base"] * exog_prod_cost_base["payr_tax_low"])
        exog_prod_cost_base["tax_rev_nat_high_base"] = (
            exog_prod_cost_base["recyc_payr_base"] * exog_prod_cost_base["payr_tax_high"])
        
        exog_prod_cost_base["delta_labor_cost_low_base"] = exog_prod_cost_base["tax_rev_nat_low_base"] * exog_prod_cost_base["labor_share_low"]
        exog_prod_cost_base["delta_labor_cost_high_base"] = exog_prod_cost_base["tax_rev_nat_high_base"] * exog_prod_cost_base["labor_share_high"]
        exog_prod_cost_base["delta_labor_cost_base"] = exog_prod_cost_base["delta_labor_cost_low_base"] + exog_prod_cost_base["delta_labor_cost_high_base"]
        
        exog_prod_cost_base["delta_prod_cost_abs_base"] = exog_prod_cost_base["tax_rev_prod_base"] - exog_prod_cost_base["delta_labor_cost_base"]
        exog_prod_cost_base["prod_cost_rel_base"] = 1 + exog_prod_cost_base["delta_prod_cost_abs_base"] / exog_prod_cost_base["output"]
        
        self.exog_prod_cost_base = exog_prod_cost_base.loc[:,["REG_imp", "PROD_COMM","prod_cost_rel_base"]]
        
        # Return the computed production costs
        return self.exog_prod_cost_base

    def calc_prod_cost(self, tax_rev_prod, recyc_rev):
        self.tax_rev_prod = tax_rev_prod
        
        exog_prod_cost = self.tax_rev_prod.merge(
            self.labor_share, how='left', on=["REG_imp", "PROD_COMM"])
        exog_prod_cost = exog_prod_cost.merge(
            self.output, how='left', on=["REG_imp", "PROD_COMM"])
        exog_prod_cost = exog_prod_cost.merge(recyc_rev, how='left', on=["REG_imp"])
    
        # Additional code starts here
        if self.rev_proportion["payr_tax"][0] == 1:
            # compute low skilled labor share in country
            exog_prod_cost["payr_tax_low"] = exog_prod_cost["low_skilled_labor_total"] / (
                exog_prod_cost["low_skilled_labor_total"] + exog_prod_cost["high_skilled_labor_total"])
            # compute high skilled labor share in country
            exog_prod_cost["payr_tax_high"] = 1 - exog_prod_cost["payr_tax_low"]
        else:
            exog_prod_cost = exog_prod_cost.merge(
                self.payr_tax_split, how='left', on=["REG_imp"])

        exog_prod_cost["tax_rev_nat_low"] = (
            exog_prod_cost["recyc_payr"] * exog_prod_cost["payr_tax_low"])
        exog_prod_cost["tax_rev_nat_high"] = (
            exog_prod_cost["recyc_payr"] * exog_prod_cost["payr_tax_high"])
        
        exog_prod_cost["delta_labor_cost_low"] = exog_prod_cost["tax_rev_nat_low"] * exog_prod_cost["labor_share_low"]
        exog_prod_cost["delta_labor_cost_high"] = exog_prod_cost["tax_rev_nat_high"] * exog_prod_cost["labor_share_high"]
        exog_prod_cost["delta_labor_cost"] = exog_prod_cost["delta_labor_cost_low"] + exog_prod_cost["delta_labor_cost_high"]
        
        # ? MAIN CALCULATION
        exog_prod_cost["delta_prod_cost_abs"] = exog_prod_cost["tax_rev_prod"] - exog_prod_cost["delta_labor_cost"]
        exog_prod_cost["prod_cost_rel"] = 1 + exog_prod_cost["delta_prod_cost_abs"] / exog_prod_cost["output"]

        self.exog_prod_cost = exog_prod_cost.loc[:,["REG_imp", "PROD_COMM","prod_cost_rel"]]
        
        # Return the computed production costs
        return self.exog_prod_cost

