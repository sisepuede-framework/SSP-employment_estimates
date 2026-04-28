# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 12:50:14 2023

@author: wb582890
"""

import time
import csv
import numpy as np
import pandas as pd
import scipy.io

import re
import os

start_parse = time.time()

IO_Data = "C:\\Users\\Public\\Documents\\MINDSET_module\\GLORIA_db\\v57\\Parsed IO\\2019\\"

start_load = time.time()

sut_tbl = scipy.io.loadmat(IO_Data + "GLORIA_MRIO_2019.mat")

IO_bp = sut_tbl["IO"]
FD_bp = sut_tbl["FD"]
VA = sut_tbl["VA"]
tax = sut_tbl["Tax"]

cid = sut_tbl["cid"]
cid = [str(i[0]) for sub in cid for i in sub]
cou = sut_tbl["cou"]
cou = [str(i[0]) for sub in cou for i in sub]
sec = sut_tbl["sec"]
sec = [str(i[0]) for sub in sec for i in sub]

sid = [i for i in range(1,121)]

del sut_tbl

print("--- Loading MRIO time: %s seconds ---" % (time.time() - start_load))

start_index2 = time.time()

Reg_ID = pd.DataFrame([e for e in cid for i in range(len(sec))])
Region = pd.DataFrame([e for e in cou for i in range(len(sec))])
Sector = pd.DataFrame(list(sec) * len(cid))
Sec_ID = pd.DataFrame(list(range(1,121)) * len(cid))

GLORIA_id = pd.concat([Reg_ID, Region, Sec_ID, Sector], axis=1)
GLORIA_id.columns = ["Reg_ID", "Region", "Sec_ID", "Sector"]

GLORIA_rp = pd.concat([Reg_ID, Sec_ID], axis=1)
GLORIA_rp.columns = ["REG_imp", "PROD_COMM"]

del Reg_ID, Region, Sec_ID, Sector

print("--- Building 2D Indices time: %s seconds ---" % (time.time() - start_index2))

Parsed_Data = "C:\\Users\\Public\\Documents\\MINDSET_module\\GLORIA_db\\v57\\Parsed IO\\"

usecol, userow = [], []

for i in range(0,164):
    for j in range(0,120):
        usecol.append(i*240+j)
        userow.append((2*i+1)*120+j)

for year in range(1990,2027):
    
    SUTData = f"C:\\Users\\Public\\Documents\\MINDSET_module\\GLORIA_db\\v57\\Satellite Accounts\\GLORIA_SatelliteAccounts_057_{year}\\"
    
    for file in os.listdir(SUTData):
        if re.search(f"TQ\-Results\_{year}\_057\_Markup001\(full\)\.csv", file):
            print(f"Raw file Satellite found: {file}")
            break

    satellite_dta = csv.reader(open(SUTData + file))

    satellite = [data for data in satellite_dta]
    satellite = np.asarray(satellite, dtype=np.float64)

    print("--- Parsing Satellite time: %s seconds ---" % (time.time() - start_parse))

    satellite = satellite[:,usecol]
    empl_GLORIA = satellite[62:67]
    empl_GLORIA = pd.concat([GLORIA_rp, pd.DataFrame(empl_GLORIA.transpose())], axis=1)
    empl_GLORIA.columns = ["REG_imp", "PROD_COMM", "Empl_Female", "Empl_Male",
                           "Empl_low", "Empl_mid", "Empl_high"]

    empl_GLORIA.to_pickle(Parsed_Data + f"{year}\\parsed_db\\empl_data.pkl")
