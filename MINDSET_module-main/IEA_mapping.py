# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 23:18:06 2023

@author: wb582890
"""

import numpy as np
import pandas as pd
import pickle

class Enerbal:
    def __init__(self, exog_vars):
        IEA_vars_list = ["COU_ID", "COU_NAME", "FUEL_EMF", "EB_COA", "EB_LIG", "EB_COK",
                         "EB_OIL", "EB_P_C", "EB_GAS", "EB_GDT", "IO_IEA_MAPPING", 
                         "IND_BASE", "HH_BASE", "NPISH_BASE", "GOV_BASE", "FCF_BASE"]
        
        for var in IEA_vars_list:
             value = getattr(exog_vars, var).copy()
             setattr(self, var, value)
        
    def calc_ener_mon_flow(self):
        
        self.Reg_ID = pd.DataFrame(np.array([self.COU_ID, self.COU_NAME]).transpose(), 
                                   columns=["COUNTRY", "Country"])
        
        cou_list = self.COU_ID # ["CHN", "USA", "SGP"] # cid
        cou_list = [i for i in cou_list if i not in ["DYE", "SOM", "LAO"]]
        
        self.cou_list = cou_list
        
        Ener_GLORIA_dict = {24: "Coal", 25: "Lignite", 26: "Crude Oil", 27: "Gas", 62: "Coke", 
                            63: "Refined Oil", 93: "Electricity", 94: "Refined Gas"}
        Ener_GLORIA_list = list(Ener_GLORIA_dict.keys())

        Coal_IDs = [24,25,62]
        RefOil_IDs = [63]
        Gas_IDs = [27,94]

        Ener_II = self.IND_BASE.loc[pd.IndexSlice[:,:,:,Ener_GLORIA_list], :]
        Ener_II = Ener_II.groupby(["REG_imp", "PROD_COMM", "TRAD_COMM"])["z_bp"].sum()

        Ener_HH = self.HH_BASE.loc[pd.IndexSlice[:,:,Ener_GLORIA_list], :]
        Ener_HH = Ener_HH.groupby(["REG_imp", "TRAD_COMM"])["VIPA"].sum()
        Ener_NPISH = self.NPISH_BASE.loc[pd.IndexSlice[:,:,Ener_GLORIA_list], :]
        Ener_NPISH = Ener_NPISH.groupby(["REG_imp", "TRAD_COMM"])["NPISH"].sum()
        Ener_GOV = self.GOV_BASE.loc[pd.IndexSlice[:,:,Ener_GLORIA_list], :]
        Ener_GOV = Ener_GOV.groupby(["REG_imp", "TRAD_COMM"])["VIGA"].sum()
        Ener_FCF = self.FCF_BASE.loc[pd.IndexSlice[:,:,Ener_GLORIA_list], :]
        Ener_FCF = Ener_FCF.groupby(["REG_imp", "TRAD_COMM"])["VDFA"].sum()

        Ener_II_cou = pd.DataFrame(Ener_II).loc[self.cou_list]
        Ener_HH_cou = pd.DataFrame(Ener_HH).loc[self.cou_list]
        Ener_NPISH_cou = pd.DataFrame(Ener_NPISH).loc[self.cou_list]
        Ener_GOV_cou = pd.DataFrame(Ener_GOV).loc[self.cou_list]
        Ener_FCF_cou = pd.DataFrame(Ener_FCF).loc[self.cou_list]
        
        Ener_II_cou = Ener_II_cou.reset_index()
        
        Ener_HH_cou = Ener_HH_cou.reset_index()
        Ener_HH_cou["PROD_COMM"] = 121
        Ener_HH_cou = Ener_HH_cou.rename(columns={"VIPA": "z_bp"})
        Ener_HH_cou = Ener_HH_cou[["REG_imp", "PROD_COMM", "TRAD_COMM", "z_bp"]]
        
        Ener_NPISH_cou = Ener_NPISH_cou.reset_index()
        Ener_NPISH_cou["PROD_COMM"] = 122
        Ener_NPISH_cou = Ener_NPISH_cou.rename(columns={"NPISH": "z_bp"})
        Ener_NPISH_cou = Ener_NPISH_cou[["REG_imp", "PROD_COMM", "TRAD_COMM", "z_bp"]]
        
        Ener_GOV_cou = Ener_GOV_cou.reset_index()
        Ener_GOV_cou["PROD_COMM"] = 123
        Ener_GOV_cou = Ener_GOV_cou.rename(columns={"VIGA": "z_bp"})
        Ener_GOV_cou = Ener_GOV_cou[["REG_imp", "PROD_COMM", "TRAD_COMM", "z_bp"]]
        
        Ener_FCF_cou = Ener_FCF_cou.reset_index()
        Ener_FCF_cou["PROD_COMM"] = 124
        Ener_FCF_cou = Ener_FCF_cou.rename(columns={"VDFA": "z_bp"})
        Ener_FCF_cou = Ener_FCF_cou[["REG_imp", "PROD_COMM", "TRAD_COMM", "z_bp"]]
        
        Ener_cou = pd.concat(
            [Ener_II_cou, Ener_HH_cou, Ener_NPISH_cou, Ener_GOV_cou, Ener_FCF_cou])
        Ener_cou = Ener_cou.reset_index(drop=True)
        
        Coal_IDs = [24,25,62]
        RawOil_IDs = [26]
        RefOil_IDs = [63]
        Gas_IDs = [27,94]
        Ely_IDs = [93]
        
        Ener_cou.loc[Ener_cou["TRAD_COMM"].isin(Coal_IDs), "Fuel"] = "Coal"
        Ener_cou.loc[Ener_cou["TRAD_COMM"].isin(RawOil_IDs), "Fuel"] = "RawOil"
        Ener_cou.loc[Ener_cou["TRAD_COMM"].isin(RefOil_IDs), "Fuel"] = "RefOil"
        Ener_cou.loc[Ener_cou["TRAD_COMM"].isin(Gas_IDs), "Fuel"] = "Gas"
        Ener_cou.loc[(Ener_cou["TRAD_COMM"]==27) & (Ener_cou["PROD_COMM"]==94), "z_bp"] = 0
        
        Ener_cou.loc[Ener_cou["TRAD_COMM"].isin(Ely_IDs), "Fuel"] = "Ely"
        
        Ener_cou = Ener_cou.groupby(["REG_imp", "PROD_COMM", "Fuel"])["z_bp"].sum()
        Ener_cou = pd.DataFrame(Ener_cou).reset_index()
        
        self.Ener_cou = Ener_cou
        
    def calc_tax_incidence(self):
        EB_COA = self.EB_COA.rename(columns={"Value": "Ener_coa"})
        EB_LIG = self.EB_LIG.rename(columns={"Value": "Ener_lig"})
        EB_COK = self.EB_COK.rename(columns={"Value": "Ener_cok"})
        
        # EB_OIL = self.EB_OIL.rename(columns={"Value": "Ener_oil"})
        EB_P_C = self.EB_P_C.rename(columns={"Value": "Ener_p_c"})
        
        EB_GAS = self.EB_GAS.rename(columns={"Value": "Ener_gas"})
        EB_GDT = self.EB_GDT.rename(columns={"Value": "Ener_gdt"})
        
        EB_Coal = EB_COA.merge(EB_LIG, on=["COUNTRY", "Country", "AG_ID", "AG_FLOW", "AG_Flow"])
        EB_Coal = EB_Coal.merge(EB_COK, on=["COUNTRY", "Country", "AG_ID", "AG_FLOW", "AG_Flow"])
        EB_Coal["Energy"] = EB_Coal["Ener_coa"] + EB_Coal["Ener_lig"] + EB_Coal["Ener_cok"]
        EB_Coal["FUEL"] = "Coal"
        
        EB_RefOil = EB_P_C.copy()
        EB_RefOil["Energy"] = EB_RefOil["Ener_p_c"]
        EB_RefOil["FUEL"] = "RefOil"
        
        EB_Gas = EB_GAS.merge(EB_GDT, on=["COUNTRY", "Country", "AG_ID", "AG_FLOW", "AG_Flow"])
        EB_Gas["Energy"] = EB_Gas["Ener_gas"] + EB_Gas["Ener_gdt"]
        EB_Gas["FUEL"] = "Gas"
        
        EB_cou = EB_Coal[EB_Coal["COUNTRY"].isin(self.cou_list)][["COUNTRY", "AG_FLOW", "FUEL", "Energy"]]
        EB_cou = pd.concat(
            [EB_cou, EB_RefOil[EB_RefOil["COUNTRY"].isin(self.cou_list)][["COUNTRY", "AG_FLOW", "FUEL", "Energy"]]], axis=0)
        EB_cou = pd.concat(
            [EB_cou, EB_Gas[EB_Gas["COUNTRY"].isin(self.cou_list)][["COUNTRY", "AG_FLOW", "FUEL", "Energy"]]], axis=0)
        
        IEA_GLORIA_map = self.IO_IEA_MAPPING.melt(id_vars=['GLORIA_ID', 'GLORIA_sector'],
                                             var_name='IEA_sector', value_name='Share')

        IEA_GLORIA_map[IEA_GLORIA_map["Share"]==0] = np.nan
        IEA_GLORIA_map = IEA_GLORIA_map.dropna()
        
        EB_cou.loc[EB_cou["AG_FLOW"] == "FISHING", "AG_FLOW"] = "AGRICULT"
        EB_cou = EB_cou.groupby(["COUNTRY", "AG_FLOW", "FUEL"])["Energy"].sum()
        EB_cou = EB_cou.reset_index()

        EB_cou_mapped = EB_cou.merge(IEA_GLORIA_map, how="inner",
                                     left_on=["AG_FLOW"], right_on=["IEA_sector"])
        EB_cou_mapped = EB_cou_mapped.set_index(["COUNTRY", "FUEL", "GLORIA_ID", "IEA_sector"])

        for c in self.cou_list:
            for i in ["Coal", "RefOil", "Gas"]:
                for j in range(1,125):
                    try:
                        temp = EB_cou_mapped.loc[c,i,j,:]
                        if ((len(temp) != 0) & (len(temp[temp["Energy"] == 0]) == 0)):
                            if ((j != 62) & (j != 93)):
                                EB_cou_mapped.loc[c,i,j,["INONSPEC", "TRNONSPE", "ONONSPEC"], "Share"] = np.nan
                    except:
                        pass

        EB_cou_mapped = EB_cou_mapped.reset_index()
        EB_cou_mapped["Energy"] = abs(EB_cou_mapped["Energy"])
        EB_cou_mapped = EB_cou_mapped.dropna()

        Ener_cou_mapped = self.Ener_cou.merge(
            EB_cou_mapped, how="inner", left_on=["REG_imp", "PROD_COMM", "Fuel"],
            right_on=["COUNTRY", "GLORIA_ID", "FUEL"])
        Ener_cou_mapped["Ener_flow"] = Ener_cou_mapped["z_bp"] * Ener_cou_mapped["Share"]
        
        Ener_total = Ener_cou_mapped.groupby(["REG_imp", "IEA_sector", "Fuel"])["Ener_flow"].sum()
        Ener_total = pd.DataFrame(Ener_total).reset_index().rename(columns={"Ener_flow": "Ener_total"})
        
        EF_db, EF_map = {}, {0: "Coal", 2: "RefOil", 3: "Gas"} # , 1:"EF_lignite", 4:"EF_coke"

        for i in [0,2,3]:
            EF_db[EF_map[i]] = np.median(self.FUEL_EMF[i], axis=1)
            
        EF_db = pd.concat([self.Reg_ID[["COUNTRY"]], pd.DataFrame(EF_db)], axis=1)
        EF_db = EF_db
        
        EF_cou = EF_db[EF_db["COUNTRY"].isin(self.cou_list)]
        EF_cou = EF_cou.melt(id_vars=["COUNTRY"], var_name="FUEL", value_name="EF")

        Ener_cou_mapped = Ener_cou_mapped.merge(Ener_total, how="left", on=["REG_imp", "IEA_sector", "Fuel"])
        Ener_cou_mapped = Ener_cou_mapped.merge(EF_cou, how="left", on=["COUNTRY", "FUEL"])
        
        self.Ener_cou_mapped = Ener_cou_mapped
        
        # Energy multiplied by Emissions Factor by tax rate by share for each sector divided by (energy in monetary / 1000) * 100%
        Ener_cou_mapped["Tax_incidence"] = (
            Ener_cou_mapped["Energy"] * Ener_cou_mapped["EF"] * 80 * Ener_cou_mapped["Share"] / Ener_cou_mapped["Ener_total"] / 1000 * 100)
        Ener_cou_mapped = Ener_cou_mapped[["REG_imp", "PROD_COMM", "FUEL", "Tax_incidence"]]
        Ener_cou_mapped = Ener_cou_mapped.groupby(["REG_imp", "PROD_COMM", "FUEL"])["Tax_incidence"].sum()
        
        Ener_cou_coal = Ener_cou_mapped.loc[:,:,"Coal"]
        Ener_cou_oil = Ener_cou_mapped.loc[:,:,"RefOil"]
        Ener_cou_gas = Ener_cou_mapped.loc[:,:,"Gas"]
        
        Ener_cou_coal = Ener_cou_coal.reset_index()
        Ener_cou_oil = Ener_cou_oil.reset_index()
        Ener_cou_gas = Ener_cou_gas.reset_index()        
        
        Tax_incidence_coal = Ener_cou_coal.pivot(
            index='PROD_COMM', columns='REG_imp', values='Tax_incidence')
        Tax_incidence_oil = Ener_cou_oil.pivot(
            index='PROD_COMM', columns='REG_imp', values='Tax_incidence')
        Tax_incidence_gas = Ener_cou_gas.pivot(
            index='PROD_COMM', columns='REG_imp', values='Tax_incidence')
        
        Tax_incidence_24 = Tax_incidence_coal.fillna(0)
        Tax_incidence_25 = Tax_incidence_coal.fillna(0)
        Tax_incidence_27 = Tax_incidence_gas.fillna(0)
        Tax_incidence_62 = Tax_incidence_coal.fillna(0)
        Tax_incidence_63 = Tax_incidence_oil.fillna(0)
        Tax_incidence_94 = Tax_incidence_gas.fillna(0)
        
        try:
            Tax_incidence_27.loc[94] = 0
        except:
            pass
        
        self.Tax_incidence = {24: Tax_incidence_24, 25: Tax_incidence_25,
                              27: Tax_incidence_27, 62: Tax_incidence_62,
                              63: Tax_incidence_63, 94: Tax_incidence_94}
        
iea_enerbal = Enerbal(MRIO_BASE)
iea_enerbal.calc_ener_mon_flow()
iea_enerbal.calc_tax_incidence()
