# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 18:42:54 2023


Link for export and import of missing countries from IMF: Direcion of Trade

@author: xinru
"""

import pandas as pd
import os
import numpy as np
import scipy.io
import time
import math
import copy
from Functions import fillmat
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import zipfile

# GLobal variables, update as necessary in future runs
icou = 164  # Number of Gloria countries
isec = 120  # Number of Gloria sectors
Start_y = 1990 # Start year of the histrical data
End_y = 2050  # Last year of projection
WDI_End_y = 2022 # End year in WDI
WEO_End_y = 2028
base_y_gloria = 2019
GLORIA_End_y = 2021

# File paths
path_gloria = "D:\\WB\\GLORIA_db"
path_pkl = "D:\\WB\\GLORIA_db\\v57\\"
path_wdi = "D:\\WB\\Projections\\Economic\\Data\\Trade_WDI.xlsx"
path_weo = "D:\\WB\\Projections\\Economic\\Data\\Economic_outlook_WEO.xlsx"
path_imf_trade = "D:\\WB\\Projections\\Economic\\Data\\Direction_of_Trade_Statistics_DOTS.xlsx"
path_result = "D:\\WB\\Projections\\Economic\\Results\\Economic_proj.mat"
path_prox = "D:\\WB\\Projections\\Economic\\Converter\\proxy_mapping_trade.csv"
path_con = "D:\\WB\\Projections\\Economic\\Converter\\WDItoGloria_cou.csv" # WDItoGloria converter
path_cou = "D:\\WB\\Projections\\Economic\\Converter\\WITStoGloria_cou.xlsx"
path_imf_con = "D:\\WB\\Projections\\Economic\\Converter\\IMFtoGloria_cou.csv"
path_import = "D:\\WB\\Projections\\Economic\\Data\\WITS_import\\"
path_export = "D:\\WB\\Projections\\Economic\\Data\\WITS_export\\"
path_concordance = "D:\\WB\\Projections\\Economic\\Converter\\Concordance_S2_to_I2.xlsx"



# %%
if __name__ == "__main__":
    
    # 1. Read in raw data
    
    # Read in Gloria classifications
    os.chdir(path_gloria)
    year_gloria = list((range(Start_y, GLORIA_End_y+1)))
    years_wdi = list((range(Start_y, WDI_End_y+1)))
    years_full = list((range(Start_y, End_y+1)))
    years_proj = list((range(WDI_End_y+1, End_y+1)))
    # Read in lables
    sut_tbl = scipy.io.loadmat("GLORIA_MRIO_2019.mat")
    cid = sut_tbl["cid"]
    cid = [str(i[0]) for sub in cid for i in sub]
    sec = sut_tbl["sec"]
    sec = [str(i[0]) for sub in sec for i in sub]
    del sut_tbl

    # Read in GDP projections
    gdp = pd.DataFrame(scipy.io.loadmat(path_result)['GDP'], index=cid, columns=years_full)
    
    # Read in WDI to Gloria region converter
    wdi_glo_con = pd.read_csv(path_con, index_col=0)
    
    # Read in proxy mapping
    proxy_map = pd.read_csv(path_prox, index_col=0)

#%%    
    # 2. Read in WDI data
    wdi_data =pd.read_excel(path_wdi, 'Data', usecols="A, D, E:AK")
    ex_share = wdi_data[wdi_data['Series Name']=='Exports of goods and services (% of GDP)']
    im_share = wdi_data[wdi_data['Series Name']=='Imports of goods and services (% of GDP)']
    trade_share = {'export': ex_share.copy(), 'import': im_share.copy()}
    # Format data
    for t in trade_share:
        trade_share[t].drop(['Series Name'], axis=1, inplace=True)
        trade_share[t].set_index('Country Code', inplace=True)
        trade_share[t].columns = years_wdi
        trade_share[t].replace('..', np.nan, inplace=True)    
        trade_share[t] = fillmat.interpolate(trade_share[t].T).T
        # Fill missing years
        for row in trade_share[t].index:
            for col in trade_share[t].columns:
                if (col!=Start_y and np.isnan(trade_share[t].loc[row, col])):
                    trade_share[t].loc[row, col] = trade_share[t].loc[row, col-1]
            for col in trade_share[t].columns[::-1]:
                if (col!=WDI_End_y and np.isnan(trade_share[t].loc[row, col])):
                    trade_share[t].loc[row, col] = trade_share[t].loc[row, col+1]
        # trade_share[t].fillna(0, inplace=True)    
    
    # For GLORIA country that correspond to multiple WDI countries, use average shares
    share_wdi = {}
    for t in trade_share:
        share_wdi[t] = pd.DataFrame(0, index=cid, columns=years_wdi)
        for c in cid:
            try:
                if list(wdi_glo_con.index).count(c) > 1:
                    share_wdi[t].loc[c] = trade_share[t].loc[list(wdi_glo_con.loc[c, 'WDI'])].mean()
                else:
                    share_wdi[t].loc[c] = trade_share[t].loc[wdi_glo_con.loc[c, 'WDI']]
            except KeyError:
                pass
    
    # Get list of countries without data in WDI
    rows_with_nan = {}
    for t in share_wdi:
        rows_with_nan=([index for index, row in share_wdi[t].iterrows() if row.isnull().any()])
    
#%%    
    # 3. FIX: for countries without data in WDI, use trade and GDP data from IMF's database to estimate % of GDP
    
    # Trade data - units: million
    export_imf = pd.read_excel(path_imf_trade, 'Export', index_col=0, skipfooter=2)
    export_imf.index = rows_with_nan
    import_imf = pd.read_excel(path_imf_trade, 'Import', index_col=0, skipfooter=2)
    import_imf.index = rows_with_nan
    
    # Export and import data from IMF
    trade_imf = {'export': export_imf, 'import': import_imf}
    
    # GDP data - units: billion
    weo_outlook = pd.read_excel(path_weo, usecols="B, E, G, J:AV", index_col=0) 
    GDP_imf = weo_outlook[weo_outlook['Subject Descriptor'] == 'Gross domestic product, current prices']
    GDP_imf = GDP_imf[GDP_imf['Units'] == 'U.S. dollars']
    GDP_imf.drop(['Subject Descriptor', 'Units'], axis=1, inplace=True)
    GDP_imf *= 1000
    
    rows_with_nan_ = rows_with_nan.copy()
    rows_with_nan_.remove('PRK')
    gdp_miss = GDP_imf.loc[rows_with_nan_, years_wdi]
    
    # North Korea GDP is missing in IMF as well, read in from GLORIA directly
    va_data = {}
    for y in years_wdi:
        va_data[y] = pd.read_pickle(path_pkl + '{}\\VA.pkl'.format(y))
        # last column is tax/subsidy of products (exclude for gva, include for GDP)
        gdp_miss.loc['PRK', y] = va_data[y][va_data[y]['REG_imp']=='PRK'].iloc[:, 2:].sum(axis=1).sum()
    gdp_miss.loc['PRK'] /= 1000
    gdp_miss = gdp_miss.astype(float)
    
    # Replace estimated IMF trade shares to the missing WDI shares
    for t in share_wdi:
        for c in rows_with_nan:
            share_wdi[t].loc[c] = trade_imf[t].loc[c].values / gdp_miss.loc[c].values * 100
            
    # Fill missing years, use the nearest available year's shares to fill the missing years
    for t in trade_share:
        for row in rows_with_nan:
            for col in share_wdi[t].columns[::-1]:
                if (col>=WDI_End_y-1 and np.isnan(share_wdi[t].loc[row, col])):
                    share_wdi[t].loc[row, col] = share_wdi[t].loc[row, col-1]
                elif np.isnan(share_wdi[t].loc[row, col]):
                    share_wdi[t].loc[row, col] = share_wdi[t].loc[row, col+1]

#%% 
    # 4. Apply shares to processed GDP projections
    
    gdp_proj = pd.DataFrame(scipy.io.loadmat(path_result)['GDP'], index=cid, columns=years_full)
    
    # Calculate trade using trade shares
    trade = {}
    for t in trade_share:
        trade[t] = share_wdi[t] / 100 * gdp_proj
    
#%%
    # 5. Project forward using growth from IMF

    # Read in projected trade groth to 2028 from IMF
    ex_growth = weo_outlook[weo_outlook['Subject Descriptor'] == 'Volume of exports of goods and services']
    im_growth = weo_outlook[weo_outlook['Subject Descriptor'] == 'Volume of imports of goods and services']
    trade_growth = {'export': ex_growth.copy(), 'import': im_growth.copy()}
    for t in trade_growth:
        trade_growth[t].drop(['Subject Descriptor', 'Units'], axis=1, inplace=True)
        trade_growth[t].replace('--', np.nan, inplace=True)
        trade_growth[t] = trade_growth[t].loc[:, WDI_End_y:]
    
    # Get converter from IMF to Gloria regions
    imf_glo_con = pd.read_csv(path_imf_con, index_col=0)
    
    # For countries that correspond to multiple IMF countries, use average growth
    growth_proj = {}
    for t in trade_share:
        growth_proj[t] = pd.DataFrame(np.nan, index=cid, columns=trade_growth[t].columns)
        for c in cid:
            try:
                if list(imf_glo_con.index).count(c) > 1:
                    growth_proj[t].loc[c] = trade_growth[t].loc[list(imf_glo_con.loc[c, 'IMF'])].mean()
                else:
                    growth_proj[t].loc[c] = trade_growth[t].loc[imf_glo_con.loc[c, 'IMF']]
            except KeyError:
                pass
    
    # For countries without projected growth in IMF data, use growth from proxy countries
    for t in growth_proj:
        growth_proj[t].loc['DYE'] = 0
        for c in proxy_map.index:
            prox = proxy_map.loc[c, 'proxy_cou']
            for year in growth_proj[t].columns:
                if math.isnan(growth_proj[t].loc[c, year]):
                    growth_proj[t].loc[c, year] = growth_proj[t].loc[prox, year]
                    
    # Project forward growth rate by holding the last year of projection growth constant to 2050
    # Hold same growth forward as in 2028
    for t in growth_proj:                
        for year in list(range(WEO_End_y+1, End_y+1)):
            growth_proj[t][year] = growth_proj[t][year-1]
        
    # Method 1: hold growth from IMF forward
    # Apply growth rates to trade data up to the forecast year in IMF (2028)
    for t in trade:
        for year in list(range(WDI_End_y+1, End_y+1)):
            trade[t][year] = trade[t][year-1] *  (1+growth_proj[t][year]/100)
    
    # Method 2: use GDP growth rate
    trade_2 = {}
    for t in trade:
        trade_2[t] = pd.concat([trade[t].loc[:, :WDI_End_y], pd.DataFrame(np.nan, index=cid,
                                columns=list(range(WDI_End_y+1, End_y+1)))], axis=1)
        
        trade_2[t] = fillmat.fill_with_growth_rates(var_to_fill=trade_2[t].T,
                                                    var_to_get_growth=gdp.T).T
#%%
    '''
    # Compare trade from two methods        
    plt.ioff()
    # Plot comparison graphs (2015 price GDP vs OECD 2015 price)
    x = list(range(2018, End_y+1))
    
    p = PdfPages('D:\\WB\\Projections\\Economic\\Results\\Check\\Trade_comparison.pdf')
    for r in cid:
        fig, axs = plt.subplots(1, 1)
        y = trade['export'].loc[r, 2018:]
        z = trade_2['export'].loc[r, 2018:]
        w = trade['import'].loc[r, 2018:]
        s = trade_2['import'].loc[r, 2018:]
        axs.plot(x, y, label='export')
        axs.plot(x, z, linestyle='dashdot', label='export_2')
        axs.plot(x, w, label='import')
        axs.plot(x, s, linestyle='dashdot', label='import_2')
        fig.suptitle(r, fontsize=10)
        axs.legend(loc="lower right", fontsize="7")
        p.savefig(fig) 
    p.close()
    '''    
#%%
    # Read in data from WITS
    # Import    
    process_time = time.time()
    
    # Read in country mapping, and list of country to drop from WITS
    remove_cou = list(pd.read_excel(path_cou, 'cou_to_remove', usecols='A')['Cou_remove'])
    wits_gloria_con = pd.read_excel(path_cou, 'cou_mapping', index_col=0)
    
    with zipfile.ZipFile('D:\WB\Projections\Economic\Data\WITS_import.zip', 'r') as zip_file:
       file_list = zip_file.namelist()
    file_list.remove('[Content_Types].xml')
    
    # Get country code from file names
    wits_cou_import = [name[3:6] for name in file_list]
    wits_cou_import = list(dict.fromkeys(wits_cou_import))
    wits_cou_import = [i for i in wits_cou_import if i not in remove_cou]
    
    # Get year from file names
    data_year_import = {}
    sub_list = {}
    for c in wits_cou_import:
        sub_list[c] = [i for i in file_list if c in i]
        data_year_import[c] = [int(name[7:11]) for name in sub_list[c]]
    
    # Read in WID trade data by country and year
    import_in = {}
    for c in wits_cou_import:
        import_in[c] = {}
        for y in data_year_import[c]:
            with zipfile.ZipFile(path_import + 'S2_{}_{}_Import.zip'.format(c, y), 'r') as zip_file:
                file = zip_file.namelist()
                with zip_file.open(file[0]) as myZipCsv:
                    import_in[c][y] = pd.read_csv(myZipCsv, usecols=['ProductCode', 'TradeValue']) 
                    import_in[c][y]['ProductCode'] = import_in[c][y]['ProductCode'].astype(str)
                    import_in[c][y]['3_digit'] = import_in[c][y]['ProductCode'].str[:3]
                    import_in[c][y] = import_in[c][y].groupby(['3_digit'])['TradeValue'].sum()
          
    
    # Export             
    with zipfile.ZipFile('D:\WB\Projections\Economic\Data\WITS_export.zip', 'r') as zip_file:
       file_list = zip_file.namelist()
    file_list.remove('[Content_Types].xml')
    
    # Get country code from file names
    wits_cou_export = [name[3:6] for name in file_list]
    wits_cou_export = list(dict.fromkeys(wits_cou_export))
    wits_cou_export = [i for i in wits_cou_export if i not in remove_cou]
    # Get year from file names
    data_year_export = {}
    sub_list = {}
    for c in wits_cou_export:
        sub_list[c] = [i for i in file_list if c in i]
        data_year_export[c] = [int(name[7:11]) for name in sub_list[c]]
    export_in = {}
    for c in wits_cou_export:
        export_in[c] = {}
        for y in data_year_export[c]:
            with zipfile.ZipFile(path_export + 'S2_{}_{}_Export.zip'.format(c, y), 'r') as zip_file:
                file = zip_file.namelist()
                with zip_file.open(file[0]) as myZipCsv:
                    export_in[c][y] = pd.read_csv(myZipCsv, usecols=['ProductCode', 'TradeValue']) 
                    export_in[c][y]['ProductCode'] = export_in[c][y]['ProductCode'].astype(str)
                    export_in[c][y]['3_digit'] = export_in[c][y]['ProductCode'].str[:3]
                    export_in[c][y] = export_in[c][y].groupby(['3_digit'])['TradeValue'].sum()
    
    wits_trade = {'export': copy.deepcopy(export_in), 'import': copy.deepcopy(import_in)}
    
    del(export_in)
    del(import_in)
    print("--- Read data: %s seconds ---" % round(time.time() - process_time, 1))
    
#%%
    # Map WDI SITC Rev 2 sector to ISIC2
    # Note: HTI in export not in import; TCD in import not in export)
    sitc_isic = pd.read_excel(path_concordance, 'Concordance_S2_to_I2', index_col=0)
    sitc_isic.index = sitc_isic.index.astype(str)
    
    # Map SITC2 to ISIC2 
    wits_trade_isic = copy.deepcopy(wits_trade)
    for t in wits_trade_isic.copy():
        for c in wits_trade_isic[t].copy():
            for y in wits_trade_isic[t][c].copy():
                if wits_trade_isic[t][c][y].size==0:
                    del(wits_trade_isic[t][c][y])
                    
    for t in wits_trade_isic:
        for c in wits_trade_isic[t]:
            for y in wits_trade_isic[t][c].copy():
                wits_trade_isic[t][c][y] = wits_trade_isic[t][c][y].to_frame()   
                # SITC 9310 is a residual,not sector, it has no corresponding sector to map, remove it
                if '931' in wits_trade_isic[t][c][y].index:
                    wits_trade_isic[t][c][y].drop('931', axis=0, inplace=True)
                if wits_trade_isic[t][c][y].size==0:
                    del(wits_trade_isic[t][c][y])
                    
    process_time = time.time()
    for t in wits_trade_isic:
        for c in wits_trade_isic[t]:
            for y in wits_trade_isic[t][c]:
                for indx in wits_trade_isic[t][c][y].index:
                    # When mapping exists
                    if indx in sitc_isic.index:   
                        # If one index maps to multiple, choose first one 
                        if sitc_isic.index.value_counts()[indx] > 1:
                            wits_trade_isic[t][c][y].loc[indx, 'ISIC2'] = sitc_isic.loc[
                                                                indx, 'ISIC Revision 2 Product Code'].iloc[0] 
                        else:
                            wits_trade_isic[t][c][y].loc[indx, 'ISIC2'] = sitc_isic.loc[
                                                                indx, 'ISIC Revision 2 Product Code']   
                        
                    # When mapping doesn't exist
                    # For over 3 digits: look for sector that starts with same digit (same industry group) and use corresponding mapping
                    # e.g. 6552 does not exist, look for anything starts with '655', and use that mapping
                    elif (len(indx)==3):
                        if (True in sitc_isic.index.str.startswith(indx)):
                            map_new = sitc_isic.loc[sitc_isic.index.str.startswith(indx), 
                                                    'ISIC Revision 2 Product Code'].iloc[0] 
                        else:
                            map_new = sitc_isic.loc[sitc_isic.index.str.startswith(indx[:2]), 
                                                    'ISIC Revision 2 Product Code'].iloc[0] 
                        
                        wits_trade_isic[t][c][y].loc[indx, 'ISIC2'] = map_new
                    else:
                        indx_new = indx[:1]
                        map_new = sitc_isic.loc[sitc_isic.index.str.startswith(indx_new), 
                                                'ISIC Revision 2 Product Code'].iloc[0] 
                        
                        wits_trade_isic[t][c][y].loc[indx, 'ISIC2'] = map_new
                        
                        
    print("--- Map data`: %s seconds ---" % round(time.time() - process_time, 1))
                        
    
    
    
#%%
    # Map from ISIC2 to GLORIA sectors
    isic_gloria_con = pd.read_excel(path_concordance, 'I2_to_GLORIA', index_col=0)
    
    wits_trade_gloria = copy.deepcopy(wits_trade_isic)
    for t in wits_trade_gloria:
        for c in wits_trade_gloria[t]:
            for y in wits_trade_gloria[t][c]:
                wits_trade_gloria[t][c][y].set_index('ISIC2', inplace=True)
                wits_trade_gloria[t][c][y].index = wits_trade_gloria[t][c][y].index.astype(int)
                for indx in wits_trade_gloria[t][c][y].index:
                    gloria_ind = isic_gloria_con.loc[indx, 'Gloria']
                    wits_trade_gloria[t][c][y].loc[indx, 'GLORIA_ind'] = gloria_ind
    
    for t in wits_trade_gloria:
        for c in wits_trade_gloria[t]:
            for y in wits_trade_gloria[t][c]:
                wits_trade_gloria[t][c][y] = wits_trade_gloria[t][c][y].groupby(['GLORIA_ind'])['TradeValue'].sum()
    
   
#%%

    # GILANG TO READ: Currently, for one year (and all countries), it takes over 6 min from line 426 to 462

    # Create placeholder to store trade data at same dimension
    gloria_flow_exp = {}
    gloria_flow_imp = {}
    for f in component:
        gloria_flow_exp[f] = {}
        gloria_flow_imp[f] = {}
        for c in cid:
            gloria_flow_exp[f][c] = pd.DataFrame(0, index=list(range(1, isec+1)), columns=year_gloria)
            gloria_flow_imp[f][c] = pd.DataFrame(0, index=list(range(1, isec+1)), columns=year_gloria)
            
    # column name of each components (Gov, HH, IND_sparse, NPISH and FCF)
    process_time = time.time()

    var = ['VIGA', 'VIPA', 'output', 'NPISH', 'VDFA']
    # Read in Gloria export and import, by components of all flows
    # Due to the size of data,this stage is done year by year, to avoid storing all year data at once
    flow_exp = {}   
    flow_imp = {}
    flow_exp_agg = {}   
    flow_imp_agg = {}   
    for y in year_gloria:
        gov = pd.read_pickle(path_pkl + '{}\\GOV.pkl'.format(y))
        hh = pd.read_pickle(path_pkl + '{}\\HH.pkl'.format(y))
        output = pd.read_pickle(path_pkl + '{}\\IND_sparse.pkl'.format(y))
        npish = pd.read_pickle(path_pkl + '{}\\NPISH.pkl'.format(y))
        inv = pd.read_pickle(path_pkl + '{}\\FCF.pkl'.format(y))
        flow = {'Gov':gov, 'HH':hh, 'Output':output, 'NPISH':npish, 'INV': inv}
        for f, v in zip(flow, var):
            flow[f]= flow[f].reset_index()
            flow_exp[f] = {}
            flow_exp_agg[f] = {}
            flow_imp[f] = {}
            flow_imp_agg[f] = {}
            for c in cid:
                flow_exp[f][c] = flow[f][flow[f]['REG_exp']==c]
                flow_exp[f][c] = flow_exp[f][c][flow_exp[f][c]['REG_exp']!=flow_exp[f][c]['REG_imp']]
                flow_exp_agg[f][c] = flow_exp[f][c].groupby(['REG_exp', 'TRAD_COMM'])[v].sum()
                flow_imp[f][c] = flow[f][flow[f]['REG_imp']==c]
                flow_imp[f][c] = flow_imp[f][c][flow_imp[f][c]['REG_imp']!=flow_imp[f][c]['REG_exp']]
                flow_imp_agg[f][c] = flow_imp[f][c].groupby(['REG_imp', 'TRAD_COMM'])[v].sum()
                
                # loop through sector index, and put value into the already created dataframe where index is 
                # gloria sectors. So that all five components will have same 120 sectors as rows, and year
                # as columns
                for s in flow_exp_agg[f][c].index:
                    gloria_flow_exp[f][c].loc[s, y] = flow_exp_agg[f][c].loc[s]
                for s in flow_imp_agg[f][c].index:
                    gloria_flow_imp[f][c].loc[s, y] = flow_imp_agg[f][c].loc[s]
    
    
    # Sum the five components together to get final trade
    gloria_flow = {'export': gloria_flow_exp, 'import':gloria_flow_imp}
    for t in gloria_trade:
        gloria_trade[t] = {}
        for c in cid:
            gloria_trade[t][c] = pd.DataFrame(0, index=list(range(1, isec+1)), columns=year_gloria)
            for f in flow:
                gloria_trade[t][c] += gloria_flow[t][f][c]
    
    print("--- Map data`: %s seconds ---" % round(time.time() - process_time, 1))
            
#%%            
'''
    flow = {}
    for com in component:
        flow[com] = {}
        for y in year_gloria:
            flow[com][y] = pd.read_pickle(path_pkl + '{}\\{}.pkl'.format(y, com))
            
    for f in flow:
        for y in flow[f]:
            flow[f][y] = flow[f][y].reset_index()
    # Collect export
    flow_exp = {}   
    flow_exp_agg = {}   
    for f, v in zip(flow, var):
        flow_exp[f] = {}
        flow_exp_agg[f] = {}
        for c in cid:
            flow_exp[f][c] = {}
            flow_exp_agg[f][c] = {}
            for y in year_gloria:
                flow_exp[f][c][y] = flow[f][y][flow[f][y]['REG_exp']==c]
                flow_exp[f][c][y] = flow_exp[f][c][y][flow_exp[f][c][y]['REG_exp']!=flow_exp[f][c][y]['REG_imp']]
                # flow_exp[f][c][y].drop(['REG_exp', 'REG_imp'] , axis=1, inplace=True)
                flow_exp_agg[f][c][y] = flow_exp[f][c][y].groupby(['TRAD_COMM'])[v].sum()
    del(flow_exp)
            
    # Collect import
    flow_imp = {}   
    flow_imp_agg = {}   
    for f, v in zip(flow, var):
        flow_imp[f] = {}
        flow_imp_agg[f] = {}
        for c in cid:
            flow_imp[f][c] = {}
            flow_imp_agg[f][c] = {}
            for y in year_gloria:
                flow_imp[f][c][y] = flow[f][y][flow[f][y]['REG_imp']==c]
                flow_imp[f][c][y] = flow_imp[f][c][y][flow_imp[f][c][y]['REG_imp']!=flow_imp[f][c]['REG_exp']]
                flow_imp[f][c][y].drop(['REG_exp', 'REG_imp'] , axis=1, inplace=True)
                flow_imp_agg[f][c][y] = flow_imp[f][c][y].groupby(['TRAD_COMM'])[v].sum()
    del(flow_imp)
    
    flow_agg = {'export': copy.deepcopy(flow_exp_agg), 'import': copy.deepcopy(flow_imp_agg)}     
    
    gloria_flow = {'export': {}, 'import': {}}
    for t in gloria_flow:
        gloria_flow[t] = {}
        for f in flow:
            gloria_flow[t][f] = {}
            for c in cid:
                gloria_flow[t][f][c] = pd.DataFrame(0, index=list(range(1, isec+1)), columns=year_gloria)
                for s in flow_agg[t][f][c][y].index:
                    gloria_flow[t][f][c].loc[s, y] = flow_agg[t][f][c][y].loc[s]
                    
    # Sum across all flows to get aggregate trade
    gloria_trade = {'export': {}, 
                    'import': {}}
    
    for t in gloria_trade:
        gloria_trade[t] = {}
        for c in cid:
            gloria_trade[t][c] = pd.DataFrame(0, index=list(range(1, isec+1)), columns=year_gloria)
            for f in flow:
                gloria_trade[t][c] += gloria_flow[t][f][c]
#%%
'''
#%%
    # Use Gloria export/import shares to convert WITS data from ISIC2 to corresponding Gloria sectors
    ind_to_split = [i for i in isic_gloria_con['Gloria'] if not pd.api.types.is_number(i)]
    ind_to_split = list(dict.fromkeys(ind_to_split))
    
    # For ISIC2 sectors that map to multiple gloria sectors, split to gloria sector using trade shares
    for t in wits_trade_gloria:
        for c in wits_trade_gloria[t]:
            cou = wits_gloria_con.index[wits_gloria_con['WITS']==c].item()
            for y in wits_trade_gloria[t]:
            # for y in wits_trade_gloria[t][c]:
                for i in wits_trade_gloria[t][c][y].index:
                    if not pd.api.types.is_number(i):
                        ind_list = i.split(',')
                        ind_list = [int(i) for i in ind_list]
                        wits_trade_gloria[t][c][y].loc[ind_list] = (gloria_trade[t][cou].loc[ind_list, y] 
                                                                / gloria_trade[t][cou].loc[ind_list, y].sum())
    
    # For Gloria regions that consist of multiple member states, aggregates
    cou_to_add = [i for i in wits_gloria_con.index if list(wdi_glo_con.index).count(i) > 1]
    
    
 
        # for ind in glo_def[c].index:
        #     ind_list = sea_map.loc[ind, 'sea_ind'].split(',')
        #     # if one subsector can be mapped under one broad sector
        #     if len(ind_list) == 1:
        #         glo_def[c].loc[ind] = sea_def_2019[c].loc[sea_map.loc[ind, 'sea_ind']]
        #     # else, use weighted deflator from multiple sub-sectors
        #     else:
        #         weight[c][ind] = pd.DataFrame(0, index=ind_list, columns=years)
        #         for sub_ind in weight[c][ind].index:
        #             weight[c][ind].loc[sub_ind] = sea_gva_usd['cp'][c].loc[sub_ind] / sea_gva_usd['cp'][c].loc[ind_list].sum()
        #         # Calculate weighted average
        #         glo_def[c].loc[ind] = (weight[c][ind] * sea_def_2019[c].loc[ind_list]).sum()
        #         if weight[c][ind].loc[sub_ind].isnull().all():
        #             glo_def[c].loc[ind] = sea_def_2019[c].loc[sub_ind]
            
            
            
    
        
    
    
    
    
    