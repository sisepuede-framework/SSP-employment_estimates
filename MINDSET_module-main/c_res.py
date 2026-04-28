# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 23:24:53 2023

@author: meime
"""
# -*- coding: utf-8 -*-
"""
=========================================
collect_res.py
=========================================
Power generation shares FTT module.

Functions included:
    - shares
        Calculate market shares

"""

# Standard library imports
from math import sqrt
import os
import copy
import sys
import warnings

# Third party imports
import pandas as pd
import numpy as np
from numba import njit
import pickle
#import mindset_ftt_year_test
#A=data['MEWG'][:,:,0]
# Replace 'your_file_path.pkl' with the actual path to your pickle file
os.chdir("C:\\Users\\meime\\Documents\\WB_CPAT_model\\MINDSET_modules_v1")
from mindset_ftt_year_test import MINDSETRUN_YEAR 

file_path = "C:\\Users\\meime\\Documents\\WB_CPAT_model\\FTT_StandAlone_v0.8-main_copy_mindset\\MEWG0.pkl"
# Open the pickle file for reading (rb: read binary mode)
with open(file_path, 'rb') as file:
    # Load the data from the pickle file
    MEWG0 = pickle.load(file)
# with open('MEWG0.pkl', 'rb') as file:
#     MEWG0 = pickle.load(file)

    
def c_res(A, year, scenario):
    print("This is which year: " + str(year))
    os.chdir("C:\\Users\\meime\\Documents\\WB_CPAT_model\\IEA_data")
    conc_ftt_b = pd.read_excel("FTT-IEA.xlsx", "Sheet1")
    coun_ftt_gl = pd.read_excel("FTT-IEA.xlsx", "country_fttglo")
    conc_ftt_array = conc_ftt_b.values
    conc_ftt_t = np.transpose(conc_ftt_array[1:11, 1:25])
    
    MEWG_0 = np.zeros((24, 71))
    MEWG1 = np.zeros((71, 24))
    MEWG1_t = np.zeros((71, 24))
    
    #write down what is A
    for k in range(0, 71):
        MEWG_0[0:25, k] = MEWG0[k, 0:25, 0, year - 2010]
    MEWG_0_t = np.transpose(MEWG_0)
    #scenario = "S1"
    
    if scenario == "S1" and year>2023:
        # Convert the processed_df DataFrame to a dictionary
        for k in range(0, 71):
            MEWG1[k,0:25] = A[k, 0:25, 0]
        #MEWG1_t = np.transpose(MEWG1)
        MEWG1_t = MEWG1
        mewg_conc = {}
        mewg_conc1={}#
        diff_FTT_MEWG = {}
        t_diff_FTT_MEWG={}
        #print(MEWG1_t)
        mewg_conc[year] = np.dot(MEWG_0_t[:, 0:25], conc_ftt_t[0:25, :10])
        mewg_conc1[year]=np.dot(MEWG1_t[0:71, 0:25], conc_ftt_t[0:25, :10])
        # print(MEWG1_t.shape)
        # print(conc_ftt_t.shape)
 
        denominator = mewg_conc[year]
        numerator = mewg_conc[year]
        differences = np.zeros_like(denominator)
        non_zero_denominator = denominator != 0
        differences[non_zero_denominator] = (numerator[non_zero_denominator] - denominator[non_zero_denominator]) / denominator[non_zero_denominator]
        diff_FTT_MEWG[year] = differences
        t_diff_FTT_MEWG[year]=np.transpose(diff_FTT_MEWG[year])
        coun_ftt_gl_array = coun_ftt_gl.values
        sliced_coun_ftt_gl_array = coun_ftt_gl_array[0:71, 1:166]
        # print(diff_FTT_MEWG[year].shape)
        # print(sliced_coun_ftt_gl_array.shape)
        ftt_mewg_gl=np.dot(t_diff_FTT_MEWG[year], sliced_coun_ftt_gl_array)
        
        ieause_df=pd.read_excel("C:\\Users\\meime\\Documents\\WB_CPAT_model\\GLORIA_documentation\\ieause.xlsx", "ieause_df")
        ieause_df = ieause_df.drop(ieause_df.columns[1], axis=1)
        ieause_n=ieause_df.to_numpy()
        rows_ieauseftt = 6068 #6068 = 164*37 
        cols_ieauseftt = 10 #12 energy sources
        ieauseftt = np.zeros((rows_ieauseftt, cols_ieauseftt))
        
        for k in range(0, 164):
              for i in range(0, 10):
                  #input into electricity from different energy resources
                  ieauseftt[37*k+2, i] = ieause_n[37*k+2, i]*(ftt_mewg_gl[i,k])
        
        d_change, output_mindset=cal_delta_tech_coef_0(ieauseftt,ieause_n,"BRA",25,year)
        output_mind = f'OutputMindset_{year}.pkl'
        output_mindset.to_pickle(output_mind)
    else:
        d_change=1
        output_mindset=1
        
    return d_change, output_mindset
            
    

def cal_delta_tech_coef_0(ieauseftt,ieause_n,tax_cou,tax_cou_num,year):
      reg_imp_data = [tax_cou] * (1 * 8)
      prod_comm_data = np.repeat([93], 8)
      trad_comm_data =  np.repeat([24, 25, 26, 27, 62, 63, 93, 94], 1)
      data = {
                 "REG_imp": reg_imp_data,
                 "TRAD_COMM": trad_comm_data,
                 "PROD_COMM": prod_comm_data
            }
        
      ftt_p_df = pd.DataFrame(data)
#         #in case oil is used 
      oil_techno = ieauseftt[37*tax_cou_num+2, 3]
      oil_demand = ieause_n[37*tax_cou_num+2, 3]
      if oil_demand != 0:
             ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 26, "delta_tech_coef"] = 1+oil_techno / oil_demand
      else:
             ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 26, "delta_tech_coef"] = 1


      #         #count positions here for below [29 24 25 26(3) 27 93(5) 21 95 62(8) 93 63(10) ]
      secs=[2,0,1,8,9,5,10,7,3,5,4]  
      #         #try coal first
      #         #calculate the change in a coefficient in each case - the power sector
      ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 24, "delta_tech_coef"] = 1+ieauseftt[37*tax_cou_num+2,1]/ieause_n[37*tax_cou_num+2, 1]
      ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 25, "delta_tech_coef"] = 1+ieauseftt[37*tax_cou_num+2,2]/ieause_n[37*tax_cou_num+2, 2]
#         # #ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 26, "delta_tech_coef"] = (ieauseftt[37*tax_cou_num+2,3]+ieauseftt[37*tax_cou_num+2,10])/(ieause_n[37*tax_cou_num+2, 3]+ieause_n[37*tax_cou_num+2, 10]) #oil
      #ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 26, "delta_tech_coef"] = ieauseftt[37*tax_cou_num+2,3]/(ieause_n[37*tax_cou_num+2, 3]) #oil
      ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 27, "delta_tech_coef"] = 1+ieauseftt[37*tax_cou_num+2,4]/ieause_n[37*tax_cou_num+2, 4] #gas
      ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 62, "delta_tech_coef"] = 1
      ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 63, "delta_tech_coef"] = 1+(ieauseftt[37*tax_cou_num+2,3]+ieauseftt[37*tax_cou_num+2,9])/(ieause_n[37*tax_cou_num+2, 3]+ieause_n[37*tax_cou_num+2, 9]) #oil
#         # ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 63, "delta_tech_coef"] = ieauseftt[37*tax_cou_num+2,3]/(ieause_n[37*tax_cou_num+2, 3]) #oil
      ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 93, "delta_tech_coef"] = 1
      ftt_p_df.loc[ftt_p_df["TRAD_COMM"] == 94, "delta_tech_coef"] = ieauseftt[37*tax_cou_num+2,4]/ieause_n[37*tax_cou_num+2, 4] #gas
      
    
      #these results need to be sent to the MINDSET code 2023
      mindsetrun=MINDSETRUN_YEAR()
      ftt_p_out,result_out1=mindsetrun.run_mindset_ftt(ftt_p_df,year)
      # if year<2030:
      #     ftt_p_out=mindsetrun.run_mindset_ftt(ftt_p_df,year)
      # else:
      #     ftt_p_out=mindsetrun.run_mindset_ftt_1(ftt_p_df,year)
      #     print("The model is stopped here")
      #     sys.exit()
      print("print here",ftt_p_out)    
      return ftt_p_out,result_out1
