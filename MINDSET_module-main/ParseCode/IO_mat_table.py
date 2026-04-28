# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 01:17:36 2022

@author: ghardadi
"""

import numpy as np
import pandas as pd
import scipy.io
import time
import pickle

IO_Data = "..\\"

start_load = time.time()

version = "v57"
year = 2019

iot_tbl = scipy.io.loadmat(
    IO_Data + f"GLORIA_db\\{version}\\{year}\\GLORIA_MRIO_{year}.mat")

IO_bp = iot_tbl["IO"]
FD_bp = iot_tbl["FD"]
VA = iot_tbl["VA"]
tax = iot_tbl["Tax"]
sub = iot_tbl["Sub"]

cid = iot_tbl["cid"]
cid = [str(i[0]) for sub in cid for i in sub]
cou = iot_tbl["cou"]
cou = [str(i[0]) for sub in cou for i in sub]
sec = iot_tbl["sec"]
sec = [str(i[0]) for sub in sec for i in sub]

del iot_tbl

print("--- Loading MRIO time: %s seconds ---" % round(time.time() - start_load, 2))

cou_ID = 104 # Mongolia

IO_dom = IO_bp[cou_ID*120:(cou_ID+1)*120,cou_ID*120:(cou_ID+1)*120]
IO_exp = IO_bp[cou_ID*120:(cou_ID+1)*120,:].reshape((120,164,120)).sum(axis=1) - IO_dom
IO_imp = IO_bp[:,cou_ID*120:(cou_ID+1)*120].reshape((164,120,120)).sum(axis=0) - IO_dom

FD_dom = FD_bp[cou_ID*120:(cou_ID+1)*120,cou_ID*6:(cou_ID+1)*6]
FD_exp = FD_bp[cou_ID*120:(cou_ID+1)*120,:].reshape((120,164,6)).sum(axis=1) - FD_dom
FD_imp = FD_bp[:,cou_ID*6:(cou_ID+1)*6].reshape((164,120,6)).sum(axis=0) - FD_dom

VA_cou = VA[:,cou_ID*120:(cou_ID+1)*120]
tax_cou = tax[0,cou_ID*120:(cou_ID+1)*120]
sub_cou = sub[0,cou_ID*120:(cou_ID+1)*120]

Output1 = IO_bp[:,cou_ID*120:(cou_ID+1)*120].sum(axis=0) + VA_cou.sum(axis=0) + tax_cou + sub_cou
Output2 = IO_bp[cou_ID*120:(cou_ID+1)*120,:].sum(axis=1) + FD_bp[cou_ID*120:(cou_ID+1)*120,:].sum(axis=1)

Dom_IO_tbl = np.empty((130,129))
Dom_IO_tbl[:] = np.nan

Dom_IO_tbl[:120,:120] = IO_dom

Dom_IO_tbl[:120,120] = IO_exp.sum(axis=1)
Dom_IO_tbl[120,:120] = IO_imp.sum(axis=0)

Dom_IO_tbl[:120,121:127] = FD_dom

Dom_IO_tbl[:120,127] = FD_exp.sum(axis=1)
Dom_IO_tbl[120,121:127] = FD_imp.sum(axis=0)

Dom_IO_tbl[121:127,:120] = VA_cou
Dom_IO_tbl[127,:120] = tax_cou
Dom_IO_tbl[128,:120] = sub_cou

Dom_IO_tbl[129,:120] = Output1
Dom_IO_tbl[:120,128] = Output2

Dom_IO_row = sec.copy()
Dom_IO_row.extend(["Imports", "Compensation of employees", "Taxes on production",
                   "Subsidies on production", "Net operating surplus",
                   "Net mixed income", "Consumption of fixed capital",
                   "Taxes on products", "Subsidies on products", "Output"])

Dom_IO_col = sec.copy()
Dom_IO_col.extend(["Intmd. exp.", "Household", "NPISH", "Government", "Capital form.",
                   "Chg. in invt.", "Acquisitions", "Fin. Demand exp.", "Output"])

Dom_IO = pd.DataFrame(Dom_IO_tbl, index=Dom_IO_row, columns=Dom_IO_col)

ExIm_IO_col = sec.copy()
ExIm_IO_col.extend(["Household", "NPISH", "Government", "Capital form.",
                    "Chg. in invt.", "Acquisitions"])

Exp_IO_tbl = np.zeros((120,126))
Exp_IO_tbl[:120,:120] = IO_exp
Exp_IO_tbl[:120,120:126] = FD_exp

Imp_IO_tbl = np.zeros((120,126))
Imp_IO_tbl[:120,:120] = IO_imp
Imp_IO_tbl[:120,120:126] = FD_imp

Exp_IO = pd.DataFrame(Exp_IO_tbl, index=sec, columns=ExIm_IO_col)
Imp_IO = pd.DataFrame(Imp_IO_tbl, index=sec, columns=ExIm_IO_col)

Dom_IO = round(Dom_IO / 1000, 1)
Exp_IO = round(Exp_IO / 1000, 1)
Imp_IO = round(Imp_IO / 1000, 1)

with pd.ExcelWriter(
        IO_Data + f'National_IO\\GLORIA_{version}_' + cid[cou_ID] + f'_{year}.xlsx',
        engine='xlsxwriter') as ResultsWriter:
    Dom_IO.to_excel(ResultsWriter, sheet_name='Dom_IO')
    Exp_IO.to_excel(ResultsWriter, sheet_name='Exp_IO')
    Imp_IO.to_excel(ResultsWriter, sheet_name='Imp_IO')
    
ResultsWriter.close()

