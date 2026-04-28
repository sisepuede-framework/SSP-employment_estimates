# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 16:44:06 2023

@author: wb582890
"""

import numpy as np
import pandas as pd
from concurrent import futures
from tqdm import tqdm

class BTA:
    def __init__(self, scenario, bta, regions, temp, exog_vars):
        self.bta = bta
        self.REGIONS = regions
        self.REGIONS_list = exog_vars.COU_ID
        self.scenario_file = scenario.scenario_file
        self.ALL_POLLUTANTS = exog_vars.ALL_POLLUTANTS
        self.ALL_PROCESS_EMISSIONS = exog_vars.ALL_PROCESS_EMISSIONS
        self.temp = temp

        try:
            self.carbon_tax_countries = scenario.carbon_tax_countries
        except AttributeError:
            pass

        try:
            cbam_setup = pd.read_excel(self.scenario_file, sheet_name="cbam")
        except ValueError:
            # catch if there is no sheet
            cbam_setup = pd.DataFrame(columns=['REG_imp','TRAD_COMM','REG_exp','cbam'])

        # REG_exp with exclusion
        sel = cbam_setup['REG_exp'].str.contains('ALL\[')
        exclude = cbam_setup[sel].copy()
        exclude['REG_exp_excl'] = exclude['REG_exp'].str.extract(r"^ALL\[(.*?)\]")[0].str.split(",")
        cbam_setup.loc[sel,'REG_exp'] = 'ALL'

        # comma in TRAD_COMM
        sel = cbam_setup['TRAD_COMM'].str.contains(",")
        cbam_setup['new_TRAD_COMM'] = np.nan
        cbam_setup.loc[sel, 'new_TRAD_COMM'] = cbam_setup.loc[sel, 'TRAD_COMM'].str.split(',')
        cbam_setup = cbam_setup.explode('new_TRAD_COMM')
        cbam_setup.loc[~cbam_setup['new_TRAD_COMM'].isna(),'TRAD_COMM'] = cbam_setup['new_TRAD_COMM']
        cbam_setup = cbam_setup.drop(columns=['new_TRAD_COMM'])

        # treatment of ALL in TRAD_COMM, ie all upstream sectors impacted
        pairs = cbam_setup[cbam_setup['TRAD_COMM']=='ALL'][['REG_imp','REG_exp','cbam']].copy()
        if len(pairs) > 0:
            pairs['key'] = 1
            keys = pd.DataFrame({
                'TRAD_COMM': [x for x in np.arange(1,121)],
                'key': 1
            })
            complement_ALL = keys.merge(pairs, how='left', on='key')
            cbam_setup = pd.concat([cbam_setup[cbam_setup['TRAD_COMM']!='ALL'], complement_ALL])
            cbam_setup = cbam_setup.drop(columns=['key'])

            del complement_ALL

        # treatment for ALL in TRAD_COMM, ie all downstream sectors impacted
        pairs = cbam_setup[cbam_setup['REG_exp']=='ALL'][['REG_imp','TRAD_COMM','cbam']].copy()
        if len(pairs) > 0:
            pairs['key'] = 1
            keys = pd.DataFrame({
                'REG_exp': self.REGIONS['Region_acronyms'].to_list(),
                'key': 1
            })
            complement_ALL = keys.merge(pairs, how='left', on='key')
            cbam_setup = pd.concat([cbam_setup[cbam_setup['REG_exp']!='ALL'], complement_ALL])
            cbam_setup = cbam_setup.drop(columns=['key'])

            del complement_ALL
        del pairs

        for k, r in exclude.iterrows():
            cbam_setup = cbam_setup[((cbam_setup['REG_imp']!=r['REG_imp'])|\
                                     (cbam_setup['TRAD_COMM']!=r['TRAD_COMM']))|\
                                        (~cbam_setup['REG_exp'].isin(r['REG_exp_excl']))]

        # * export BTA don't use
        if (self.bta == 1):
            bta_exp_df = scenario.scenario_data["bta_exports"]
            bta_exp_df.reset_dimensions()

            bta_exp_df = pd.DataFrame(bta_exp_df.values)

            bta_exp_df.columns = bta_exp_df.iloc[0]
            bta_exp_df = bta_exp_df.drop(index=0)
            bta_exp_df = bta_exp_df.reset_index().drop(columns=["index"])
            
            bta_exp = bta_exp_df.melt(id_vars=['REG_exp','PROD_COMM'],
                                         value_vars=list(bta_exp_df.columns)[2:])
            bta_exp = bta_exp.rename(columns={0:"REG_imp", "value":"BTA_exp"})
            bta_exp["BTA_exp"] = pd.Series(bta_exp["BTA_exp"], dtype=int)
            # bta_exp = bta_exp.set_index(["REG_exp","PROD_COMM","REG_imp"])
            # bta_exp = bta_exp[bta_exp["BTA_exp"] != 0]
            
            self.bta_exp = bta_exp
        
        # ! IMPORT BTA and no BTA (i.e. bta will be zero / non-existent)
        elif (self.bta == -1 or self.bta == 0):
            # bta_imp_df = scenario.scenario_data["bta_imports"]
            # bta_imp_df.reset_dimensions()
            # bta_imp_df = pd.DataFrame(bta_imp_df.values)
            
            # bta_imp_df.columns = bta_imp_df.iloc[0]
            # bta_imp_df = bta_imp_df.drop(index=0)
            # bta_imp_df = bta_imp_df.reset_index().drop(columns=["index"])

            # bta_imp = bta_imp_df.melt(id_vars=["REG_exp","PROD_COMM"],
            #                           value_vars=bta_imp_df.columns[2:])
            # bta_imp = bta_imp.rename(columns={"PROD_COMM":"TRAD_COMM", 0:"REG_imp",
            #                                   "value":"BTA_imp"})
            
            # bta_imp["BTA_imp"] = pd.Series(bta_imp["BTA_imp"], dtype=int)
            # bta_imp = bta_imp.set_index(["REG_exp","PROD_COMM","REG_imp"])
            # bta_imp = bta_imp[bta_imp["BTA_exp"] != 0]

            # * cbam setup structure
            # * REG_exp REG_imp TRAD_COMM cbam
            bta_imp = cbam_setup
            
            self.bta_imp = bta_imp

    def cbam_incidence_loop(self, country):
        """
        This loop calculates the CBAM incidence given carbon_tax_rate files generated
        by earlier functions (these are stored in the Temp folder).
        This loop is only expected to be run within the `calculate_cbam_incidence` function
        in a parallel loop.
        """
        # import pdb; pdb.set_trace()

        # first get the carbon_tax_rate of the target
        carbon_tax_rate = self.temp.read_from_pickle("{}_carbon_tax_rate".format(country), delete_=False)
        # calculate emission cost per flow
        carbon_tax_rate = carbon_tax_rate.pipe(lambda d: d[~d['ctax'].isna()])
        carbon_tax_rate = carbon_tax_rate.astype({'PROD_COMM':'str'})
        carbon_tax_rate = carbon_tax_rate.drop(columns=['REG_exp','TRAD_COMM','REG_imp'])
        # reg_exp and trad_comm is just technicality
        carbon_tax_rate = carbon_tax_rate.groupby(['PROD_COMM']).agg({'ctax':'mean'}).reset_index()

        mrio = self.mrio[self.mrio['REG_imp']==country].drop(columns=['IO_coef_ener','tech_coef_ener']).copy()
        # share of flow within REG_imp / target-sector
        mrio = mrio.astype({'PROD_COMM': 'str', 'TRAD_COMM': 'str'})
        
        mrio = mrio.groupby(['REG_imp','REG_exp','TRAD_COMM']).agg({'z_bp_ener':'sum','imp_exp_TRAD_share':'sum'}).reset_index()

        # ! FINAL DEMAND IS MISSING FROM PROCESS EMISSIONS

        # mrio is
        #  REG_imp REG_exp TRAD_COMM

        rename_ = {'REG_imp':'REG_exp','PROD_COMM':'TRAD_COMM'}
        self.scope1['REG_imp'] = self.scope1['REG_imp'].astype('str')
        self.scope1['REG_imp'] = self.scope1['REG_imp'].astype('str')
        mrio['REG_imp'] = mrio['REG_imp'].astype('str')
        mrio['REG_exp'] = mrio['REG_exp'].astype('str')
        
        cbam_incidence = mrio.merge(self.scope1.rename(columns=rename_),
                                     how='left', on=['REG_exp','TRAD_COMM'])\
                                     .merge(self.scope2.rename(columns=rename_), how='left',
                                             on=['REG_exp','TRAD_COMM'])
        

        cbam_incidence['SCOPE1_EMISSIONS'] = cbam_incidence['SCOPE1_EMISSIONS'] * cbam_incidence['imp_exp_TRAD_share']
        cbam_incidence['SCOPE2_EMISSIONS'] = cbam_incidence['SCOPE2_EMISSIONS'] * cbam_incidence['imp_exp_TRAD_share']
        
        # with SCOPE1 and SCOPE2 merged on REG_exp and TRAD_COMM
        # scope1 ans scope2 values are duplicated across REG_IMP; but there is only one REG_imp
        
        # carbon_tax_rate -> reg_exp and TRAD_COMM is only technical | we're within a single reg-imp
        # ! TODO carbon_tax_rate technically has REG_exp and TRAD_comm, but it shouldnt
        cbam_incidence = cbam_incidence.merge(carbon_tax_rate.rename(columns={'PROD_COMM':'TRAD_COMM'}),                                        
                                               how='left',on=['TRAD_COMM']).fillna(0)
        
        # actual calculations
        # ! DEFAULT values are need to be added for missing emission rates

        # self.bta_imp stores the CBAM switches
        # 'REG_imp','TRAD_COMM','REG_exp','cbam'

        cbam_incidence = cbam_incidence.merge(self.bta_imp.astype({'TRAD_COMM': 'str'}),
                                               how='left', on=['REG_imp','TRAD_COMM','REG_exp'])

        cbam_incidence['cbam_cost'] =\
              (cbam_incidence['SCOPE1_EMISSIONS'] + cbam_incidence['SCOPE2_EMISSIONS']) * cbam_incidence['ctax']
        cbam_incidence['cbam_cost'] = cbam_incidence['cbam_cost'] * cbam_incidence['cbam']
         # SCOPE1 and SCOPE2 EMISSIONS in tCO2, ctax in USD/tCO2
        cbam_incidence = cbam_incidence[~cbam_incidence['cbam_cost'].isna()]

        # calculate base monetary value of flow to get tax incidence in %
        # merge to emission cost
        # z_bp is in kUSD; emission cost is USD
        cbam_incidence['delta_cbam'] = (cbam_incidence['cbam_cost'] / 1000) / cbam_incidence['z_bp_ener']
        # [delta_cbam] -> 0.1 is 10% -> 0.1

        return cbam_incidence[['REG_imp','REG_exp','TRAD_COMM','delta_cbam','z_bp_ener']].copy()

    def calc_cbam_incidence(self, mrio):

        # import pdb; pdb.set_trace()

        # do for countries with carbon tax
        carbon_tax_countries = self.carbon_tax_countries
        if len(carbon_tax_countries) == 0:
            return pd.DataFrame(columns=['REG_imp','REG_exp','TRAD_COMM','delta_cbam','z_bp_ener'])
        cbam_incidence_all = None

        mrio = mrio.reset_index()

        self.mrio = mrio
        self.mrio['imp_exp_TRAD_share'] = self.mrio['z_bp_ener'] / self.mrio.groupby(['REG_exp','TRAD_COMM'])['z_bp_ener'].transform('sum')

        mrio = mrio.astype({'PROD_COMM':'str','TRAD_COMM':'str'})

        emissions = self.ALL_POLLUTANTS.pipe(lambda d: d[d['POLLUTANT_FRACTION']=='CO2']).copy()
        emissions = emissions.astype({'target-sector':'str','origin-sector':'str'})

        # calculate process emissions
        # target-sector	target-country-iso3	Y_2019	output_kUSD	EF_ktCO2_per_kUSD
        process_emissions = self.ALL_PROCESS_EMISSIONS[['target-sector','target-country-iso3','EF_ktCO2_per_kUSD']].copy()
        process_emissions['target-sector'] = process_emissions['target-sector'].astype(str)
        
        # * TARGET AND ORIGIN is twisted here, bc process emissions are applied not on the incoming, but on the outgoing flow
        process_emissions = process_emissions.rename(columns={'target-sector':'PROD_COMM','target-country-iso3':'REG_imp'})
        process_emissions = process_emissions.merge(mrio, how='left', on=['REG_imp','PROD_COMM'])
        # kUSD * ktco2/kUSD -> ktco2 * 1000
        # PROCESS EMISSION REG_exp TRAD_COMM REG_imp PROD_COMM
        process_emissions['PROCESS_EMISSION'] = process_emissions['z_bp_ener'] * process_emissions['EF_ktCO2_per_kUSD'] * 1000
        process_emissions = process_emissions[['REG_imp','PROD_COMM','REG_exp','TRAD_COMM','PROCESS_EMISSION']]

        # we'll need several things
        # 1st we'll need emissions aggregated for PROD_COMM [scope 1]
        scope1 = emissions.groupby(['target-sector','target-country-iso3']).agg({'POLLUTANT_VALUE':'sum'})
        scope1 = emissions.rename(columns={'target-country-iso3':'REG_imp','target-sector':'PROD_COMM'})\
            .rename(columns={'origin-country-iso3':'REG_exp','origin-sector':'TRAD_COMM'})\
            .merge(process_emissions, how='left', on=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])\
            .groupby(['PROD_COMM','REG_imp']).agg({'POLLUTANT_VALUE':'sum','PROCESS_EMISSION':'sum'})\
            .reset_index()
        scope1['SCOPE1_EMISSIONS'] = scope1['POLLUTANT_VALUE'] + scope1['PROCESS_EMISSION']

        # 2nd emissions in power generation and heat for PROD_COMM [scope 2]
        # 93 is electricity generation and heat
        scope2 = scope1[scope1['PROD_COMM']=='93'].copy()
        scope2 = scope2.rename(columns={'SCOPE1_EMISSIONS':'SCOPE2_EMISSIONS'}).drop(columns=['PROD_COMM'])

        mrio = mrio[mrio['TRAD_COMM']=='93'].copy()
        mrio = mrio[['REG_imp','REG_exp','PROD_COMM','z_bp_ener']].copy()
        mrio = mrio.merge(scope2.rename(columns={'REG_imp':'REG_exp'}), how='left', on=['REG_exp'])
        mrio['electricity_share'] = mrio['z_bp_ener'] / mrio.groupby(['REG_exp'])['z_bp_ener'].transform('sum')
        mrio['SCOPE2_EMISSIONS'] = mrio['SCOPE2_EMISSIONS'] * mrio['electricity_share']
        mrio = mrio.groupby(['REG_imp','PROD_COMM']).agg({'SCOPE2_EMISSIONS':'sum'}).reset_index()

        scope2 = mrio[['REG_imp','PROD_COMM','SCOPE2_EMISSIONS']].copy()

        self.scope1 = scope1
        # REG_imp PROD_COMM SCOPE1_EMISSIONS
        self.scope2 = scope2
        # REG_imp SCOPE2_EMISSIONS

        print("Calculating CBAM incidence... Parallel started.")
        futures_ = [] 
        with futures.ThreadPoolExecutor() as executor:
            for c in carbon_tax_countries:
                futures_.append(executor.submit(self.cbam_incidence_loop, c))
        
            tmp_df = []
            with tqdm(total=len(futures_)) as progress:
                for f in futures.as_completed(futures_):
                    progress.update()
                    tmp_df.append(f.result())
            cbam_incidence_all = pd.concat(tmp_df)

        cbam_incidence_all = cbam_incidence_all[['REG_imp','REG_exp','TRAD_COMM','delta_cbam','z_bp_ener']]
        self.temp.write_to_csv(cbam_incidence_all, 'cbam_incidence_all')

        return cbam_incidence_all
            
    def calc_rev_subtract_exp_base(self, tax_rev_base):
        # return None
        # if (self.bta == 1):
        #     bta_exp = self.bta_exp.set_index(["REG_exp","PROD_COMM","REG_imp"])
        #     bta_exp = bta_exp[bta_exp["BTA_exp"] != 0]
            
        #     tax_rev_base = tax_rev_base.reset_index()
        #     tax_rev_base = tax_rev_base.set_index(["REG_exp","PROD_COMM","REG_imp"])
            
        #     for i in list(bta_exp.columns):
        #         tax_rev_base[i] = np.nan
                
        #     tax_rev_base.loc[bta_exp.index, bta_exp.columns] = bta_exp

        #     tax_rev_base["tax_rev_bta_base"] = tax_rev_base["tax_rev_base"] * tax_rev_base["BTA_exp"]
            
        #     rev_subtract_base = tax_rev_base.groupby(
        #         ["REG_imp","PROD_COMM"])["tax_rev_bta_base"].sum()
        #     rev_subtract_base = rev_subtract_base.to_frame()
        #     rev_subtract_base = rev_subtract_base.rename(
        #         columns={"tax_rev_bta_base": "rev_subtract_base"})
            
        #     self.rev_subtract_exp = rev_subtract_base
            
        #     return self.rev_subtract_exp
        
        # else:
        rev_subtract_exp_base = tax_rev_base.copy()
        rev_subtract_exp_base["rev_subtract_exp_base"] = 0
        
        rev_subtract_exp_base = rev_subtract_exp_base.loc[:,["rev_subtract_exp_base"]]
        
        self.rev_subtract_exp_base = rev_subtract_exp_base
        
        return self.rev_subtract_exp_base
            
    def calc_rev_subtract_exp(self, tax_rev):
        # return None
        # if (self.bta == 1):
        #     bta_exp = self.bta_exp.set_index(["REG_exp","PROD_COMM","REG_imp"])
        #     bta_exp = bta_exp[bta_exp["BTA_exp"] != 0]
            
        #     tax_rev = tax_rev.reset_index()
        #     tax_rev = tax_rev.set_index(["REG_exp","PROD_COMM","REG_imp"])
            
        #     for i in list(bta_exp.columns):
        #         tax_rev[i] = np.nan
                
        #     tax_rev.loc[bta_exp.index, bta_exp.columns] = bta_exp

        #     tax_rev["tax_rev_bta"] = tax_rev["tax_rev"] * tax_rev["BTA_exp"]
        #     # tax_rev["tax_rev_bta_base"] = tax_rev["tax_rev_base"] * tax_rev["BTA_exp"]
            
        #     rev_subtract = tax_rev.groupby(
        #         ["REG_imp","PROD_COMM"])["tax_rev_bta"].sum()
        #     rev_subtract = rev_subtract.to_frame()
        #     rev_subtract = rev_subtract.rename(
        #         columns={"tax_rev_bta": "rev_subtract"})
            
        #     rev_subtract = rev_subtract.loc[:,["rev_subtract"]]
            
        #     self.rev_subtract_exp = rev_subtract
            
        #     return self.rev_subtract_exp
        
        # else:
        rev_subtract_exp = tax_rev.copy()
        rev_subtract_exp["rev_subtract_exp"] = 0
        
        rev_subtract_exp = rev_subtract_exp.loc[:,["rev_subtract_exp"]]
        
        self.rev_subtract_exp = rev_subtract_exp
        
        return self.rev_subtract_exp