# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 13:18:11 2024

@author: wb582890
"""

import pandas as pd
# import openpyxl
import xlwings as xw
import os

tax_inc_coa = pd.read_excel("GLORIA_template\\Energy\\Tax_incidence.xlsx", sheet_name="24_coa")
tax_inc_lig = pd.read_excel("GLORIA_template\\Energy\\Tax_incidence.xlsx", sheet_name="25_lig")
tax_inc_gas = pd.read_excel("GLORIA_template\\Energy\\Tax_incidence.xlsx", sheet_name="27_gas")
tax_inc_cok = pd.read_excel("GLORIA_template\\Energy\\Tax_incidence.xlsx", sheet_name="62_cok")
tax_inc_p_c = pd.read_excel("GLORIA_template\\Energy\\Tax_incidence.xlsx", sheet_name="63_p_c")
tax_inc_gdt = pd.read_excel("GLORIA_template\\Energy\\Tax_incidence.xlsx", sheet_name="94_gdt")

template_loc = "GLORIA_template\\Scenarios\\Jobs Group\\Payroll Tax Cut\\Templates_tax_BTA_cou_Gloria.xlsx"

for cou in list(tax_inc_coa.columns[1:]):
    location_loc = f"GLORIA_template\\Scenarios\\Jobs Group\\Payroll Tax Cut\\Templates_tax_BTA_{cou}_Gloria.xlsx"

    os.system(f'copy "{template_loc}" "{location_loc}"')
    
    # read the existing sheets so that openpyxl won't create a new one later
    # tax_template = pd.read_excel(location_loc, sheet_name="tax_scenarios")
    
    # tax_template["REG"] = cou
    # tax_template[24] = tax_inc_coa.loc[:121,cou]
    # tax_template[25] = tax_inc_lig.loc[:121,cou]
    # # tax_template[26] = tax_inc_oil.loc[:121,cou]
    # tax_template[27] = tax_inc_gas.loc[:121,cou]
    # tax_template[62] = tax_inc_cok.loc[:121,cou]
    # tax_template[63] = tax_inc_p_c.loc[:121,cou]
    # tax_template[94] = tax_inc_gdt.loc[:121,cou]
    
    # tax_template = openpyxl.load_workbook(location_loc)
    wb = xw.Book(template_loc)
    # sheet = wb.sheets['Sheet1']
    for i in range(121):
        wb.sheets['tax_scenarios'][f"A{i+2}"].value=cou
        wb.sheets['tax_scenarios'][f"C{i+2}"].value=tax_inc_coa.loc[i,cou]
        wb.sheets['tax_scenarios'][f"D{i+2}"].value=tax_inc_lig.loc[i,cou]
        wb.sheets['tax_scenarios'][f"F{i+2}"].value=tax_inc_gas.loc[i,cou]
        wb.sheets['tax_scenarios'][f"G{i+2}"].value=tax_inc_cok.loc[i,cou]
        wb.sheets['tax_scenarios'][f"H{i+2}"].value=tax_inc_p_c.loc[i,cou]
        wb.sheets['tax_scenarios'][f"J{i+2}"].value=tax_inc_gdt.loc[i,cou]

    wb.save(location_loc)
    wb.close()
    
    print(f"Country done: {cou}")
    
    