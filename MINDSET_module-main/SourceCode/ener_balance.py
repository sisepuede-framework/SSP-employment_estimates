# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 14:12:54 2023

@author: wb582890
"""

import numpy as np
import pandas as pd
import pickle
from SourceCode.utils import temporary_storage
from alive_progress import alive_bar
import gc
from tqdm import tqdm
from concurrent import futures

class ener_balance:
    def __init__(self, exog_vars, scenario):
        self.IND_BASE = exog_vars.IND_BASE.reset_index()
        self.HH_BASE = exog_vars.HH_BASE.reset_index()
        self.GOV_BASE = exog_vars.GOV_BASE.reset_index()
        self.FCF_BASE = exog_vars.FCF_BASE.reset_index()
        self.A_id = exog_vars.A_id
        # self.NPISH = exog_vars.NPISH.reset_index(inplace=True)
        
        self.COU_ID = exog_vars.COU_ID
        self.REGION = exog_vars.R
        self.PRODUCTS = exog_vars.P
        self.DIMS = len(self.REGION) * len(self.PRODUCTS)

        try:
            self.carbon_tax_countries = scenario.carbon_tax_countries
        except AttributeError:
            pass
        
        # read in IEA-energy generated data
        self.ALL_POLLUTANTS = exog_vars.ALL_POLLUTANTS
        self.ALL_PROCESS_EMISSIONS = exog_vars.ALL_PROCESS_EMISSIONS

        self.temp = temporary_storage("Temp")
    
    def init_ener_vars(self):
        self.IEA_eb_sec = 34 # number of flows in IEA
        self.GLORIA_sec = 120 # number of sectors in GLORIA
        self.FD_sec = 6
        
        self.fuel_list_g = ["Coal","Lignite","Oil","Gas","Coke"]
        self.iea_main_fuel = ['COAL','LIGNITE','OIL','GAS','OVENCOKE']
        self.glo_elist_name = ['COAL','LIGNITE','OILExt','GASExt','OVENCOKE','OILRef','GASDis']
        self.gloria_flow_elist = [24,25,26,27,62,63,94]
        self.IEA_GLORIA_corr=[0,1,2,3,4,2,3]
        
        self.tax_sector = [24,25,62,63,94] # oil and gas are taxed when used (mid/downstream taxation)
        self.tax_sector_name = ['COAL','LIGNITE','COKE','OIL','GAS']
        
    def assign_tax_cou(self, Scenario):
        # country_list = ["IDN"] # ["BRA", "KAZ"]
        # coun_num = [71] #34-1 etc. But this will be modified so it depends on country_list and no need to enter manually
        
        # self.tax_scen = Scenario.tax_scen
        # self.country_list = Scenario.country_list
        # self.coun_num = Scenario.coun_num
        self.country_list = ["AUT","BEL","BGR","CZE","CYP","DEU","DNK","ESP","EST","FIN","FRA",
             "GRC","HRV","HUN","IRL","ITA","LVA","LTU","LUX","MLT","NLD","POL","PRT",
             "ROU","SVK","SVN","SWE"]
        self.coun_num = [11, 14, 18, 41, 42, 43, 46, 52, 53, 55, 56, 64, 68, 70, 73, 78, 93, 94, 95, 102, 113, 124, 126, 129,
                         141, 142, 143]

    def calc_emissions_IEA(self):
        #GEF_df = pd.DataFrame(columns=['Fuel_type','REG_imp','IEA_sector','EmisFact'])
        IEA_EB_df = pd.DataFrame(columns=['Fuel_type','REG_imp','IEA_sector','Energy'])

        self.GLORIA_sec_list = list(range (1, self.GLORIA_sec + 1)) # number of sectors in GLORIA
        self.GLORIA_sec_list.extend(['hh', 'npi', 'gov', 'fcf'])

        for i in range(0, len(self.fuel_list_g)):
            A_temp = pd.DataFrame(self.IEA_EB[i], index=self.COU_ID, columns=range(1,34))
            A_temp = A_temp.reset_index()
            A_temp = A_temp.melt(id_vars="index", value_vars=A_temp.columns)
            A_temp.columns = ["REG_imp", "IEA_sector", "Energy"]
            A_temp["Fuel_type"] = self.fuel_list_g[i]
            A_temp = A_temp[['Fuel_type','REG_imp','IEA_sector','Energy']]
            
            IEA_EB_df = pd.concat([IEA_EB_df, A_temp])

        IEA_EB_df = IEA_EB_df[IEA_EB_df['REG_imp'].isin(self.country_list)]
        self.Reg_ID_selected = np.repeat(self.country_list, self.GLORIA_sec)
        
        self.iea_fuel_em = dict()
        self.fuel_em_g = dict()
        
        for i in range(0, len(self.fuel_list_g)): 
            self.iea_fuel_em[i] = np.zeros((len(self.country_list), self.IEA_eb_sec-1))
            self.fuel_em_g[i] = np.zeros((len(self.country_list),(self.FD_sec + self.GLORIA_sec)))
            
        # # Calculates emissions in IEA dimension (fuel, countries, flow)
        for m in range(0, len(self.fuel_list_g)):
             for k in range(0, len(self.country_list)):
                for i in range(0, self.IEA_eb_sec-1):
                     self.iea_fuel_em[m][k,i] = self.IEA_EB[m][self.coun_num[k],i] * self.GEF[m][self.coun_num[k],i]

    def map_emissions_sec(self):
        ret_ = None
        # # The emission is in IEA flow dimension x 164 countries in the fuel order
        for i in range(0,len(self.fuel_list_g)):
            for k in range(0,len(self.country_list)):
                  start = (self.GLORIA_sec+self.FD_sec)*self.coun_num[k]
                  end = (self.GLORIA_sec+self.FD_sec)*(self.coun_num[k]+1)
                  self.fuel_em_g[i][k,0:(self.GLORIA_sec+self.FD_sec)] = np.matmul(
                      self.iea_fuel_em[i][k,0:(self.IEA_eb_sec-1)],
                      self.IEA_GL_map[i][0:self.IEA_eb_sec-1,start:end])
        # return self.IEA_GL_map[0][0:self.IEA_eb_sec-1,start:end]
        # return self.fuel_em_g[0][k,0:(self.GLORIA_sec+self.FD_sec)]
                  
    def calc_fuel_sec(self):
        fuel_em_g_df = {}
        fuel_em_h_df = {}
        fuel_reshaped = {}
        fuel_res_df = {}

        # fuel_em_g has the following structure
        # --> fuel_em_g[x] where x is the energy carrier
        # --> fuel_em_g[x][k,] where k is the country from the country list
        # --> fuel_em_g[x][k,s] where s is the GLORIA sector up to 120 and then final demand (6 sectors)

        for i in range(0,len(self.fuel_list_g)):
        #     # Build dataframe from emissions

            fuel_em_g_df[i] = pd.DataFrame(self.fuel_em_g[i][:,0:self.GLORIA_sec])
            fuel_em_h_df[i] = pd.DataFrame(self.fuel_em_g[i][:,0:(self.FD_sec+self.GLORIA_sec)])
            #fuel_em_h_df[i].columns=allsec['Sector_names']
            fuel_em_h_df[i].index=self.country_list

            # reshape df holding only GLORIA sectors
            fuel_reshaped[i]=fuel_em_g_df[i].values.reshape(((len(self.country_list)*self.GLORIA_sec),1))
            
            fuel_res_df[i] = pd.DataFrame(fuel_reshaped[i])

            fuel_res_df[i]["REG_imp"]=np.repeat(self.country_list, self.GLORIA_sec)
            fuel_res_df[i]["PROD_COMM"]=np.tile(np.arange(1,self.GLORIA_sec+1), len(self.country_list))
            fuel_res_df[i]["fuel"]=self.fuel_list_g[i]
            fuel_res_df[i]=fuel_res_df[i].rename(columns={0:'emissions'})
            
        self.fuel_res_df = fuel_res_df
        return self.fuel_res_df
    
    def calc_fuel_fd(self):
        fuel_em_fd = {}
        for i in range(0,len(self.fuel_list_g)):

            # ####Final demand 
            fuel_em_fd[i] = pd.DataFrame(self.fuel_em_g[i][:,self.GLORIA_sec:(self.GLORIA_sec+self.FD_sec)])
            fuel_em_fd[i]= pd.DataFrame(fuel_em_fd[i])
            fuel_em_fd[i]["REG_imp"]=self.country_list
            fuel_em_fd[i]["fuel"]=self.iea_main_fuel[i]
            fuel_em_fd[i]=fuel_em_fd[i].rename(columns={0:'hh'})
            fuel_em_fd[i]=fuel_em_fd[i].rename(columns={1:'npi'})
            fuel_em_fd[i]=fuel_em_fd[i].rename(columns={2:'gov'})
            fuel_em_fd[i]=fuel_em_fd[i].rename(columns={3:'fcf'})
            fuel_em_fd[i].reset_index(inplace=True) 
            
            self.fuel_em_fd = fuel_em_fd
            
    def a(self):
        z_flow_fuel, z_flowf, em_rev_f = [{}, {}, {}]
        # em_rev_f_phy = []

        # z_flow_fuel is the aggregate monetary use of the flow by REG_imp and by PROD_COMM

        for i in range(0,len(self.gloria_flow_elist)):
            z_flow_fuel[i]=self.IND_BASE.loc[(self.IND_BASE['REG_imp'].isin(self.country_list)) \
                                             & (self.IND_BASE['TRAD_COMM'] == self.gloria_flow_elist[i])]\
                                                [['PROD_COMM','z_bp','REG_imp','REG_exp']].groupby(['REG_imp','PROD_COMM'])['z_bp'].sum()    
            z_flowf[i]=z_flow_fuel[i].to_frame()
            z_flowf[i].reset_index(inplace=True)
            em_rev_f[i] = pd.merge(z_flowf[i], self.fuel_res_df[self.IEA_GLORIA_corr[i]],  how='left', left_on=['REG_imp','PROD_COMM'], right_on=['REG_imp','PROD_COMM'])
            # em_rev_f_phy[i] = pd.merge(em_rev_f[i], fuel_phy_df[IEA_GLORIA_corr[i]],  how='left', left_on=['REG_imp','PROD_COMM'], right_on=['REG_imp','PROD_COMM'])

        print("inside enerbal")
        # import pdb; pdb.set_trace()
        # for i in range(0,len(self.gloria_flow_elist)):
            # em_rev_f_phy[i] = pd.merge(em_rev_f[i], fuel_phy_df[self.IEA_GLORIA_corr[i]],  how='left', left_on=['REG_imp','PROD_COMM'], right_on=['REG_imp','PROD_COMM'])
            
        em_rev_coa = em_rev_f[self.glo_elist_name.index('COAL')].rename(columns={"z_bp":"z_bp_coal", "emissions":"emissions_coal"})
        em_rev_coa = em_rev_coa.drop(columns=["fuel"])
        em_rev_lig = em_rev_f[self.glo_elist_name.index('LIGNITE')].rename(columns={"z_bp":"z_bp_lignite", "emissions":"emissions_lignite"})
        em_rev_lig = em_rev_lig.drop(columns=["fuel"])
        em_rev_cok = em_rev_f[self.glo_elist_name.index('OVENCOKE')].rename(columns={"z_bp":"z_bp_coke", "emissions":"emissions_coke"})
        em_rev_cok = em_rev_cok.drop(columns=["fuel"])

        em_rev_coa=pd.merge(em_rev_coa, em_rev_lig, how='outer',
                            left_on=['REG_imp','PROD_COMM'], right_on=['REG_imp','PROD_COMM'])
        em_rev_coa=pd.merge(em_rev_coa, em_rev_cok,  how='outer',
                            left_on=['REG_imp','PROD_COMM'], right_on=['REG_imp','PROD_COMM'])
        em_rev_gas=pd.merge(em_rev_f[self.glo_elist_name.index('GASExt')], em_rev_f[self.glo_elist_name.index('GASDis')],  how='outer',
                            left_on=['REG_imp','PROD_COMM'], right_on=['REG_imp','PROD_COMM'])
        em_rev_gas = em_rev_gas.drop(columns=["fuel_x", "fuel_y"])
        em_rev_oil=pd.merge(em_rev_f[self.glo_elist_name.index('OILExt')], em_rev_f[self.glo_elist_name.index('OILRef')],  how='outer',
                            left_on=['REG_imp','PROD_COMM'], right_on=['REG_imp','PROD_COMM'])
        em_rev_oil = em_rev_oil.drop(columns=["fuel_x", "fuel_y"])

        em_rev_gas.loc[em_rev_gas.PROD_COMM==94,'z_bp_x']=0 # Block this flow to zero
        em_rev_oil['z_bp_x']=0

        em_rev_coa = em_rev_coa.fillna(0)
        em_rev_gas = em_rev_gas.fillna(0)
        em_rev_oil = em_rev_oil.fillna(0)

        em_rev_coa['z_bp']=em_rev_coa['z_bp_coal']+em_rev_coa['z_bp_lignite']+em_rev_coa['z_bp_coke']
        em_rev_coa['emissions']=em_rev_coa['emissions_coal']+em_rev_coa['emissions_lignite']+em_rev_coa['emissions_coke']

        em_rev_oil['z_bp']=em_rev_oil['z_bp_x']+em_rev_oil['z_bp_y']

        em_rev_gas['z_bp']=em_rev_gas['z_bp_x']+em_rev_gas['z_bp_y']
        em_rev_oil['z_bp']=em_rev_oil['z_bp_x']+em_rev_oil['z_bp_y']

        em_rev_gas["emissions"] = em_rev_gas[["emissions_x", "emissions_y"]].max(axis=1)
        em_rev_oil["emissions"] = em_rev_oil[["emissions_x", "emissions_y"]].max(axis=1)

        # import pdb; pdb.set_trace()

        self.em_rev_coa = em_rev_coa
        self.em_rev_oil = em_rev_oil
        self.em_rev_gas = em_rev_gas

    def calc_mon_flow_fd(self):
        z_hh_fuel, z_gov_fuel, z_fcf_fuel, z_npi_fuel = [{}, {}, {}, {}]
        z_hh, z_gov, z_fcf, z_npi = [{}, {}, {}, {}]
        # #Final demand sectors
        for i in range(0,len(self.gloria_flow_elist)):
            z_hh_fuel[self.glo_elist_name[i]]=self.HH_BASE.loc[(self.HH_BASE['REG_imp'].isin(self.country_list)) & (self.HH_BASE['TRAD_COMM'] == self.gloria_flow_elist[i])][['VIPA','REG_imp','REG_exp']].groupby(['REG_imp'])['VIPA'].sum()    
            z_gov_fuel[self.glo_elist_name[i]]=self.GOV_BASE.loc[(self.GOV_BASE['REG_imp'].isin(self.country_list)) & (self.GOV_BASE['TRAD_COMM'] == self.gloria_flow_elist[i])][['VIGA','REG_imp','REG_exp']].groupby(['REG_imp'])['VIGA'].sum()    
            z_fcf_fuel[self.glo_elist_name[i]]=self.FCF_BASE.loc[(self.FCF_BASE['REG_imp'].isin(self.country_list)) & (self.FCF_BASE['TRAD_COMM'] == self.gloria_flow_elist[i])][['VDFA','REG_imp','REG_exp']].groupby(['REG_imp'])['VDFA'].sum()   
            # z_npi_fuel[self.glo_elist_name[i]]=self.NPISH.loc[(self.NPISH['REG_imp'].isin(self.country_list)) & (self.NPISH['TRAD_COMM'] == self.gloria_flow_elist[i])][['NPISH','REG_imp','REG_exp']].groupby(['REG_imp'])['NPISH'].sum() 
            #Add a column of finaldemandhh etc. 
            z_hh[self.glo_elist_name[i]]=z_hh_fuel[self.glo_elist_name[i]].to_frame()
            z_gov[self.glo_elist_name[i]]=z_gov_fuel[self.glo_elist_name[i]].to_frame()
            z_fcf[self.glo_elist_name[i]]=z_fcf_fuel[self.glo_elist_name[i]].to_frame()
            # z_npi[self.glo_elist_name[i]]=z_npi_fuel[self.glo_elist_name[i]].to_frame()
            z_hh[self.glo_elist_name[i]].rename(columns = {'VIPA':self.glo_elist_name[i]}, inplace = True)
            z_gov[self.glo_elist_name[i]].rename(columns = {'VIGA':self.glo_elist_name[i]}, inplace = True)
            z_fcf[self.glo_elist_name[i]].rename(columns = {'VDFA':self.glo_elist_name[i]}, inplace = True)
            # z_npi[self.glo_elist_name[i]].rename(columns = {'NPISH':self.glo_elist_name[i]}, inplace = True)    
            z_hh[self.glo_elist_name[i]].reset_index(inplace=True)
            z_gov[self.glo_elist_name[i]].reset_index(inplace=True)
            z_fcf[self.glo_elist_name[i]].reset_index(inplace=True)
            # z_npi[self.glo_elist_name[i]].reset_index(inplace=True)

        z_hh_m = pd.concat([z_hh[self.glo_elist_name[0]],z_hh[self.glo_elist_name[1]],z_hh[self.glo_elist_name[2]],z_hh[self.glo_elist_name[3]],z_hh[self.glo_elist_name[4]],z_hh[self.glo_elist_name[5]],z_hh[self.glo_elist_name[6]]], axis=1)
        z_hh_m['PROD_COMM']='finalhhdemand'
        z_gov_m = pd.concat([z_gov[self.glo_elist_name[0]],z_gov[self.glo_elist_name[1]],z_gov[self.glo_elist_name[2]],z_gov[self.glo_elist_name[3]],z_gov[self.glo_elist_name[4]],z_gov[self.glo_elist_name[5]],z_gov[self.glo_elist_name[6]]], axis=1)
        z_gov_m['PROD_COMM']='finalgovdemand'
        z_fcf_m = pd.concat([z_fcf[self.glo_elist_name[0]],z_fcf[self.glo_elist_name[1]],z_fcf[self.glo_elist_name[2]],z_fcf[self.glo_elist_name[3]],z_fcf[self.glo_elist_name[4]],z_fcf[self.glo_elist_name[5]],z_fcf[self.glo_elist_name[6]]], axis=1)
        z_fcf_m['PROD_COMM']='fcfdemand'
        # z_npi_m = pd.concat([z_npi[self.glo_elist_name[0]],z_npi[self.glo_elist_name[1]],z_npi[self.glo_elist_name[2]],z_npi[self.glo_elist_name[3]],z_npi[self.glo_elist_name[4]],z_npi[self.glo_elist_name[5]],z_npi[self.glo_elist_name[6]]], axis=1)
        # z_npi_m['PROD_COMM']='npishdemand'
        #merge z and 
        # z_fd_m=pd.concat([z_hh_m,z_gov_m,z_fcf_m,z_npi_m])
        z_fd_m=pd.concat([z_hh_m,z_gov_m,z_fcf_m])

        z_hh_gas = pd.merge(z_hh_fuel['GASExt'], z_hh_fuel['GASDis'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])
        z_hh_oil = pd.merge(z_hh_fuel['OILExt'], z_hh_fuel['OILRef'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])
        z_gov_gas = pd.merge(z_gov_fuel['GASExt'], z_gov_fuel['GASDis'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])
        z_gov_oil = pd.merge(z_gov_fuel['OILExt'], z_gov_fuel['OILRef'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])
        z_fcf_gas = pd.merge(z_fcf_fuel['GASExt'], z_fcf_fuel['GASDis'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])
        z_fcf_oil = pd.merge(z_fcf_fuel['OILExt'], z_fcf_fuel['OILRef'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])
        # z_npi_gas = pd.merge(z_npi_fuel['GASExt'], z_npi_fuel['GASDis'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])
        # z_npi_oil = pd.merge(z_npi_fuel['OILExt'], z_npi_fuel['OILRef'],  how='left', left_on=['REG_imp'], right_on=['REG_imp'])

        z_hh_gas.reset_index(inplace=True)
        z_hh_oil.reset_index(inplace=True)
        z_gov_gas.reset_index(inplace=True)
        z_gov_oil.reset_index(inplace=True)
        z_fcf_gas.reset_index(inplace=True)
        z_fcf_oil.reset_index(inplace=True)
        # z_npi_gas.reset_index(inplace=True)
        # z_npi_oil.reset_index(inplace=True)

        # FD_gas=[z_hh_gas,z_gov_gas,z_fcf_gas,z_npi_gas]
        # FD_oil=[z_hh_oil,z_gov_oil,z_fcf_oil,z_npi_oil]
        # FD_variable=['VIPA_','VIGA_','VDFA_','NPISH_']
        FD_gas=[z_hh_gas,z_gov_gas,z_fcf_gas]
        FD_oil=[z_hh_oil,z_gov_oil,z_fcf_oil]
        FD_variable=['VIPA_','VIGA_','VDFA_']

        for i in range(0,len(FD_gas)):
             FD_gas[i][FD_variable[i]+'y'] = FD_gas[i][FD_variable[i]+'y'].fillna(0)
             FD_gas[i][FD_variable[i]]=FD_gas[i][FD_variable[i]+'x']+FD_gas[i][FD_variable[i]+'y']
            
        for i in range(0,len(FD_oil)):
            FD_oil[i][FD_variable[i]+'y'] = FD_oil[i][FD_variable[i]+'y'].fillna(0)
            FD_oil[i][FD_variable[i]]=FD_oil[i][FD_variable[i]+'x']+FD_oil[i][FD_variable[i]+'y']    

        fuel_emfd_m=pd.concat([self.fuel_em_fd[self.IEA_GLORIA_corr[0]],self.fuel_em_fd[self.IEA_GLORIA_corr[1]],\
                               self.fuel_em_fd[self.IEA_GLORIA_corr[2]],self.fuel_em_fd[self.IEA_GLORIA_corr[3]],\
                                self.fuel_em_fd[self.IEA_GLORIA_corr[4]],self.fuel_em_fd[self.IEA_GLORIA_corr[5]],\
                                    self.fuel_em_fd[self.IEA_GLORIA_corr[6]]], axis=0)
        # fuel_emfd_m.rename({'hh': 'finalhhdemand', 'npi': 'npishdemand', 'gov': 'finalgovdemand', 'fcf': 'fcfdemand'}, axis=1, inplace=True)
        fuel_emfd_m.rename({'hh': 'finalhhdemand', 'gov': 'finalgovdemand', 'fcf': 'fcfdemand'}, axis=1, inplace=True)
        fuel_emfd_m=fuel_emfd_m.drop(fuel_emfd_m.columns[0],axis = 1)
        # fuel_emfd_sel=fuel_emfd_m[['finalhhdemand','finalgovdemand','fcfdemand','npishdemand']].transpose()
        fuel_emfd_sel=fuel_emfd_m[['finalhhdemand','finalgovdemand','fcfdemand']].transpose()
        fuel_emfd_a=fuel_emfd_sel.values.reshape((7*len(self.country_list)*3, 1))
        fuel_emfd_a=pd.DataFrame(fuel_emfd_a)
        
        # set fuel column 
        # coun_F=pd.concat([fuel_emfd_m['REG_imp'],fuel_emfd_m['REG_imp'],fuel_emfd_m['REG_imp'],fuel_emfd_m['REG_imp']])
        coun_F=pd.concat([fuel_emfd_m['REG_imp'],fuel_emfd_m['REG_imp'],fuel_emfd_m['REG_imp']])
        coun_F=coun_F.to_frame()
        coun_F=coun_F.set_index(fuel_emfd_a.index)
        fuel_emfd_a['REG_imp']=coun_F['REG_imp']
        #set country column 
        prod_F=pd.DataFrame([['finalhhdemand']*7*len(self.country_list),['finalgovdemand']*7*len(self.country_list),
                             ['fcfdemand']*7*len(self.country_list)])
        # prod_F_df=prod_F.values.reshape((28*1, 1))
        prod_F_df=prod_F.values.reshape((21*1*len(self.country_list), 1))
        # import pdb; pdb.set_trace()
        fuel_emfd_a['PROD_COMM']=[x[0] for x in prod_F_df.tolist()]
        #fuel use 
        #form a column with the same names 
        f_typ=pd.concat([fuel_emfd_m['fuel'],fuel_emfd_m['fuel'],fuel_emfd_m['fuel'],fuel_emfd_m['fuel']])
        f_typ_1=pd.DataFrame([['COAL','LIGNITE','OILExt','GASExt','OVENCOKE','OILRef','GASDis']*2])
        f_typ_2=f_typ_1.values.reshape((14, 1))
        f_typ_2=pd.DataFrame(f_typ_2)
        f_typ=pd.concat([f_typ_2,f_typ_2,f_typ_2,f_typ_2])
        f_typ=f_typ.reset_index()
        fuel_emfd_a['Fuel']=f_typ[0]
        #Then I need to reshape 
        z_fd_se=z_fd_m[['COAL','LIGNITE','OILExt','GASExt','OVENCOKE','OILRef','GASDis']]
        # z_fd_res=z_fd_se.values.reshape((7*len(self.country_list)*4, 1))
        z_fd_res=z_fd_se.values.reshape((7*len(self.country_list)*3, 1))
        z_fd_res=pd.DataFrame(z_fd_res)
        # z_fd_fuel=pd.DataFrame([['COAL','LIGNITE','OILExt','GASExt','OVENCOKE','OILRef','GASDis']*4*len(self.country_list)])
        z_fd_fuel=pd.DataFrame([['COAL','LIGNITE','OILExt','GASExt','OVENCOKE','OILRef','GASDis']*3*len(self.country_list)])
        # fuel_z=z_fd_fuel.values.reshape((28*1, 1))
        fuel_z=z_fd_fuel.values.reshape((21*1*len(self.country_list), 1))
        fuel_z=pd.DataFrame(fuel_z)
        z_fd_res['Fuel']=fuel_z
        #country 
        z_coun=pd.DataFrame([self.country_list*3*7]).transpose()
        z_fd_res['REG_imp']=z_coun
        #sector 
        z_fd_m = z_fd_m.reset_index()
        z_sec_com=pd.DataFrame([['finalhhdemand']*7*len(self.country_list),['finalgovdemand']*7*len(self.country_list),['fcfdemand']*7*len(self.country_list)])
        z_sec_res=pd.DataFrame(z_sec_com.values.reshape((21*1*len(self.country_list), 1)))
        z_fd_res['PROD_COMM']=z_sec_res
        #fuel_emfd['COAL']=fuel_emfd_m
        #Merge dataframes based on three values 
        z_emfd_com=pd.merge(z_fd_res, fuel_emfd_a,  how='left', left_on=['REG_imp','Fuel','PROD_COMM'], right_on=['REG_imp','Fuel','PROD_COMM'])
        z_emfd_com = z_emfd_com.rename(columns={'0_x': 'z_bp', '0_y': 'emissions'})

        # import pdb; pdb.set_trace()

        self.z_emfd_com = z_emfd_com
        
    def calc_tax_incidence_sec(self):
        cols_ = ['REG_imp','PROD_COMM','z_bp','emissions','fuel']
        tax_rate_list = pd.DataFrame(columns=cols_)
        tax_rate_list = pd.concat([tax_rate_list,self.em_rev_coa.assign(fuel='coal')[cols_]])
        tax_rate_list = pd.concat([tax_rate_list,self.em_rev_oil.assign(fuel='oil')[cols_]])
        tax_rate_list = pd.concat([tax_rate_list,self.em_rev_gas.assign(fuel='gas')[cols_]])

        self.tax_incidence_sec = tax_rate_list

    def calc_tax_incidence_fd(self):
        fd_dta={}    
        #Combine the final demand sectors
        #form final demand sectors of of the format of the intermediate sectors
        #rename
        z_emfd_com = self.z_emfd_com.rename({'0_x': 'z_bp', '0_y': 'emissions'}, axis=1)
        for i in range(0,len(self.glo_elist_name)):
            fd_dta[i]=z_emfd_com.loc[z_emfd_com['Fuel']==self.glo_elist_name[i]][['REG_imp','z_bp','emissions','PROD_COMM']] # "physical units"
            fd_dta[i].reset_index(inplace=False)
            fd_dta[i]=fd_dta[i].fillna(0)

        fd_cleaned={}

        fd_cleaned[0] = pd.merge(fd_dta[0], fd_dta[1], on=['REG_imp','PROD_COMM'])
        fd_cleaned[0] = pd.merge(fd_cleaned[0], fd_dta[4], on=['REG_imp','PROD_COMM'])
        fd_cleaned[0]['z_bp']=fd_cleaned[0]['z_bp_x'] + fd_cleaned[0]['z_bp_y'] + fd_cleaned[0]['z_bp'] # fd_dta[len(self.glo_elist_name)]['z_bp_x']+
        fd_cleaned[0]['emissions']=fd_cleaned[0]['emissions_x'] + fd_cleaned[0]['emissions_y'] + fd_cleaned[0]['emissions']

        fd_cleaned[1] = pd.merge(fd_dta[2], fd_dta[5], on=['REG_imp','PROD_COMM'])
        fd_cleaned[1]['z_bp']=fd_cleaned[1]['z_bp_y'] # fd_dta[len(self.glo_elist_name)]['z_bp_x']+
        fd_cleaned[1]['emissions']=fd_cleaned[1]['emissions_y'] # fd_dta[len(self.glo_elist_name)]['z_bp_x']+

        fd_cleaned[2] = pd.merge(fd_dta[3], fd_dta[6], on=['REG_imp','PROD_COMM'])
        fd_cleaned[2]['z_bp']=fd_cleaned[2]['z_bp_x'] + fd_cleaned[2]['z_bp_y'] # fd_dta[len(self.glo_elist_name)]['z_bp_x']+
        fd_cleaned[2]['emissions']=fd_cleaned[2]['emissions_y'] # fd_dta[len(self.glo_elist_name)]['z_bp_x']+

        cols_ = ['REG_imp','PROD_COMM','z_bp','emissions','fuel']
        incidence = pd.DataFrame(columns=cols_)
        incidence = pd.concat([incidence,fd_cleaned[0].assign(fuel='coal')[cols_]])
        incidence = pd.concat([incidence,fd_cleaned[1].assign(fuel='oil')[cols_]])
        incidence = pd.concat([incidence,fd_cleaned[2].assign(fuel='gas')[cols_]])

        # tax_rate_fd={}

        #Merge fd_dta w 
        # for i in range(0,3):
            # tax_rate_fd[i]=pd.merge(tax_scen_s, fd_cleaned[i], on=['REG_imp','PROD_COMM'])
            
        # tax_rate_fd[0]['tax_rate']=(tax_rate_fd[0]['emissions']*tax_rate_fd[0]['COAL']).sum()/tax_rate_fd[0]['z_bp'].sum()/1000
        # tax_rate_fd[1]['tax_rate']=(tax_rate_fd[1]['emissions']*tax_rate_fd[1]['OILRef']).sum()/tax_rate_fd[1]['z_bp'].sum()/1000
        # tax_rate_fd[2]['tax_rate']=(tax_rate_fd[2]['emissions']*tax_rate_fd[2]['GASDis']).sum()/tax_rate_fd[2]['z_bp'].sum()/1000

        self.tax_incidence_fd = incidence

    def merge_and_calc_tax(self):
        df = pd.concat([self.tax_incidence_sec, self.tax_incidence_fd])
        carbon_tax_rate = self.carbon_tax_rate

        df = df.merge(carbon_tax_rate, how='left', on=['REG_imp','PROD_COMM'])
        df.fillna(0, inplace=True)
        # multiply by 100 bc that's how it goes into taxes
        # MNG fuel:coal -> power generation
        # ctax * emission / [monetary flow]
        # tax incidence of the input of the industry
        # [ctax] -> USD / tco2
        # [emissions] -> tco2
        # [z_bp] -> kUSD
        # [delta_tax] -> percentages as in 10 is 10% -> 0.1

        df['delta_tax'] = df['ctax'] * df['emissions'] / df['z_bp'] / 1000 * 100
        
        # coal 24-25
        df_coa = df[df['fuel']=='coal'].copy()
        df_coa = pd.concat([df_coa.assign(TRAD_COMM = 24), df_coa.assign(TRAD_COMM = 25)])
        df_coa = df_coa[['REG_imp','PROD_COMM','TRAD_COMM','delta_tax']]
        # gas 27
        df_gas = df[df['fuel']=='gas'].copy()
        df_gas = df_gas.assign(TRAD_COMM = 27)
        df_gas = df_gas[['REG_imp','PROD_COMM','TRAD_COMM','delta_tax']]
        # oil 26-63
        df_oil = df[df['fuel']=='oil'].copy()
        df_oil = pd.concat([df_oil.assign(TRAD_COMM = 26), df_oil.assign(TRAD_COMM = 63)])
        df_oil = df_oil[['REG_imp','PROD_COMM','TRAD_COMM','delta_tax']]

        df = pd.concat([df_coa,df_gas,df_oil])

        return df
    
    def read_tax_incidence(self, tax_incidence_file):
        tmp_ = None
        tmp_ = pd.read_csv(tax_incidence_file)

        return tmp_
    
    def tax_incidence_loop(self, country):
        """
        This loop calculates the tax incidence given carbon_tax_rate files generated
        by earlier functions (these are stored in the Temp folder).
        This loop is only expected to be run within the `calculate_tax_incidence` function
        in a parallel loop.
        """

        carbon_tax_rate = self.temp.read_from_pickle("{}_carbon_tax_rate".format(country), delete_=False)
        # calculate emission cost per flow
        carbon_tax_rate = carbon_tax_rate.pipe(lambda d: d[~d['ctax'].isna()])
        emissions = self.ALL_POLLUTANTS.pipe(lambda d: d[d['POLLUTANT_FRACTION']=='CO2']).copy()

        carbon_tax_rate = carbon_tax_rate.astype({'PROD_COMM':'str','TRAD_COMM':'str'})
        emissions = emissions.astype({'target-sector':'str','origin-sector':'str'})

        mrio = self.IND_BASE[(self.IND_BASE['REG_imp']==country) | (self.IND_BASE['REG_exp']==country)].drop(columns=['a_bp','a_tech','output']).copy()
        hh_base = self.HH_BASE.reset_index()
        # VIPA; note: does not have PROD_COMM by default
        hh_base = hh_base[(hh_base['REG_imp']==country)|(hh_base['REG_exp']==country)].copy().rename(columns={'VIPA':'z_bp'})
        hh_base['PROD_COMM'] = 'FD_1'
        mrio = pd.concat([mrio, hh_base])
        # share of flow within REG_imp / target-sector
        mrio = mrio.astype({'TRAD_COMM': 'str', 'PROD_COMM': 'str'})

        # ! FINAL DEMAND IS MISSING FROM PROCESS EMISSIONS

        # import pdb; pdb.set_trace()

        # calculate process emissions
        # target-sector	target-country-iso3	Y_2019	output_kUSD	EF_ktCO2_per_kUSD
        process_emissions = self.ALL_PROCESS_EMISSIONS[['target-sector','target-country-iso3','EF_ktCO2_per_kUSD']].copy()
        process_emissions['target-sector'] = process_emissions['target-sector'].astype(str)
        process_emissions = process_emissions.rename(columns={'target-sector':'PROD_COMM','target-country-iso3':'REG_imp'})

        default_process_emissions = process_emissions[process_emissions['REG_imp']=='DEFAULT'].copy()
        default_process_emissions = default_process_emissions.rename(columns={'EF_ktCO2_per_kUSD':'def_EF_ktCO2_per_kUSD'})

        # DEFAULT values are need to be added for missing emission rates
        process_emissions = process_emissions.merge(default_process_emissions.drop(columns=['REG_imp']), how='left', on=['PROD_COMM'])
        sel = np.isnan(process_emissions['EF_ktCO2_per_kUSD'])
        process_emissions.loc[sel, 'EF_ktCO2_per_kUSD'] = process_emissions.loc[sel, 'def_EF_ktCO2_per_kUSD']
        process_emissions = process_emissions.drop(columns=['def_EF_ktCO2_per_kUSD'])
        del default_process_emissions 
        
        # * TARGET AND ORIGIN is twisted here, bc process emissions are applied not on the incoming, but on the outgoing flow
        process_emissions = process_emissions.rename(columns={'REG_imp':'REG_exp','PROD_COMM':'TRAD_COMM'})
        process_emissions = process_emissions[process_emissions['REG_exp']==country].copy()
        process_emissions = process_emissions.merge(mrio, how='left', on=['REG_exp','TRAD_COMM'])
        process_emissions = process_emissions[~process_emissions['z_bp'].isna()]

        # kUSD * ktco2/kUSD -> ktco2 * 1000
        # PROCESS EMISSION REG_exp TRAD_COMM REG_imp PROD_COMM
        process_emissions['PROCESS_EMISSION'] = process_emissions['z_bp'] * process_emissions['EF_ktCO2_per_kUSD'] * 1000
        process_emissions = process_emissions[['REG_imp','PROD_COMM','REG_exp','TRAD_COMM','PROCESS_EMISSION']].astype({'PROD_COMM':'str','TRAD_COMM':'str'})

        emission_cost =  mrio[['REG_imp','PROD_COMM','REG_exp','TRAD_COMM']]\
            .merge(emissions.rename(columns={'target-country-iso3':'REG_imp','target-sector':'PROD_COMM', 'origin-country-iso3':'REG_exp','origin-sector':'TRAD_COMM'}), how='left')\
            .merge(carbon_tax_rate, how='left', on=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])\
            .merge(process_emissions, how='left', on=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])

        # import pdb; pdb.set_trace()        
        emission_cost = emission_cost.fillna(0)

        emission_cost['emission_cost'] = (emission_cost['POLLUTANT_VALUE'] + emission_cost['PROCESS_EMISSION']) * emission_cost['ctax'] # POLLUTANT_VALUE in tCO2, ctax in USD/tCO2
        emission_cost = emission_cost[~emission_cost['emission_cost'].isna()]
        emission_cost = emission_cost[['REG_imp','PROD_COMM','REG_exp','TRAD_COMM','POLLUTANT_VALUE','PROCESS_EMISSION','ctax','emission_cost']].copy()

        # calculate base monetary value of flow to get tax incidence in %
        # merge to emission cost
        tax_incidence = emission_cost.merge(mrio, how='left', on=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        # [delta_tax] -> percentages as in 10 is 10% -> 0.1

        # z_bp is in kUSD; emission cost is USD
        tax_incidence['delta_tax'] = (tax_incidence['emission_cost'] / 1000) / tax_incidence['z_bp'] * 100
        tax_incidence = tax_incidence[~tax_incidence['delta_tax'].isna()]
        tax_incidence = tax_incidence[tax_incidence['delta_tax']!=0]

        return tax_incidence

    def calculate_tax_incidence(self):

        # do for countries with carbon tax
        carbon_tax_countries = self.carbon_tax_countries
        if len(carbon_tax_countries) == 0:
            return pd.DataFrame(columns=['REG_imp','PROD_COMM','REG_exp','TRAD_COMM','delta_tax','z_bp','emission_cost','POLLUTANT_VALUE'])
        tax_incidence_all = None
        
        print("Calculating tax incidence... Parallel started.")
        # with alive_bar(len(tax_rate['REG_imp'].unique()), title="Generating carbon tax files...") as bar:

        # non-parallel for debugging
        # for c in carbon_tax_countries:
        #     self.tax_incidence_loop(c)
        
        futures_ = [] 
        with futures.ThreadPoolExecutor() as executor:
            for c in carbon_tax_countries:
                futures_.append(executor.submit(self.tax_incidence_loop, c))
        
            tmp_df = []
            with tqdm(total=len(futures_)) as progress:
                for f in futures.as_completed(futures_):
                    progress.update()
                    tmp_df.append(f.result())
            tax_incidence_all = pd.concat(tmp_df)

            # results = list(tqdm(executor.map(self.tax_incidence_loop, carbon_tax_countries), 
                    #   total=len(carbon_tax_countries)))
        print("Completed.")

        # import pdb; pdb.set_trace()    
        # del results

        # with alive_bar(len(carbon_tax_countries), title="Processing carbon tax incidence...") as bar:
            # for country in carbon_tax_countries:
                

                # tax_incidence_all = tax_incidence if tax_incidence_all is None else pd.concat([tax_incidence_all, tax_incidence])
                # self.temp.save_to_pickle(tax_incidence, "{}_tax_incidence".format(country))
                # self.temp.write_to_csv(tax_incidence, "{}_tax_incidence".format(country))

                # bar()
        tax_incidence_all = tax_incidence_all[['REG_imp','PROD_COMM','REG_exp','TRAD_COMM','delta_tax','z_bp','emission_cost','POLLUTANT_VALUE']]
        tax_incidence_all = tax_incidence_all.groupby(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM']).agg({'delta_tax':'sum', 'z_bp':'mean', 'emission_cost':'sum','POLLUTANT_VALUE':'mean'}).reset_index()
        self.temp.write_to_csv(tax_incidence_all, 'tax_incidence_all')

        return tax_incidence_all
    
    def MRIO_mat_to_df(self, MRIO):
        # MRIO is 19680 x 19680 matrix, this is 120x164, 120x164   

        # 1. put into dataframe
        mrio = pd.DataFrame(MRIO).reset_index()

        # now we have 
        # columns: index [sec1-reg1 = 0] [sec2-reg1 = 1] ... [sec120 - reg164 = 19680]
        # rows: 1 2 3 ... 19680

        # 2. melt
        mrio = pd.melt(mrio, id_vars=['index'])
        # now it's
        # columns: index[==row-index] variable[==column-index] value
        # rows: 1 2 3 ... 19680

        # 3. reindex
        mrio['origin-country'] = np.floor(mrio['index'] / 120)
        mrio['origin-sector'] = mrio['index'] % 120
        mrio['target-country'] = np.floor(mrio['variable'] / 120)
        mrio['target-sector'] = mrio['variable'] % 120

        # 4. merge country-iso
        mrio = self.attach_iso3(mrio, self.REGION)
        
        return mrio
    
    def attach_iso3(df, regions):
        """ 
        Attaches ISO3 codes from the `regions` input to the dataframe
        `origin-country` and `target-country` have to be present in the dataframe
        """
        df = df.merge(regions, how='left', left_on=['target-country'], right_on=['Lfd_Nr']).rename(columns={'Region_acronyms':'target-country-iso3'})\
            .drop(columns=['Region_names','Lfd_Nr'])
        df = df.merge(regions, how='left', left_on=['origin-country'], right_on=['Lfd_Nr']).rename(columns={'Region_acronyms':'origin-country-iso3'})\
            .drop(columns=['Region_names','Lfd_Nr'])
        return df
    
    def build_emission_matrix(self, pollutants_df, pollutant_fraction):
        pollutants_df = pollutants_df[pollutants_df['POLLUTANT_FRACTION']==pollutant_fraction].copy()
        pollutants_df = pollutants_df[["target-country-iso3","origin-country-iso3","target-sector","origin-sector","POLLUTANT_VALUE"]].copy()
        pollutants_df = pollutants_df[~pollutants_df['target-sector'].str.contains('FD')].copy()
        pollutants_df['target-sector'] = pollutants_df['target-sector'].astype('int32')
        pollutants_df['origin-sector'] = pollutants_df['origin-sector'].astype('int32')
        pollutants_df = pollutants_df.groupby(['origin-country-iso3','target-country-iso3','origin-sector','target-sector']).agg({'POLLUTANT_VALUE':'sum'}).reset_index()
        pollutants_df['row_index'] = tuple(zip(pollutants_df['origin-country-iso3'], pollutants_df['origin-sector']))
        pollutants_df['col_index'] = tuple(zip(pollutants_df['target-country-iso3'], pollutants_df['target-sector']))
        
        pollutants_df = pollutants_df.set_index(['row_index','col_index'])['POLLUTANT_VALUE'].unstack('col_index').fillna(0)
        p_temp = pd.DataFrame(np.zeros((self.DIMS,self.DIMS)), index=self.A_id, columns=self.A_id)
        p_temp.loc[pollutants_df.index, pollutants_df.columns] = pollutants_df.values

        POLLUTANTS_BASE = p_temp.to_numpy()
        
        return POLLUTANTS_BASE
        
    def delta_emissions(self, deltaQ, MRIO_current, MRIO_initial, q_base):
        """
        Function to calculate delta emissions given a 19680 (120*164) vector of output change across the MRIO and
        current MRIO state (A_trade).
        """

        # both MRIO is 19680 x 19680 matrix, this is 120x164, 120x164
        # deltaQ is singel 19680

        # create all pollutants matrix
        # ! ONLY CO2 for now
        all_pollutants = self.ALL_POLLUTANTS

        # ! replace inf with 0.0, th NO new sectors
        current = MRIO_current * (deltaQ + q_base)
        initial_base = MRIO_initial * q_base
        step1 = np.nan_to_num(np.divide(current, initial_base) - 1)
        del current
        del initial_base
        gc.collect()
        # print('step1')
        
        emission_matrix = self.build_emission_matrix(self.ALL_POLLUTANTS, 'CO2')
        step2 = np.multiply(step1, emission_matrix)
        del emission_matrix
        del step1
        gc.collect()

        dEmissions = step2.sum(axis=0)
        # supposed to be a 19680 vector

        # now process it into DF
        df = pd.DataFrame({
            'dEmissions': dEmissions,
            'dQ': deltaQ,
            'q_base': q_base 
            }).reset_index()
        df['target-sector'] = df['index'] % 120 + 1
        df['target-country'] = np.floor(df['index'] / 120) + 1

        # Lfd_Nr	Region_acronyms	Region_names
        df = df.merge(self.REGION.rename(columns={'Lfd_Nr':'target-country'}), how='left', on='target-country')
        df = df.rename(columns={'Region_acronyms':'target-country-iso3'}).drop(columns=['Region_names'])
        # df now is columns: target_sector target-country-iso3 deltaPollutant dQ

        # merge with POLLUTANTS
        df['target-sector'] = df['target-sector'].astype(str)
        # ! CO2 for now
        # import pdb; pdb.set_trace()
        all_pollutants = self.ALL_POLLUTANTS.query("POLLUTANT_FRACTION == 'CO2'").copy()
        all_pollutants['target-sector'] = all_pollutants['target-sector'].astype(str)
        all_pollutants = all_pollutants.groupby(['target-country-iso3','target-sector']).agg({'POLLUTANT_VALUE':'sum'}).reset_index()

        df = df.merge(all_pollutants, how='left', on=['target-country-iso3','target-sector'])
        df['deltaPollutant_nostructuralchange'] = (df['dQ'] / df['q_base']) * df['POLLUTANT_VALUE']
        df['deltaPollutant'] = df['dEmissions']
        df['qPollutant'] = df['POLLUTANT_VALUE']

        # merge with PROCESS EMISSIONS
        all_process_emissions = self.ALL_PROCESS_EMISSIONS
        all_process_emissions['target-sector'] = all_process_emissions['target-sector'].astype(str)
        df = df.merge(all_process_emissions, 
                      how='left', on=['target-country-iso3','target-sector'])
        # originally in tonnes (Y_2019) to have the same unit as POLLUTANTS multiply
        df['deltaProcess'] = (df['dQ'] / df['q_base']) * df['Y_2019'] * 1000
        df['Y_2019'] = df['Y_2019'] * 1000
        df = df.rename(columns={'Y_2019':'qProcess'})

        df = df.groupby(['target-country-iso3','target-sector']).agg({'deltaPollutant':'sum', 'qPollutant':'sum',
                                                                                           'deltaProcess':'sum', 'qProcess':'sum', 
                                                                                           'deltaPollutant_nostructuralchange':'sum'})\
        .reset_index()

        ret_ = pd.concat([df])

        return ret_