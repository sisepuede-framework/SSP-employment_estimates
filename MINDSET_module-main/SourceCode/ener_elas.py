# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 14:50:43 2023

@author: wb582890
"""

import numpy as np
import pandas as pd
import time
from SourceCode.utils import resolve_comma

class ener_elas:
    """
    INITIALIZED VARIABLES (EXOGENOUS):
      - Elasticities
        - Own-Price Elasticities (ELAS_OP) "OwnPrices.xlsx"
        - Cross-Price Elasticities (ELAS_CP)
            Merge elasticities data from country specific (".._ByCountry.xlsx"),
            rest of Europe (".._ROE.xlsx"), rest of Asia (".._ROA.xlsx"),
            and rest of world (".._ROW.xlsx").
        
    INPUTS FROM OTHER MODULES:
      - exog_vars Module
        - Call IND_BASE (previously IND_sparse) from exog_vars module
          
      - scenario Module
        - Call tax_rate (previously tax_data) from scenario module

    OUTPUTS:
      - ind_ener (previously a_bp_new in IND_sparse)

    """
    def __init__(self, exog_vars, en_cp_elas_list = [
            "EN_CP_ELAS_COU", "EN_CP_ELAS_ROA", "EN_CP_ELAS_ROE", "EN_CP_ELAS_ROW"]):
        
        self.A_id = exog_vars.A_id
        
        self.COU_ID = exog_vars.COU_ID
        self.EN_OP_ELAS = exog_vars.EN_OP_ELAS
        self.REGIONS = exog_vars.R
        
        # read concordance for world regions to countries
        self.EN_CP_ELAS_CONC = exog_vars.EN_CP_ELAS_CONC
        self.EN_OP_ELAS_CONC = exog_vars.EN_OP_ELAS_CONC

        EN_CP_ELAS = {}
        
        for key in en_cp_elas_list:
             value = getattr(exog_vars, key)
             value = value.rename(columns={"Fuel":"TRAD_COMM", "Country":"REG_imp"})
             EN_CP_ELAS[key] = value
        
        self.EN_CP_ELAS = pd.concat(EN_CP_ELAS)
        
    def build_ener_elas(self):
        
        EN_OP_ELAS = self.EN_OP_ELAS.melt(
            id_vars=["Sector","TRAD_COMM"], value_vars=self.EN_OP_ELAS_CONC['Code'].to_list())
        EN_OP_ELAS = EN_OP_ELAS.rename(
            columns={"variable":"REG_imp", "value":"OP_elas"})
        EN_OP_ELAS = EN_OP_ELAS.set_index(["REG_imp","TRAD_COMM"])
        
        self.EN_OP_ELAS = EN_OP_ELAS

        EN_CP_ELAS = self.EN_CP_ELAS_CONC.merge(
            self.EN_CP_ELAS, how='left', left_on=['Code'], right_on=['REG_imp'])
        EN_CP_ELAS = EN_CP_ELAS.drop(
            columns=["Country Name","Code","Filename","REG_imp"])
        EN_CP_ELAS = EN_CP_ELAS.rename(columns={"Original Code":"REG_imp"})
        EN_CP_ELAS = EN_CP_ELAS.set_index(["REG_imp","TRAD_COMM"])
        EN_CP_ELAS = EN_CP_ELAS.drop(columns="Sector")
        
        self.EN_CP_ELAS = EN_CP_ELAS
        
        # get list of energy sector
        self.energy_list = sorted(set(
            self.EN_OP_ELAS.index.get_level_values("TRAD_COMM")))
    
    def assign_tax_rate(self, IND_BASE, tax_rate):
        tax_cou = list(set(tax_rate['REG_imp'].unique().tolist()))
        if 'ALL' in tax_cou:
            tax_cou = self.COU_ID
        ener_elas = IND_BASE.loc[tax_cou,:].reset_index()
        # ener_elas = ener_elas.reset_index(level="REG_exp", drop=False)
        ener_elas = ener_elas.merge(tax_rate.reset_index().astype({'PROD_COMM':'int64','TRAD_COMM':'int64'}),
                                     how='inner', on=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        
        # ! TEMPORARY SOLUTION
        ener_elas = ener_elas[~ener_elas['TRAD_COMM'].isin([96, 77])]

        # ener_elas = ener_elas.set_index(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        ener_elas["delta_tax"] = ener_elas["delta_tax"] / 100

        # join elasticities and compute changes in intermediate inputs
        # ener_elas = IND_sparse.dropna()

        # * WE NEED TO CALCULATE A WEIGHTED TAX BASED ON THE COMPOSITION OF THE ENERGY SOURCE
        ener_elas['weight'] = ener_elas['z_bp'] / ener_elas.groupby(['REG_imp','PROD_COMM','TRAD_COMM'])['z_bp'].transform('sum')
        ener_elas['weighted_tax'] = ener_elas['delta_tax'] * ener_elas['weight']
        ener_elas['delta_tax'] = ener_elas['weighted_tax']
        ener_elas = ener_elas.groupby(['REG_imp','PROD_COMM','TRAD_COMM']).agg({'delta_tax':'sum','a_bp':'sum'})

        delta_tax = ener_elas["delta_tax"]
        delta_tax = delta_tax[~delta_tax.index.duplicated(keep='first')]
        
        self.delta_tax = delta_tax

        # drop exporter / origin country

        ener_elas = ener_elas.reset_index().groupby(["REG_imp","PROD_COMM","TRAD_COMM"])["a_bp"].sum()
        ener_elas = ener_elas.to_frame()
        ener_elas = ener_elas.rename(columns={"a_bp": "a_tech"})
        ener_elas = ener_elas.merge(self.delta_tax, how='left',
                                    on=["REG_imp", "PROD_COMM", "TRAD_COMM"])
        ener_elas = ener_elas.reset_index(level="PROD_COMM", drop=False)
        ener_elas = ener_elas.join(self.EN_OP_ELAS, how='left')
        ener_elas = ener_elas.drop(columns="Sector")

        ener_elas = ener_elas.join(self.EN_CP_ELAS, how="left")

        # import pdb; pdb.set_trace()
        
        self.ener_elas = ener_elas
        
        # in ener_elas, it contains delta tax, 
    
    def MRIO_vec_to_df(self, vector, name, iso3=False):
        # vector is 19680, 120x164
        vec = pd.DataFrame(vector).reset_index()
        vec.columns = ['index', name]
        vec['target-country'] = (np.floor(vec['index'] / 120)).astype('int16') + 1
        vec['target-sector'] =  (vec['index'] % 120).astype('int16') + 1
        vec[name] = vec[name].astype('float32')
        vec = vec.drop(columns=['index'])
        return vec
    
    def attach_iso3(self, df, regions):
        """ 
        Attaches ISO3 codes from the `regions` input to the dataframe
        `origin-country` and `target-country` have to be present in the dataframe
        """
        regions = regions.drop(columns=['Region_names'])
        regions['Region_acronyms'] = regions['Region_acronyms'].astype('category')
        df = df.merge(regions, how='left', left_on=['target-country'], right_on=['Lfd_Nr']).rename(columns={'Region_acronyms':'target-country-iso3'})\
            .drop(columns=['Lfd_Nr'])
        return df

    def assign_price_change(self, MRIO_BASE, tax_rate, tax_rate_hh, price_change):
        # import pdb; pdb.set_trace()
        ind_base = MRIO_BASE.IND_BASE.reset_index()
        ind_base = ind_base.astype({'PROD_COMM':'str', 'TRAD_COMM':'str'})
        # tax rate
        # REG_imp PROD_COMM TRAD_COMM REG_exp <- all in index, delta_tax is value
        tax_rate_ = tax_rate.copy()
        tax_rate_hh_ = tax_rate_hh.copy()
        # price change
        # 'REG_exp','REG_imp','TRAD_COMM','PROD_COMM','Value','Type'

        # ! bring in FD numbers (for HH for now)
        HH = MRIO_BASE.HH_BASE.reset_index()
        # REG_imp REG_exp TRAD_COMM
        HH['PROD_COMM'] = 'FD_1'
        HH = HH.rename(columns={'VIPA':'z_bp'})
        # REG_imp REG_exp TRAD_COMM PROD_COMM z_bp

        # ! PRICE CHANGE (tax) is Absolute now

        tax_change = price_change[price_change['Type'].str.contains("tax")].copy()
        # ! for testing there is no need for ALL 
        # ! WE HAVE ONLY SINGLE COUNTRY CASE!!!

        tax_change = resolve_comma(tax_change, "TRAD_COMM")
        tax_change = resolve_comma(tax_change, "PROD_COMM")

        # IF VALUE is absolute we need to proportionally scale!
        tax_change_rel = tax_change[~tax_change['Type'].str.contains("abs")].copy().drop(columns=['Type','line'])
        tax_change_abs = tax_change[tax_change['Type'].str.contains("abs")].copy().drop(columns=['Type'])
        
        # we want to proceed by line
        tax_change_abs = tax_change_abs.astype({'PROD_COMM':'str', 'TRAD_COMM':'str'})

        # merge to MRIO
        ind_full = pd.concat([ind_base[['REG_imp','REG_exp','PROD_COMM','TRAD_COMM','z_bp']], HH])
        ind_full = ind_full.astype({'TRAD_COMM':'str'})
        tax_change_abs = tax_change_abs.merge(ind_full, how='left', 
                             on=['REG_imp','REG_exp','PROD_COMM','TRAD_COMM']).fillna(0)
        

        tax_change_abs['line_share'] = tax_change_abs['z_bp'] / tax_change_abs.groupby(['line'])['z_bp'].transform('sum')
        tax_change_abs['line_share'] = tax_change_abs['line_share'].fillna(0)
        tax_change_abs['Value'] = tax_change_abs['line_share'] * tax_change_abs['Value']
        tax_change_abs['Value'] = tax_change_abs['Value'].fillna(0)
        # proceed to calculate relative change
        tax_change_abs['rel_value'] = (tax_change_abs['Value'] / tax_change_abs['z_bp']) * 100
        tax_change_abs = tax_change_abs.groupby(['REG_imp','REG_exp','PROD_COMM','TRAD_COMM']).agg({'rel_value':'sum'})
        tax_change_abs = tax_change_abs.reset_index()
        tax_change_abs = tax_change_abs.rename(columns={'rel_value':'Value'})

        tax_change = pd.concat([tax_change_abs, tax_change_rel])

        # IO from here
        tax_change_ = tax_change[~tax_change['PROD_COMM'].str.contains("FD_")]
        tax_rate_ = tax_rate_.merge(tax_change_, how='outer', on=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        tax_rate_ = tax_rate_.fillna(0)
        tax_rate_['delta_tax'] = tax_rate_['delta_tax'] + tax_rate_['Value']
        tax_rate_ = tax_rate_.drop(columns=['Value'])

        # HH here
        tax_change_ = tax_change[tax_change['PROD_COMM'].str.contains("FD_")]
        tax_rate_hh_ = tax_rate_hh_.merge(tax_change_, how='outer', on=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        tax_rate_hh_ = tax_rate_hh_.fillna(0)
        tax_rate_hh_['delta_tax_hh'] = tax_rate_hh_['delta_tax_hh'] + tax_rate_hh_['Value']
        tax_rate_hh_ = tax_rate_hh_.drop(columns=['Value'])

        return tax_rate_, tax_rate_hh_
        
    def calc_tech_coef_ener(self, fuel_sec = [24, 25, 26, 27, 62, 63, 93, 94]):
        # --- This function calculates technical coefficient based on
        # the energy elasticities and the tax templates
        # Is the MINUS correct here? : check OP_elas inputs
        tech_coef_ener = self.ener_elas.copy()
        tech_coef_ener["delta_tech_coef_OP"] = (
            1 + tech_coef_ener["delta_tax"]) ** -(tech_coef_ener["OP_elas"])        
        
        delta_tech_coef_CP = {}

        for col in fuel_sec:
            #  self.ener_elas.columns here is:
            # ['PROD_COMM', 'a_tech', 'delta_tax', 'OP_elas', 24, 25, 26, 27, 62, 63, 93, 94]
            # fuel_sec (as defined above are all fuel sectors)
             if col in self.ener_elas.columns:
                 tech_coef_ener["delta_tech_coef_CP_" + str(col)] = (
                     1 + tech_coef_ener["delta_tax"]) ** (tech_coef_ener[col])
                 
                #  tech_coef_ener here is the cross-price elasticity [columns] for the product in the row
                 tech_coef_ener = tech_coef_ener.drop(columns=col)

                 delta_tech_coef_CP[col] = tech_coef_ener.groupby(
                     ["REG_imp","PROD_COMM"])["delta_tech_coef_CP_" + str(col)].mean()
                 delta_tech_coef_CP[col] = delta_tech_coef_CP[col].to_frame()
                 delta_tech_coef_CP[col] = delta_tech_coef_CP[col].rename(
                     columns={"delta_tech_coef_CP_" + str(col) : "delta_tech_coef_CP"})
                 delta_tech_coef_CP[col]["TRAD_COMM"] = col
                 delta_tech_coef_CP[col] = delta_tech_coef_CP[col].reset_index()

        # Calculate delta_a_tech based on cross elasticies and own price elasticities
        delta_tech_coef_CP = pd.concat(delta_tech_coef_CP.values())
        delta_tech_coef_CP = delta_tech_coef_CP.set_index(["REG_imp","PROD_COMM","TRAD_COMM"])
        delta_tech_coef_CP = delta_tech_coef_CP.fillna(1)

        tech_coef_ener = tech_coef_ener.reset_index()
        tech_coef_ener = tech_coef_ener.set_index(["REG_imp","PROD_COMM","TRAD_COMM"])
        tech_coef_ener = tech_coef_ener.join(delta_tech_coef_CP)
        tech_coef_ener["delta_tech_coef"] = (
            tech_coef_ener["delta_tech_coef_OP"] * tech_coef_ener["delta_tech_coef_CP"])
        
        # tech_coef_ener.loc[tech_coef_ener["delta_tech_coef"] < 0.8, "delta_tech_coef"] = 0.8
        
        tech_coef_ener["tech_coef_ener"] = (
            tech_coef_ener["a_tech"] * tech_coef_ener["delta_tech_coef"])
        tech_coef_ener = tech_coef_ener.loc[:,["delta_tax","tech_coef_ener"]]
        
        self.tech_coef_ener = tech_coef_ener
        
        return self.tech_coef_ener
        
    def assign_IO_coef_cou(self, IND_BASE, tech_coef_ener, tax_rate):
        tax_cou = list(set(tax_rate['REG_imp'].unique().tolist()))
        if 'ALL' in tax_cou:
            tax_cou = self.COU_ID
        ind_ener_cou = IND_BASE.loc[tax_cou,:]
        ind_ener_cou = ind_ener_cou.join(tech_coef_ener, how='inner')

        # compute new coefficients and corresponding tax revenue by energy carrier
        # assuming constant trade shares, as well as total tax revenue by country and sector
        # (REG_imp and PROD_COMM)

        ind_ener_cou["tech_coef_ener"] = ind_ener_cou["tech_coef_ener"].fillna(
            ind_ener_cou["a_tech"])
        ind_ener_cou["IO_coef_ener"] = (ind_ener_cou["tech_coef_ener"] * 
                                        ind_ener_cou["a_bp"] / ind_ener_cou["a_tech"])
        ind_ener_cou["IO_coef_ener"] = ind_ener_cou["IO_coef_ener"].fillna(0)
        ind_ener_cou["z_bp_ener"] = ind_ener_cou["IO_coef_ener"] * ind_ener_cou["output"]
        
        ind_ener_cou = ind_ener_cou.reset_index(drop=False)
        ind_ener_cou = ind_ener_cou.set_index(["REG_imp","PROD_COMM","REG_exp","TRAD_COMM"])
        
        self.ind_ener_cou_base = ind_ener_cou.loc[:,["a_bp","a_tech","z_bp"]]
        self.ind_ener_cou = ind_ener_cou.loc[:,["IO_coef_ener","tech_coef_ener","z_bp_ener"]]
        
        return self.ind_ener_cou
    
    def build_tax_helper_matrix(self, ind_ener_cou):
        Reg_Sec = ind_ener_cou.reset_index()[
            ["REG_imp","PROD_COMM","REG_exp","TRAD_COMM"]]

        tax_index = sorted(set([(a,b) for a,b in zip(
            Reg_Sec["REG_imp"], Reg_Sec["PROD_COMM"])]))
        
        self.tax_index = tax_index

        ind_ener_cou = pd.concat([self.ind_ener_cou_base, ind_ener_cou], axis=1)
        
        # Build tax Matrix
        tax_matrix = ind_ener_cou.loc[:,["a_bp", "IO_coef_ener"]]
        tax_matrix["delta_IO_coef"] = tax_matrix["IO_coef_ener"] - tax_matrix["a_bp"]
        tax_matrix = tax_matrix.drop(columns=["a_bp", "IO_coef_ener"])
        tax_matrix = tax_matrix.reset_index()
        tax_matrix["IMP_SEC"] = pd.Series(list(zip(tax_matrix["REG_imp"], tax_matrix["PROD_COMM"])))
        tax_matrix["EXP_SEC"] = pd.Series(list(zip(tax_matrix["REG_exp"], tax_matrix["TRAD_COMM"])))
        tax_matrix = tax_matrix.drop(columns=["REG_imp","PROD_COMM","REG_exp","TRAD_COMM"])

        tax_matrix = tax_matrix.set_index(["IMP_SEC","EXP_SEC"])
        tax_matrix = tax_matrix.unstack(level="IMP_SEC")
        tax_matrix.columns = tax_matrix.columns.droplevel(0)

        tax_temp = pd.DataFrame(np.zeros((len(self.A_id),len(tax_index))),
                                index=self.A_id,columns=tax_index)
        tax_temp.loc[tax_matrix.index, tax_matrix.columns] = tax_matrix

        tax_matrix = tax_temp.copy()
        tax_matrix = tax_matrix.fillna(0)
        tax_matrix = tax_matrix.to_numpy()

        # Build Vt Matrix
        sec_temp = pd.DataFrame(np.zeros((len(tax_index), len(self.A_id))),
                                index=tax_index,columns=self.A_id)
        for i in list(sec_temp.index):
            sec_temp[i].loc[[i]] = 1

        sec_matrix = sec_temp.copy()
        sec_matrix = sec_matrix.fillna(0)
        sec_matrix = sec_matrix.to_numpy()

        self.tax_matrix = tax_matrix
        self.sec_matrix = sec_matrix
        
        return self.tax_index, self.tax_matrix, self.sec_matrix
        
    def assign_IO_coef_glo(self, IND_BASE, ind_ener_cou):        
        # ind_ener_cou = self.ind_ener_cou
        
        ind_ener_glo = IND_BASE.copy()

        for i in list(ind_ener_cou.columns):
            ind_ener_glo[i] = np.nan

        ind_ener_glo.loc[ind_ener_cou.index, ind_ener_cou.columns] = ind_ener_cou

        ind_ener_glo["IO_coef_ener"] = ind_ener_glo["IO_coef_ener"].fillna(
            ind_ener_glo["a_bp"])
        ind_ener_glo["tech_coef_ener"] = ind_ener_glo["tech_coef_ener"].fillna(
            ind_ener_glo["a_tech"])
        ind_ener_glo["z_bp_ener"] = ind_ener_glo["z_bp_ener"].fillna(
            ind_ener_glo["z_bp"])
        
        self.ind_ener_glo = ind_ener_glo.loc[:,[
            "IO_coef_ener", "tech_coef_ener", "z_bp_ener"]]
        
        return self.ind_ener_glo
    
