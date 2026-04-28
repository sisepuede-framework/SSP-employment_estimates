
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 10:37:41 2024

@author: wb619071
"""

import pickle as pkl
import pandas as pd
import sys
import os

print(os.getcwd())

if len(sys.argv) > 1:
    grouping_file = sys.argv[1]
else:
    grouping_file = "GLORIA_template\\Country_groupings\\R_grouping.xlsx"

reg_conv = pd.read_excel(grouping_file, sheet_name="groups")
reg_conv_mat = reg_conv[['Lfd_Nr','Lfd_Nr_agg']].copy()
reg_conv = reg_conv[['Lfd_Nr','Region_acronyms','Agg_region','Agg_region_name','Lfd_Nr_agg']].copy()
reg_conv = reg_conv.sort_values(by=['Lfd_Nr_agg'])

#%%

## First start with pickle files

PATH_PICKLE = "GLORIA_db\\v57\\2019\\parsed_db\\"

# single arrays
# cid.pkl
with open("{}cid.pkl".format(PATH_PICKLE), "wb") as file:
    pkl.dump(list(reg_conv['Agg_region'].unique()), file)
    
# cou.pkl
with open("{}cou.pkl".format(PATH_PICKLE), "wb") as file:
    pkl.dump(list(reg_conv['Agg_region_name'].unique()), file)
    
#%%

# single dimension dfs
# FCF, GOV, HH, NPISH, other_FD, INV

value_name = {
    'FCF': 'VDFA',
    'GOV': 'VIGA',
    'HH': 'VIPA',
    'INV': 'INV',
    'NPISH': 'NPISH',
    'other_FD': 'otherFD'
    }

# reg-imp reg-exp trad-comm [these are in index]

reg_conv_use = reg_conv[['Region_acronyms','Agg_region']].copy()

for key, VALUE_COL in value_name.items():

    print("{}{}.pkl".format(PATH_PICKLE, key))
    data = pd.read_pickle("{}{}.pkl".format(PATH_PICKLE, key))
    
    # both reg-imp and reg-exp
    data = data.reset_index()
    data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_imp','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'REG_imp'})
    
    data = data.merge(reg_conv_use, how='left', left_on='REG_exp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_exp','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'REG_exp'})
    
    data = data.groupby(['REG_imp','REG_exp','TRAD_COMM']).agg('sum').reset_index()
    data = data.set_index(['REG_imp','REG_exp','TRAD_COMM'])
    
    with open("{}{}.pkl".format(PATH_PICKLE, key), "wb") as file:
        pkl.dump(data, file)


#%%

# other dfs, only reg-imp and prod-comm

dfs = ['VA','labor_data','empl_data']

for key in dfs:

    print("{}{}.pkl".format(PATH_PICKLE, key))
    data = pd.read_pickle("{}{}.pkl".format(PATH_PICKLE, key))
    
    data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
    data = data.drop(columns=['REG_imp','Region_acronyms'])
    data = data.rename(columns={'Agg_region':'REG_imp'})
    
    data = data.groupby(['REG_imp','PROD_COMM']).agg('sum').reset_index()
        
    with open("{}{}.pkl".format(PATH_PICKLE, key), "wb") as file:
        pkl.dump(data, file)

#%%

# ind-sparse - MRIO table
key = "IND_sparse"

print("{}{}.pkl".format(PATH_PICKLE, key))
data = pd.read_pickle("{}{}.pkl".format(PATH_PICKLE, key))

data = data.reset_index()

output = data[['REG_imp','PROD_COMM','output']]
output = output.drop_duplicates()
output = output.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
output = output.drop(columns=['REG_imp','Region_acronyms'])
output = output.rename(columns={'Agg_region':'REG_imp'})
output = output.groupby(['REG_imp','PROD_COMM']).agg('sum').reset_index()

# a_bp == z_bp / output
# a_tech == a_bp | excluding REG_exp

data = data.merge(reg_conv_use, how='left', left_on='REG_imp', right_on='Region_acronyms')
data = data.drop(columns=['REG_imp','Region_acronyms'])
data = data.rename(columns={'Agg_region':'REG_imp'})

data = data.merge(reg_conv_use, how='left', left_on='REG_exp', right_on='Region_acronyms')
data = data.drop(columns=['REG_exp','Region_acronyms'])
data = data.rename(columns={'Agg_region':'REG_exp'})

data = data.groupby(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM']).agg({'z_bp':'sum'}).reset_index()

# ! NEED to recalculate a_bp a_tech output

data = data.merge(output, how='left', on=['REG_imp','PROD_COMM'])
data['a_bp'] = data['z_bp'] / data['output']
data['a_tech'] = data.groupby(['REG_imp','PROD_COMM','TRAD_COMM'])['a_bp'].transform('sum')
data = data.set_index(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])

with open("{}{}.pkl".format(PATH_PICKLE, key), "wb") as file:
    pkl.dump(data, file)

#%%

# now the template files

PATH_TEMPLATE = "GLORIA_template\\"

agg_groups = pd.read_excel(grouping_file, sheet_name="aggregates")

# write 'Countries_inc_cat.xlsx'
# Country_No	Country_Code	GLORIA_Country	USDA_inc_cat
df = agg_groups[['Lfd_Nr_agg','Agg_region','Agg_region_name','USDA_inc_cat']].copy()
df.columns = ['Country_No','Country_Code','GLORIA_Country','USDA_inc_cat']

df.to_excel("{}Elasticities\\Countries_inc_cat.xlsx".format(PATH_TEMPLATE), sheet_name='Countries', index=False)
print("{}Elasticities\\Countries_inc_cat.xlsx".format(PATH_TEMPLATE))

#%%

# write 'FileID.xlsx' (two sheets)
# CrossPrices ---> Original Code	Country Name	Code	Filename
# OwnPrices ---> Original Code	Country Name	Code	Filename

# CrossPrices

df = agg_groups[['Agg_region','Agg_region_name','Energy_CrossPrice_code','Energy_CrossPrice_file']].copy()
df.columns = ['Original Code', 'Country Name', 'Code', 'Filename']

df.to_excel("{}Elasticities\\FileID_CrossPrice.xlsx".format(PATH_TEMPLATE), sheet_name='CrossPrices', index=False)
print("{}Elasticities\\FileID_CrossPrice.xlsx".format(PATH_TEMPLATE))

# OwnPrices

df = agg_groups[['Agg_region','Agg_region_name','Energy_OwnPrice_code','Energy_OwnPrice_file']].copy()
df.columns = ['Original Code', 'Country Name', 'Code', 'Filename']

df.to_excel("{}Elasticities\\FileID_OwnPrice.xlsx".format(PATH_TEMPLATE), sheet_name='OwnPrices', index=False)
print("{}Elasticities\\FileID_OwnPrice.xlsx".format(PATH_TEMPLATE))

#%%

# Employment is based on USDA to GLORIA
# Investment is based on USDA to GLORIA
# compile USDA to GLORIA
# Country_No	Country_Code	GLORIA_Country	USDA_Country

df = agg_groups[['Lfd_Nr_agg','Agg_region','Agg_region_name','USDA_Country','Employment_country','Investment_country','Beta_C','Beta_C_Agg']].copy()
df.columns = ['Country_No','Country_Code','GLORIA_Country', 'USDA_Country','Employment_country','Investment_country','Beta_C','Beta_C_Agg']

df.to_excel("{}modelinputdata\\Countries_USDAtoGLORIA.xlsx".format(PATH_TEMPLATE), sheet_name='Countries', index=False)
print("{}modelinputdata\\Countries_USDAtoGLORIA.xlsx".format(PATH_TEMPLATE))

#%%

# Energy-emission data

# ______________________________________________________

data = pd.read_csv("{}Energy_emissions\\ALL_POLLUTANTS.csv".format(PATH_TEMPLATE))
data = data[data['POLLUTANT_FRACTION']=='CO2'].copy()

data = data.merge(reg_conv_use, how='left', left_on='target-country-iso3', right_on='Region_acronyms')
data = data.drop(columns=['target-country-iso3','Region_acronyms'])
data = data.rename(columns={'Agg_region':'target-country-iso3'})

data = data.merge(reg_conv_use, how='left', left_on='origin-country-iso3', right_on='Region_acronyms')
data = data.drop(columns=['origin-country-iso3','Region_acronyms'])
data = data.rename(columns={'Agg_region':'origin-country-iso3'})

data = data.groupby(['target-country-iso3','origin-country-iso3','target-sector','origin-sector','POLLUTANT_FRACTION']).agg('sum').reset_index()
data.to_csv("{}Energy_emissions\\ALL_POLLUTANTS.csv".format(PATH_TEMPLATE), index=False)
print("{}Energy_emissions\\ALL_POLLUTANTS.csv".format(PATH_TEMPLATE))

# ____________________________________________________

data = pd.read_csv("{}Energy_emissions\\ALL_PROCESS_EMISSIONS.csv".format(PATH_TEMPLATE)).pipe(lambda d: d[d['target-country-iso3'] != "DEFAULT"])
data = data.merge(reg_conv_use, how='left', left_on='target-country-iso3', right_on='Region_acronyms')
data = data[~data['Agg_region'].isna()]
data = data.drop(columns=['target-country-iso3','Region_acronyms'])
data = data.rename(columns={'Agg_region':'target-country-iso3'})
data = data.groupby(['target-country-iso3','target-sector']).agg('sum').reset_index()
data['EF_ktCO2_per_kUSD'] = data['Y_2019'] / data['output_kUSD']


data.to_csv("{}Energy_emissions\\ALL_PROCESS_EMISSIONS.csv".format(PATH_TEMPLATE), index=False)
print("{}Energy_emissions\\ALL_PROCESS_EMISSIONS.csv".format(PATH_TEMPLATE))

#%%

# VARIABLES list file
# we rewrite the R sheet NOT touch the others
# Lfd_Nr	Region_acronyms	Region_names

df = agg_groups[['Lfd_Nr_agg','Agg_region','Agg_region_name']].copy()
df.columns = ['Lfd_Nr','Region_acronyms','Region_names']

with pd.ExcelWriter('{}Variables\\Variable_list_MINDSET.xlsx'.format(PATH_TEMPLATE),engine = "openpyxl",  mode='a') as writer:
    workBook = writer.book
    try:
        workBook.remove(workBook['R'])
    except:
        print("worksheet doesn't exist")
    finally:
        df.to_excel(writer, sheet_name='R', index=False)
print('{}Variables\\Variable_list_MINDSET.xlsx'.format(PATH_TEMPLATE))
