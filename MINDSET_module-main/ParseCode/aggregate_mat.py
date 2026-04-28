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

import aggregate as agg

# {"X": MRIO_X, "Z": MRIO_Z, "VA": MRIO_VA, "Y": MRIO_Y, "F_Y": MRIO_FY,
#  "F": MRIO_F, "cid": MRIO_Country, "sid": Product_Codes, "sec": Product_Names,
#  "VA_id": VA_id, "F_id": F_id, "F_unit": F_unit}

IO_Data = "C:\\Users\\WB582890\\OneDrive - WBG\\Documents\\github\\MINDSET_module\\"

start_load = time.time()

version = "v57"
year = 2017

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

start_aggregation = time.time()

aggregate = pd.read_excel(IO_Data + "GLORIA_template\\Aggregation\\GLORIA_ag.xlsx")
mrio_id = np.array(aggregate["GLORIA_ID"])
agg_id = np.array(aggregate["AGG_ID"] - 1)
agg_sec = sorted(set(aggregate["AGG_sector"]))

agg_sector = aggregate[["AGG_ID", "AGG_sector"]]
agg_sector = agg_sector.drop_duplicates().sort_values(by=["AGG_ID"])

agg_prod = list(agg_sector["AGG_sector"])

aggregate_matrix = agg.build_MultiIndex_Aggregation_Matrix([list(range(164)),agg_id])

IO_bp = np.dot(aggregate_matrix, IO_bp)
IO_bp = np.dot(IO_bp, aggregate_matrix.transpose())

FD_bp = np.dot(aggregate_matrix, FD_bp)
VA = np.dot(VA, aggregate_matrix.transpose())
tax = np.dot(tax, aggregate_matrix.transpose())
sub = np.dot(sub, aggregate_matrix.transpose())

output1 = IO_bp.sum(axis=0) + VA.sum(axis=0) + tax[0] + sub[0]
output2 = IO_bp.sum(axis=1) + FD_bp.sum(axis=1)

if (np.mean(np.divide(
        abs(output1 - output2), output1, out=np.zeros_like(output1),
        where=output2!=0)) < 5e-4):
    print("Aggregation is performed correctly")

var_dict = {"IO": IO_bp, "FD": FD_bp, "X": output1, "VA": VA, "Tax": tax, "Sub": sub,
 "cid": cid, "cou": cou, "sec": agg_prod}

scipy.io.savemat(IO_Data + f"AggregateMRIO_{version}_{year}.mat", var_dict)

del aggregate_matrix, output1, output2

print("--- Aggregating MRIO time: %s seconds ---" % round(time.time() - start_aggregation, 2))

cou_ID = 71 # Bosnia

IO_dom = IO_bp[cou_ID*32:(cou_ID+1)*32,cou_ID*32:(cou_ID+1)*32]
IO_exp = IO_bp[cou_ID*32:(cou_ID+1)*32,:].reshape((32,164,32)).sum(axis=1) - IO_dom
IO_imp = IO_bp[:,cou_ID*32:(cou_ID+1)*32].reshape((164,32,32)).sum(axis=0) - IO_dom

FD_dom = FD_bp[cou_ID*32:(cou_ID+1)*32,cou_ID*6:(cou_ID+1)*6]
FD_exp = FD_bp[cou_ID*32:(cou_ID+1)*32,:].reshape((32,164,6)).sum(axis=1) - FD_dom
FD_imp = FD_bp[:,cou_ID*6:(cou_ID+1)*6].reshape((164,32,6)).sum(axis=0) - FD_dom

VA_cou = VA[:,cou_ID*32:(cou_ID+1)*32]
tax_cou = tax[0,cou_ID*32:(cou_ID+1)*32]
sub_cou = sub[0,cou_ID*32:(cou_ID+1)*32]

Output1 = IO_bp[:,cou_ID*32:(cou_ID+1)*32].sum(axis=0) + VA_cou.sum(axis=0) + tax_cou + sub_cou
Output2 = IO_bp[cou_ID*32:(cou_ID+1)*32,:].sum(axis=1) + FD_bp[cou_ID*32:(cou_ID+1)*32,:].sum(axis=1)

Dom_IO_tbl = np.empty((42,41))
Dom_IO_tbl[:] = np.nan

Dom_IO_tbl[:32,:32] = IO_dom

Dom_IO_tbl[:32,32] = IO_exp.sum(axis=1)
Dom_IO_tbl[32,:32] = IO_imp.sum(axis=0)

Dom_IO_tbl[:32,33:39] = FD_dom

Dom_IO_tbl[:32,39] = FD_exp.sum(axis=1)
Dom_IO_tbl[32,33:39] = FD_imp.sum(axis=0)

Dom_IO_tbl[33:39,:32] = VA_cou
Dom_IO_tbl[39,:32] = tax_cou
Dom_IO_tbl[40,:32] = sub_cou

Dom_IO_tbl[41,:32] = Output1
Dom_IO_tbl[:32,40] = Output2

Dom_IO_row = agg_prod.copy()
Dom_IO_row.extend(["Imports", "Compensation of employees", "Taxes on production",
                   "Subsidies on production", "Net operating surplus", "Net mixed income",
                   "Consumption of fixed capital", "Taxes on products",
                   "Subsidies on products", "Output"])

Dom_IO_col = agg_prod.copy()
Dom_IO_col.extend(["Intmd. exp.", "Household", "NPISH", "Government", "Capital form.",
                   "Chg. in invt.", "Acquisitions", "Fin. Demand exp.", "Output"])

Dom_IO = pd.DataFrame(Dom_IO_tbl, index=Dom_IO_row, columns=Dom_IO_col)

ExIm_IO_col = agg_prod.copy()
ExIm_IO_col.extend(["Household", "NPISH", "Government", "Capital form.",
                    "Chg. in invt.", "Acquisitions"])

Exp_IO_tbl = np.zeros((32,38))
Exp_IO_tbl[:32,:32] = IO_exp
Exp_IO_tbl[:32,32:38] = FD_exp

Imp_IO_tbl = np.zeros((32,38))
Imp_IO_tbl[:32,:32] = IO_imp
Imp_IO_tbl[:32,32:38] = FD_imp

Exp_IO = pd.DataFrame(Exp_IO_tbl, index=agg_prod, columns=ExIm_IO_col)
Imp_IO = pd.DataFrame(Imp_IO_tbl, index=agg_prod, columns=ExIm_IO_col)

Dom_IO = round(Dom_IO / 1000, 1)
Exp_IO = round(Exp_IO / 1000, 1)
Imp_IO = round(Imp_IO / 1000, 1)

with pd.ExcelWriter(
        IO_Data + f'National_IO\\GLORIA32_{version}_' + cid[cou_ID] + f'_{year}.xlsx',
        engine='xlsxwriter') as ResultsWriter:
    Dom_IO.to_excel(ResultsWriter, sheet_name='Dom_IO')
    Exp_IO.to_excel(ResultsWriter, sheet_name='Exp_IO')
    Imp_IO.to_excel(ResultsWriter, sheet_name='Imp_IO')
    
ResultsWriter.close()

