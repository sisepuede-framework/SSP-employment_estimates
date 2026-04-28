# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 09:56:54 2023

@author: wb582890
"""

import pandas as pd

class ener_scen:
    def __init__(self, scenariofile):
        self.scenario_data = pd.read_excel(scenariofile, sheet_name="Summary")
        
    def collect_tech_coal(self, scen):
        tech_coal = self.scenario_data.iloc[2:5]
        tech_coal = tech_coal[tech_coal["For 2035"] == scen]
        tech_coal = tech_coal["Unnamed: 1"].values[0]
        return tech_coal
    
    def collect_tech_gas(self, scen):
        tech_gas = self.scenario_data.iloc[7:10]
        tech_gas = tech_gas[tech_gas["For 2035"] == scen]
        tech_gas = tech_gas["Unnamed: 1"].values[0]
        return tech_gas
    
    def collect_ely_price(self, scen):
        ely_price = self.scenario_data.iloc[12:15]
        ely_price = ely_price[ely_price["For 2035"] == scen]
        ely_price = ely_price["Unnamed: 1"].values[0]
        return ely_price
    
    def collect_investment(self, scen):
        investment = self.scenario_data.iloc[17:20]
        investment = investment[investment["For 2035"] == scen]
        investment = investment["Unnamed: 1"].values[0]
        return investment
    
    def collect_data(self, scen):
        tech_coal = self.collect_tech_coal(scen)
        tech_gas = self.collect_tech_gas(scen)
        ely_price = self.collect_ely_price(scen)
        investment = self.collect_investment(scen)
        
        return {"tech_coal": tech_coal, "tech_gas": tech_gas, "ely_price": ely_price, 
                "investment": investment}
    