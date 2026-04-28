# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 09:26:37 2022

@author: ghardadi
"""

import csv
import numpy as np
import pandas as pd
import scipy.io
import time
# import openpyxl

SUTData = "C:\\Users\\Gilang Hardadi\\Documents\\GLORIA_MRIOs_55_2020\\"

regions = pd.read_excel(SUTData + "GLORIA_ReadMe.xlsx", "Regions")
sectors = pd.read_excel(SUTData + "GLORIA_ReadMe.xlsx", "Sectors")

cid = regions.iloc[:,1].to_numpy()
cou = regions.iloc[:,2].to_numpy()

sec = sectors.iloc[:,1].to_numpy()

Regions = pd.DataFrame([e for e in cid for i in range(len(sec))])
R_names = pd.DataFrame([e for e in cou for i in range(len(sec))])
Sectors = pd.DataFrame(list(sec) * len(cid))

GLORIA_id = pd.concat([Regions, R_names, Sectors], axis=1)
GLORIA_id.columns = ["ID", "Regions", "Sectors"]

del Regions, R_names, Sectors

start_parse = time.time()

sut_tbl = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_T-Results_2020_055_Markup001(full).csv"))

SUT = [data for data in sut_tbl]
SUT = np.asarray(SUT, dtype=np.float64)

# sut_tbl = pd.read_csv(
#     SUTData + "20220309_120secMother_AllCountries_002_T-Results_2020_055_Markup001(full).csv",
#     header=None, engine="pyarrow")

print("--- Parsing SUT time: %s seconds ---" % (time.time() - start_parse))

# SUT = sut_tbl.to_numpy()
del sut_tbl

usecol, userow = [], []

for i in range(0,164):
    for j in range(0,120):
        usecol.append(i*240+j)
        userow.append((2*i+1)*120+j)

supcol = userow
suprow = usecol        

V = SUT[suprow,:]
V = V[:,supcol]

U = SUT[userow,:]
U = U[:,usecol]

# V = np.zeros((19680,19680))
# U = np.zeros((19680,19680))

# for p in range(0,164):
#     for q in range(0,120):
#         for r in range(0,164):
#             for s in range(0,120):
#                 V[p*120+q, r*120+s] = SUT[p*240+q,(2*r+1)*120+s]
#                 U[p*120+q, r*120+s] = SUT[(2*p+1)*120+q,r*240+s]
#     print(p)

del SUT
        
V_diag = np.zeros(19680)

for i in range(0,19680):
    V_diag[i] = V[i,i]

if sum(V_diag != V.sum(axis=0)) == 0:
    print("Supply table is a diagonal matrix.")
    del V
else:
    print("Supply table is NOT a diagonal matrix.")

start_parse = time.time()

fd_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_Y-Results_2020_055_Markup001(full).csv"))

FD = [data for data in fd_dta]
FD = np.asarray(FD, dtype=np.float64)

# fd_tbl = pd.read_csv(
#     SUTData + "20220309_120secMother_AllCountries_002_Y-Results_2020_055_Markup001(full).csv",
#     header=None, engine="pyarrow")

print("--- Parsing FD time: %s seconds ---" % (time.time() - start_parse))

# FD = fd_tbl.to_numpy()
del fd_dta

Y = FD[userow,:]

del FD

# Y = np.zeros((19680,984))

# for p in range(0,164):
#     for q in range(0,120):
#         for r in range(0,164):
#             for s in range(0,6):
#                 Y[p*120+q, r*6+s] = FD[(2*p+1)*120+q, r*6+s]
#     print(p)

start_parse = time.time()

va_tbl = pd.read_csv(
    SUTData + "20220309_120secMother_AllCountries_002_V-Results_2020_055_Markup001(full).csv",
    header=None)

print("--- Parsing VA time: %s seconds ---" % (time.time() - start_parse))

VA = va_tbl.to_numpy()
del va_tbl

W = np.zeros((6,19680))

for p in range(0,164):
    for q in range(0,120):
        for s in range(0,6):
            W[s, p*120+q] = VA[p*6+s, p*240+q]
    # print(p)

start_parse = time.time()

td_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_T-Results_2020_055_Markup002(full).csv"))

td_mgn = [data for data in td_dta]
td_mgn = np.asarray(td_mgn, dtype=np.float64)

print("--- Parsing Trade Margin time: %s seconds ---" % (time.time() - start_parse))

TdM_IO = td_mgn[userow,:]
TdM_IO = TdM_IO[:,usecol]

del td_mgn

start_parse = time.time()

tp_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_T-Results_2020_055_Markup003(full).csv"))

tp_mgn = [data for data in tp_dta]
tp_mgn = np.asarray(tp_mgn, dtype=np.float64)

print("--- Parsing Transport Margin time: %s seconds ---" % (time.time() - start_parse))

TpM_IO = tp_mgn[userow,:]
TpM_IO = TpM_IO[:,usecol]

del tp_mgn

start_parse = time.time()

fd_tdm_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_Y-Results_2020_055_Markup002(full).csv"))

FD_tdm = [data for data in fd_tdm_dta]
FD_tdm = np.asarray(FD_tdm, dtype=np.float64)

print("--- Parsing FD Trade Margin time: %s seconds ---" % (time.time() - start_parse))

del fd_tdm_dta

Y_tdm = FD_tdm[userow,:]

del FD_tdm

start_parse = time.time()

fd_tpm_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_Y-Results_2020_055_Markup003(full).csv"))

FD_tpm = [data for data in fd_tpm_dta]
FD_tpm = np.asarray(FD_tpm, dtype=np.float64)

print("--- Parsing FD Transport Margin time: %s seconds ---" % (time.time() - start_parse))

del fd_tpm_dta

Y_tpm = FD_tpm[userow,:]

del FD_tpm

scipy.io.savemat(SUTData + "GLORIA_Margin_2020.mat",
                 {"Trade_IO": TdM_IO, "Transport_IO": TpM_IO,
                  "Trade_FD": Y_tdm, "Transport_FD": Y_tpm})

Td_Margin = TdM_IO.sum(axis=0)
Tp_Margin = TpM_IO.sum(axis=0)

del TdM_IO, TpM_IO, Y_tdm, Y_tpm

start_parse = time.time()

tax_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_T-Results_2020_055_Markup004(full).csv"))

tax = [data for data in tax_dta]
tax = np.asarray(tax, dtype=np.float64)

print("--- Parsing Taxes Data time: %s seconds ---" % (time.time() - start_parse))

Tax_IO = tax[userow,:]
Tax_IO = Tax_IO[:,usecol]

del tax

start_parse = time.time()

sub_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_T-Results_2020_055_Markup005(full).csv"))

sub = [data for data in sub_dta]
sub = np.asarray(sub, dtype=np.float64)

print("--- Parsing Subsidies Data time: %s seconds ---" % (time.time() - start_parse))

Sub_IO = sub[userow,:]
Sub_IO = Sub_IO[:,usecol]

del sub
 
start_parse = time.time()

fd_tax_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_Y-Results_2020_055_Markup004(full).csv"))

FD_tax = [data for data in fd_tax_dta]
FD_tax = np.asarray(FD_tax, dtype=np.float64)

print("--- Parsing FD Taxes time: %s seconds ---" % (time.time() - start_parse))

del fd_tax_dta

Y_tax = FD_tax[userow,:]

del FD_tax

start_parse = time.time()

fd_sub_dta = csv.reader(open(
    SUTData + "20220309_120secMother_AllCountries_002_Y-Results_2020_055_Markup005(full).csv"))

FD_sub = [data for data in fd_sub_dta]
FD_sub = np.asarray(FD_sub, dtype=np.float64)

print("--- Parsing FD Subsidies time: %s seconds ---" % (time.time() - start_parse))

del fd_sub_dta

Y_sub = FD_sub[userow,:]

del FD_sub

scipy.io.savemat(SUTData + "GLORIA_Taxes_2020.mat",
                 {"Taxes_IO": Tax_IO, "Subsidies_IO": Sub_IO,
                  "Taxes_FD": Y_tax, "Subsidies_FD": Y_sub})

Tax = Tax_IO.sum(axis=0)
Sub = Sub_IO.sum(axis=0)

scipy.io.savemat(SUTData + "GLORIA_MRIO_2020.mat",
                 {"IO": U, "S": V_diag, "VA": W, "FD": Y, "Tax": Tax, "Sub": Sub,
                  "cid": cid, "cou": cou, "sec": sec})

Q1 = U.sum(axis=1) + Y.sum(axis=1)
Q2 = U.sum(axis=0) + W.sum(axis=0) + Tax_IO.sum(axis=0) + Sub_IO.sum(axis=0)

DeltaQ = pd.concat([GLORIA_id, pd.DataFrame(Q1)], axis=1)
DeltaQ = pd.concat([DeltaQ, pd.DataFrame(Q2)], axis=1)
DeltaQ = pd.concat([DeltaQ, pd.DataFrame(abs(Q1-Q2))], axis=1)
DeltaQ = pd.concat([DeltaQ, pd.DataFrame(abs(Q1-Q2)/Q1)], axis=1)
DeltaQ = pd.concat([DeltaQ, pd.DataFrame(V_diag)], axis=1)
DeltaQ = DeltaQ.fillna(0)
DeltaQ.columns = ["ID", "Regions", "Sectors", "Q1", "Q2", "dQ_abs", "dQ_rel", "Q3"]

ResultsWriter = pd.ExcelWriter(SUTData + 'GLORIA_Balance.xlsx', engine='xlsxwriter')

DeltaQ.to_excel(ResultsWriter, sheet_name='Delta_Q')
# ResultsWriter.save()

Margin_IO = pd.concat([GLORIA_id, pd.DataFrame(Td_Margin)], axis=1)
Margin_IO = pd.concat([Margin_IO, pd.DataFrame(Tp_Margin)], axis=1)
Margin_IO.columns = ["ID", "Regions", "Sectors", "Trade", "Transport"]

# ResultsWriter = pd.ExcelWriter(SUTData + 'Margin_IO.xlsx', engine='xlsxwriter')

Margin_IO.to_excel(ResultsWriter, sheet_name='Margin_IO')

Q_element = pd.concat([GLORIA_id, pd.DataFrame(U.sum(axis=1))], axis=1)
Q_element = pd.concat([Q_element, pd.DataFrame(Y.sum(axis=1))], axis=1)
Q_element = pd.concat([Q_element, pd.DataFrame(U.sum(axis=0))], axis=1)
Q_element = pd.concat([Q_element, pd.DataFrame(W.sum(axis=0))], axis=1)
Q_element = pd.concat([Q_element, pd.DataFrame(Tax_IO.sum(axis=0))], axis=1)
Q_element = pd.concat([Q_element, pd.DataFrame(Sub_IO.sum(axis=0))], axis=1)
Q_element.columns = ["ID", "Regions", "Sectors", "Int. Demand", "Fin. Demand",
                     "Int. Input", "Value Added", "Taxes", "Subsidies"]

# ResultsWriter = pd.ExcelWriter(SUTData + 'Margin_IO.xlsx', engine='xlsxwriter')

Q_element.to_excel(ResultsWriter, sheet_name='Q_element')

ResultsWriter.save()

