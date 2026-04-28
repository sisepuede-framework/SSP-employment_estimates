# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 14:23:57 2024

@author: xinru
"""

import pandas as pd

scenario = [
            "mitigation_2030_cprice", "mitigation_2050_cprice",
            "mitigation_2030_cprice_rr", "mitigation_2050_cprice_rr",
            # "mitigation_2030", "mitigation_2050", 
            # "adaptation_2030_tax", "adaptation_2050_tax",
            # "climate_2030", "climate_2050", 
            # "coal_2030", "coal_2050", 
            # "coal+copper_2030", "coal+copper_2050"
            ]

file_name = [
              "Results_MNG_Mitigation_2030_cprice.xlsx", "Results_MNG_Mitigation_2050_cprice.xlsx",
              "Results_MNG_Mitigation_2030_cprice_rr.xlsx","Results_MNG_Mitigation_2050_cprice_rr.xlsx",
             # "Results_MNG_mitigation_2030_coeff.xlsx", "Results_MNG_mitigation_2050_coeff.xlsx",
             # "Results_MNG_adaptation_2030_tax_coeff.xlsx","Results_MNG_adaptation_2050_tax_coeff.xlsx",
             # "Results_MNG_climate_2030_coeff.xlsx","Results_MNG_climate_2050_coeff.xlsx",
             # "Results_MNG_coal_2030_coeff.xlsx","Results_MNG_coal_2050_coeff.xlsx",
             # "Results_MNG_coal+copper_2030_coeff.xlsx","Results_MNG_coal+copper_2050_coeff.xlsx"
             ]

path = "D:\WB\MINDSET_module-main\GLORIA_results\\"

coefficient = "D:\WB\MINDSET_module-main\GLORIA_template\Employment\\Empl_coefficient.csv"
output_path = "D:\WB\MINDSET_module-main\GLORIA_results\Employment change\\"

Region = 'Mongolia' # Update region name

# %%
if __name__ == "__main__":
    
    # Read in output-employment coefficients for region of interest
    coeff = pd.read_csv(coefficient, header=1, index_col=1)[Region]
    
    va = pd.read_pickle("D:\\WB\\GLORIA_db\\v57\\2019\\VA.pkl")#
    va_mng = va[va['REG_imp']=='MNG']['Compensation of employees']
    
    for s, f in zip(scenario, file_name):
        q_base = pd.read_excel(path+f, 'output').loc[:, ['Sector', 'q_base']]
        q_base = q_base.set_index(['Sector'])
        emp_base = pd.read_excel(path+f, 'employment').loc[:, ['Sector', 'empl_base']]
        emp_base = emp_base.set_index(['Sector'])
    
        # Get output changes 
        output_coeff = pd.read_excel(path+f, 'output').loc[:, ['Sector', 'dq_total']]
        output_coeff = output_coeff.set_index(['Sector'])
    
        # Calculate implied employment and wage effects
        
        # multiply output change with sectoral output-employment coefficients
        multiplier = coeff.to_frame().values * (emp_base.values/q_base.values)
        employment_change = output_coeff * multiplier
        employment_change.rename(columns={'dq_total':'dempl_total'}, inplace=True)
        employment_change['emp_base'] = emp_base
        # wage base
        employment_change['wage_base'] = va_mng.values
        # wage change
        multiplier_2 = (1-coeff).to_frame().values * (emp_base.values/q_base.values)
        employment_change['dwage_total'] = output_coeff * multiplier_2
        # calculate % changes 
        employment_change['emp_effect (%)'] = employment_change['dempl_total'] / employment_change['emp_base'] * 100
        employment_change['wage_effect (%)'] = employment_change['dwage_total'] / employment_change['emp_base'] * 100
        employment_change.loc['total_impact'] = employment_change.sum()
        employment_change.loc['total_impact', 'emp_effect (%)'] = employment_change['dempl_total'].sum() / employment_change['emp_base'].sum() * 100
        employment_change.loc['total_impact', 'wage_effect (%)'] = employment_change['dwage_total'].sum() / employment_change['emp_base'].sum() * 100
    
        employment_change.to_csv(output_path + s + "_emp_cal.csv")
    
    
    

        