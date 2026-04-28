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

IO_Data = "C:\\Users\\WB582890\\OneDrive - WBG\\Documents\\mrio-recycling\\dynamicmriopricemodelDATA\\"

start_load = time.time()

sut_tbl = scipy.io.loadmat(IO_Data + "GLORIA_db\\GLORIA_MRIO_2019.mat")

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

start_index4 = time.time()

Reg_imp = pd.DataFrame([e for e in cid for i in range(len(sec) * len(cid) * len(sec))])
Prod_ID = pd.DataFrame([i for i in range(1,121) for _ in range(len(sec) * len(cid))] * len(cid))
Reg_exp = pd.DataFrame([e for e in cid for i in range(len(sec))] * (len(cid) * len(sec)))
Trad_ID = pd.DataFrame(list(range(1,121)) * (len(cid) * len(sec) * len(cid)))

IND_sparse = pd.concat([Reg_imp, Prod_ID, Reg_exp, Trad_ID], axis=1)
IND_sparse.columns = ["REG_imp","PROD_COMM","REG_exp","TRAD_COMM"]

del Reg_imp, Prod_ID, Reg_exp, Trad_ID

print("--- Building 4D Indices time: %s seconds ---" % (time.time() - start_index4))

start_sparse = time.time()

output = IO_bp.sum(axis=0) + VA.sum(axis=0) + tax

# del FD_bp, VA, tax

IO_bp[IO_bp < 1] = 0

IND_sparse = pd.concat([IND_sparse,pd.DataFrame(IO_bp.transpose().reshape(len(IO_bp)**2))], axis=1)

colnames = list(IND_sparse.columns[:4])
colnames.append("z_bp")
IND_sparse.columns = colnames

A_bp = np.divide(IO_bp, output, where=output!=0)

del IO_bp

IND_sparse = pd.concat([IND_sparse,pd.DataFrame(A_bp.transpose().reshape(len(A_bp)**2))], axis=1)

del A_bp

colnames = list(IND_sparse.columns[:5])
colnames.append("a_bp")
IND_sparse.columns = colnames

IND_sparse["z_bp"] = IND_sparse["z_bp"].replace({0:np.nan})
IND_sparse = IND_sparse.dropna()
IND_sparse = IND_sparse.set_index(["REG_imp","PROD_COMM","REG_exp","TRAD_COMM"])

IND_sparse["a_tech"] = IND_sparse.groupby(["REG_imp","PROD_COMM","TRAD_COMM"])["a_bp"].transform('sum')

Output = pd.concat([GLORIA_rp,pd.DataFrame(output[0])], axis=1)
Output = Output.rename(columns={0:"output"})
Output = Output.set_index(["REG_imp","PROD_COMM"])

Output.to_pickle(IO_Data + "GLORIA_db\\Output.pkl")

IND_index = IND_sparse.index

IND_sparse = pd.merge(IND_sparse, Output, left_on=["REG_imp","PROD_COMM"],
                      right_on=["REG_imp","PROD_COMM"])

IND_sparse = IND_sparse.set_index(IND_index)

IND_sparse.to_pickle(IO_Data + "GLORIA_db\\IND_sparse.pkl")

print("--- Building IND_sparse time: %s seconds ---" % (time.time() - start_sparse))

with open(IO_Data + "GLORIA_db\\cid.pkl", 'wb') as f:
    pickle.dump(cid, f)

with open(IO_Data + "GLORIA_db\\cou.pkl", 'wb') as f:
    pickle.dump(cou, f)

with open(IO_Data + "GLORIA_db\\sec.pkl", 'wb') as f:
    pickle.dump(sec, f)

HH = np.zeros((19680,164))

for i in range(164):
    HH[:,i] = FD_bp[:,6*i] 

HH = pd.concat([GLORIA_rp,pd.DataFrame(HH)], axis=1)
HH = HH.rename(columns={"REG_imp":"REG_exp", "PROD_COMM":"TRAD_COMM"})
HH.columns.values[2:] = cid 
HH = HH.melt(id_vars=["REG_exp","TRAD_COMM"], value_vars=cid)
HH = HH.rename(columns={"variable":"REG_imp","value":"VIPA"})
HH = HH.set_index(["REG_imp","REG_exp","TRAD_COMM"])

HH[HH < 1e-3] = 0
HH["VIPA"] = HH["VIPA"].replace({0:np.nan})
HH = HH.dropna()

HH.to_pickle(IO_Data + "GLORIA_db\\HH.pkl")

GOV = np.zeros((19680,164))

for i in range(164):
    GOV[:,i] = FD_bp[:,6*i+2] 

GOV = pd.concat([GLORIA_rp,pd.DataFrame(GOV)], axis=1)
GOV = GOV.rename(columns={"REG_imp":"REG_exp", "PROD_COMM":"TRAD_COMM"})
GOV.columns.values[2:] = cid 
GOV = GOV.melt(id_vars=["REG_exp","TRAD_COMM"], value_vars=cid)
GOV = GOV.rename(columns={"variable":"REG_imp","value":"VIGA"})
GOV = GOV.set_index(["REG_imp","REG_exp","TRAD_COMM"])

GOV[GOV < 1e-3] = 0
GOV["VIGA"] = GOV["VIGA"].replace({0:np.nan})
GOV = GOV.dropna()

GOV.to_pickle(IO_Data + "GLORIA_db\\GOV.pkl")

FCF = np.zeros((19680,164))

for i in range(164):
    FCF[:,i] = FD_bp[:,6*i+3] 

FCF = pd.concat([GLORIA_rp,pd.DataFrame(FCF)], axis=1)
FCF = FCF.rename(columns={"REG_imp":"REG_exp", "PROD_COMM":"TRAD_COMM"})
FCF.columns.values[2:] = cid 
FCF = FCF.melt(id_vars=["REG_exp","TRAD_COMM"], value_vars=cid)
FCF = FCF.rename(columns={"variable":"REG_imp","value":"VDFA"})
FCF = FCF.set_index(["REG_imp","REG_exp","TRAD_COMM"])

FCF[FCF < 1e-3] = 0
FCF["VDFA"] = FCF["VDFA"].replace({0:np.nan})
FCF = FCF.dropna()

FCF.to_pickle(IO_Data + "GLORIA_db\\FCF.pkl")

NPISH = np.zeros((19680,164))

for i in range(164):
    NPISH[:,i] = FD_bp[:,6*i+1]
        
NPISH = pd.concat([GLORIA_rp,pd.DataFrame(NPISH)], axis=1)
NPISH = NPISH.rename(columns={"REG_imp":"REG_exp", "PROD_COMM":"TRAD_COMM"})
NPISH.columns.values[2:] = cid
NPISH = NPISH.melt(id_vars=["REG_exp","TRAD_COMM"], value_vars=cid)
NPISH = NPISH.rename(columns={"variable":"REG_imp","value":"NPISH"})
NPISH = NPISH.set_index(["REG_imp","REG_exp","TRAD_COMM"])

NPISH[NPISH < 1e-3] = 0
NPISH["NPISH"] = NPISH["NPISH"].replace({0:np.nan})
NPISH = NPISH.dropna()

NPISH.to_pickle(IO_Data + "\\GLORIA_db\\NPISH.pkl")

INV = np.zeros((19680,164))

for i in range(164):
    INV[:,i] = FD_bp[:,6*i+4:6*i+6].sum(axis=1)
        
INV = pd.concat([GLORIA_rp,pd.DataFrame(INV)], axis=1)
INV = INV.rename(columns={"REG_imp":"REG_exp", "PROD_COMM":"TRAD_COMM"})
INV.columns.values[2:] = cid
INV = INV.melt(id_vars=["REG_exp","TRAD_COMM"], value_vars=cid)
INV = INV.rename(columns={"variable":"REG_imp","value":"INV"})
INV = INV.set_index(["REG_imp","REG_exp","TRAD_COMM"])

INV[((INV > 0) & (INV < 1e-3)) | ((INV < 0) & (INV > -1e-3))] = 0
INV["INV"] = INV["INV"].replace({0:np.nan})
INV = INV.dropna()

INV.to_pickle(IO_Data + "\\GLORIA_db\\INV.pkl")

other_FD = np.zeros((19680,164))

for i in range(164):
    other_FD[:,i] = FD_bp[:,6*i+1] + FD_bp[:,6*i+4:6*i+6].sum(axis=1)
    
other_FD = pd.concat([GLORIA_rp,pd.DataFrame(other_FD)], axis=1)
other_FD = other_FD.rename(columns={"REG_imp":"REG_exp", "PROD_COMM":"TRAD_COMM"})
other_FD.columns.values[2:] = cid
other_FD = other_FD.melt(id_vars=["REG_exp","TRAD_COMM"], value_vars=cid)
other_FD = other_FD.rename(columns={"variable":"REG_imp","value":"otherFD"})
other_FD = other_FD.set_index(["REG_imp","REG_exp","TRAD_COMM"])

other_FD[((other_FD > 0) & (other_FD < 1e-3)) | ((other_FD < 0) & (other_FD > -1e-3))] = 0
other_FD["otherFD"] = other_FD["otherFD"].replace({0:np.nan})
other_FD = other_FD.dropna()

other_FD.to_pickle(IO_Data + "GLORIA_db\\other_FD.pkl")

VA = pd.concat([GLORIA_rp,pd.DataFrame(VA.transpose())], axis=1)
VA.columns.values[2:] = ["Compensation of employees", "Taxes on production",
                          "Subsidies on production", "Net operating surplus",
                          "Net mixed income", "Consumption of fixed capital"]

VA = pd.concat([VA, pd.DataFrame(tax.transpose())], axis=1)
VA = VA.rename(columns={0:"Taxes on products"})

VA.to_pickle(IO_Data + "GLORIA_db\\VA.pkl")
