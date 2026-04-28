# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 08:41:13 2023

@author: wb582890
"""

import numpy as np
import pandas as pd
import pickle

EB_loc = "C:\\Users\\wb582890\\OneDrive - WBG\\Documents\\IEA Data"

# %% IEA Energy Balance by Country

save_db = 1 # Save parsed dataset (1) or not
year = str(2019)

coal_list = ["ANTCOAL", "COKCOAL", "BITCOAL"]
lignite_list = ["SUBCOAL", "LIGNITE", "PATFUEL", "PEAT", "PEATPROD", "OILSHALE"]
coke_list = ["OVENCOKE", "GASCOKE", "COALTAR", "BKB", "GASWKSGS", "COKEOVGS", 
             "BLFURGS", "OGASES", "PETCOKE"]

oil_list = ["CRUDEOIL", "REFFEEDS", "NONCRUDE"]
ref_oil_list = ["ETHANE", "LPG", "NONBIOGASO", "AVGAS", "JETGAS", "NONBIOJETK", "OTHKERO", 
                "NONBIODIES", "RESFUEL", "NAPHTHA", "WHITESP", "LUBRIC", "BITUMEN", 
                "PARWAX", "ONONSPEC"] # , "BIOGASOL", "BIODIESEL", "BIOJETKERO", "OBIOLIQ"

gas_list = ["NATGAS", "NGL"]
ref_gas_list = ["REFINGAS"] # , "BIOGASES"

IEA_EB = pd.read_csv(f"{EB_loc}\\IEA_EB_{year}.csv")
IEA_Map = pd.read_excel(f"{EB_loc}\\IEA_EB_Mapping.xlsx", "Flow_Mapping")

class Enerbal:
    def __init__(self, IEA_EB):
        self.EB_coa = IEA_EB[IEA_EB["PRODUCT"].isin(coal_list)]
        self.EB_lig = IEA_EB[IEA_EB["PRODUCT"].isin(lignite_list)]
        self.EB_cok = IEA_EB[IEA_EB["PRODUCT"].isin(coke_list)]
        self.EB_oil = IEA_EB[IEA_EB["PRODUCT"].isin(oil_list)]
        self.EB_p_c = IEA_EB[IEA_EB["PRODUCT"].isin(ref_oil_list)]
        self.EB_gas = IEA_EB[IEA_EB["PRODUCT"].isin(gas_list)]
        self.EB_p_g = IEA_EB[IEA_EB["PRODUCT"].isin(ref_gas_list)]

EB = Enerbal(IEA_EB)
country_list = sorted(set(IEA_EB["COUNTRY"]))

del IEA_EB

EB_list = ["EB_coa", "EB_lig", "EB_cok", "EB_oil", "EB_p_c", "EB_gas", "EB_p_g"]

for name in EB_list:
    temp = getattr(EB, name)
    temp = temp.merge(IEA_Map, how="left", on=["FLOW", "Flow"])
    temp = temp.groupby(["COUNTRY", "Country", "AG_ID", "AG_FLOW", "AG_Flow"])["Value"].sum()
    temp = temp.reset_index(drop=False)
    temp = temp[temp["AG_ID"]!=0]
    setattr(EB, name, temp)


IEA_temp_loc = "C:\\Users\\wb582890\\OneDrive - WBG\\Documents\\github\\MINDSET_module\\GLORIA_template\\"

for name in EB_list:
    temp = getattr(EB, name)
    temp.to_pickle(f"{IEA_temp_loc}\\Energy\\{name}.pkl")

if save_db == 1:
    for cou in country_list:
        temp_dict = {}
        for name in EB_list:
            temp = getattr(EB, name)
            temp = temp[temp["COUNTRY"]==cou]
            temp_dict[name] = temp
        with pd.ExcelWriter(f"{EB_loc}\\Country_EB\\IEA_EB_{cou}_{year}.xlsx",
                            engine="xlsxwriter") as ResultsWriter:
            for name in EB_list:
                temp_dict[name].to_excel(ResultsWriter, sheet_name=name)
        
# %% IEA Emissions from Energy Balance by Country

# EF = {"coal": 94.3, "oil": 70.75, "gas": 55.8} # Emissions Factor

db_loc = "C:\\Users\\wb582890\\OneDrive - WBG\\Documents\\github\\MINDSET_module\\"
Country_EF = pd.read_pickle(db_loc + "GLORIA_template\\IEA_elas\\fuel_emf.pkl")
EF_db, EF_map = {}, {0: "EF_coal", 2: "EF_oil", 3: "EF_gas"} # , 1:"EF_lignite", 4:"EF_coke"

for i in [0,2,3]:
    EF_db[EF_map[i]] = np.median(Country_EF[i], axis=1)

# This has the dimension of IEA flows x GLORIA countries in the order of fuels 
GLORIA_db = db_loc + "GLORIA_db\\v56\\2019\\parsed_db\\"

with open(GLORIA_db + "cid.pkl", 'rb') as f:
    cid = pickle.load(f)

with open(GLORIA_db + "cou.pkl", 'rb') as f:
    cou = pickle.load(f)

Reg_ID = pd.DataFrame(np.array([cid, cou]).transpose(), columns=["COUNTRY", "Country"])

EF_db = pd.concat([Reg_ID[["COUNTRY", "Country"]], pd.DataFrame(EF_db)], axis=1)
EF_cou = EF_db

# %% IEA Emissions from Energy Balance by Country

Emissions = pd.DataFrame(
    columns=["COUNTRY", "Energy_coal", "Energy_oil", "Energy_gas"]) #, "Emissions"])

# country_test = ["VNM"]
for cou in country_list:
    energy_dict = {}
    emissions_dict = {}
    for name in EB_list:
        if name == "EB_oil":
            pass
        
        else:
            temp = getattr(EB, name)
            temp = temp[temp["COUNTRY"]==cou]
            # country = temp["Country"].iloc[0]
            if name in ["EB_coa", "EB_lig", "EB_cok"]:
                fuel = "coal"
            elif name == "EB_p_c":
                fuel = "oil"
            else:
                fuel = "gas"
            # ef = EF[fuel]
            
            temp["Fuel"] = fuel
            temp["Energy_cons"] = 0
            
            trans_cond = ((temp["AG_ID"].isin([4,5,8])) & (temp["Value"] <= 0))
            temp['Energy_cons'] = -temp['Value'].where(trans_cond, temp['Energy_cons'])
            
            trans_cond = (temp["AG_ID"].isin(range(11,37)))
            temp['Energy_cons'] = temp['Value'].where(trans_cond, temp['Energy_cons'])
            
            temp['Energy_cons'] = temp['Energy_cons'] / 1000
            # temp["Emissions"] = temp['Energy_cons'] * ef / 1000
            
            energy_dict[(cou, name)] = temp["Energy_cons"].sum()
            # emissions_dict[(cou, name)] = temp["Emissions"].sum()
            
    energy_dict[(cou, "Coal")] = (
        energy_dict[(cou, "EB_coa")] + energy_dict[(cou, "EB_lig")] + energy_dict[(cou, "EB_cok")])
    energy_dict[(cou, "Oil")] = energy_dict[(cou, "EB_p_c")]
    energy_dict[(cou, "Gas")] = energy_dict[(cou, "EB_gas")] + energy_dict[(cou, "EB_p_g")]
    
    # emissions_dict[cou] = sum(emissions_dict.values())
    
    df = pd.DataFrame(
        [[cou, energy_dict[cou, "Coal"], energy_dict[cou, "Oil"], # country, 
         energy_dict[cou, "Gas"]]], # , emissions_dict[cou]]],
        columns=["COUNTRY", "Energy_coal", "Energy_oil", "Energy_gas"]) # "Country", "Emissions"])
    
    Emissions = pd.concat([Emissions, df], axis=0)

# Adjust names manually    
Emissions.loc[Emissions['COUNTRY'] == "MALI", "COUNTRY"] = "MLI"

Emissions = EF_db.merge(Emissions, how="left", on="COUNTRY")

Emissions["Emissions_coal"] = Emissions["Energy_coal"] * Emissions["EF_coal"] / 1e3
Emissions["Emissions_oil"] = Emissions["Energy_oil"] * Emissions["EF_oil"] / 1e3
Emissions["Emissions_gas"] = Emissions["Energy_gas"] * Emissions["EF_gas"] / 1e3

Emissions["Energy_tot"] = Emissions[["Energy_coal", "Energy_oil", "Energy_gas"]].sum(axis=1)
Emissions["Emissions_tot"] = Emissions[["Emissions_coal", "Emissions_oil", "Emissions_gas"]].sum(axis=1)

Energy = Emissions[["COUNTRY", "Country", "Energy_tot", "Energy_coal", "Energy_oil", "Energy_gas"]]
Emissions = Emissions[["COUNTRY", "Country", "Emissions_tot", "Emissions_coal", "Emissions_oil", "Emissions_gas"]]

with pd.ExcelWriter(f"{EB_loc}\\Emissions_summary_{year}.xlsx",
                    engine="xlsxwriter") as ResultsWriter:
    Energy.to_excel(ResultsWriter, sheet_name="Energy")
    Emissions.to_excel(ResultsWriter, sheet_name="Emissions")
    