# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 16:10:16 2023

@author: wb582890
"""

#%%

"""
MINDSET model main program code
run from command line or SPYDER

if running from SPYDER set SPYDER=True and set input arguments if needed

if running from CMD you can set input arguments through specifying them in the call, i.e.:
python RunMINDSET.py "IDN_FFSR_onlyHH" "tax_incidence_all.csv" "Temp\\dL_ener.pkl"

the arguments in the CMD case are the following
1st argument (required): scenario file (xlsx) from the GLORIA_Templates\\Scenarios folder
2nd argument (optional): tax incidence file for carbon tax and CBAM if it has been already calculated
3rd argument (optional): Leontief-inverse after energy impacts if it has been already calculated

"""
# ^ -----------------------------------------------------------------------------
# ^ I. Import modules and external packages                                      
# ^ -----------------------------------------------------------------------------

import numpy as np
import pandas as pd
import time
import sys
import os
import gc
import pickle

from SourceCode.exog_vars import exog_vars
from SourceCode.scenario import scenario
from SourceCode.ener_elas import ener_elas 
from SourceCode.ener_balance import ener_balance
from SourceCode.tax_rev import tax_rev
from SourceCode.BTA import BTA
from SourceCode.prod_cost import prod_cost
from SourceCode.InputOutput import IO
from SourceCode.price import price
from SourceCode.household import household as hh
from SourceCode.government import gov
from SourceCode.trade import trade
from SourceCode.investment import invest
from SourceCode.employment import empl
from SourceCode.income import income
from SourceCode.GDP import GDP
from SourceCode.results import results

from SourceCode.utils import temporary_storage
from SourceCode.utils import logging
from SourceCode.utils import MRIO_df_to_vec, MRIO_vec_to_df, MRIO_mat_to_df

from alive_progress import alive_bar

Log = logging()

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
pd.set_option('display.max_columns', None)  # Show all rows

#%%

# ^ -----------------------------------------------------------------------------
# ^ II. Read arguments                                                           
# ^ -----------------------------------------------------------------------------

# read input scenario and output file name
# #1 is scenario name
# output file name and input file name will be generated based on this
# output is: GLORIA_results//Results_MNG_XXXX.xlsx
# intput file: GLORIA_template//Scenarios//XXXX.xlsx
# where XXXX is scenario name
tax_incidence_file = None
dL_ener_file = None
residuals_file = None
mrio_inverse_recalculate = None

if len(sys.argv) > 1:
    scenario_name = sys.argv[1]
    if len(sys.argv) > 2:
        mrio_inverse_recalculate = True
        if len(sys.argv) > 3:
            residuals_file = sys.argv[3]    
else:
    scenario_name = None
    print("No arguments provided. Default scenario and re-calculating all values.")
print("Scenario being run is: {}".format(scenario_name))

SPYDER = True

if SPYDER:
    # ! ONLY FOR SPYDER
    scenario_name = "MYS_Mitigation_NETR_2030_withcarbon"
    residuals_file = "GLORIA_results\\FullResults_BA_MYS.xlsx"
    A_trade_out = False # Default = False; if wishes to print out final A matrix, set to True
    mrio_inverse_recalculate = True
    # ! END ONLY FOR SPYDER
    print("Running with SPYDER defaults")


start_time = time.time()
module_time = time.time()
cwd_ = os.getcwd() + "\\"
temp = temporary_storage("Temp")

iter_results, full_results = 1, 0
bta = 0 # no BTA

if scenario_name is None:
    print("No scenario to run. Exiting.")
    exit()

scenario_path = cwd_ + "GLORIA_template\\Scenarios\\{}.xlsx".format(scenario_name)
print("Reading scenario at: {}".format(scenario_path))

# ^ -----------------------------------------------------------------------------
# ^ III. Read in all exogenous stuff, including MRIO and scenario                
# ^ -----------------------------------------------------------------------------

# INITIALIZE exogenous variables (excluding scenario variables)
MRIO_BASE = exog_vars()

if mrio_inverse_recalculate:
    if 'Y_BASE' in MRIO_BASE.__dict__.keys():
        del MRIO_BASE.Y_BASE #type: ignore
    if 'L_BASE' in MRIO_BASE.__dict__.keys():
        del MRIO_BASE.L_BASE #type: ignore
    if 'G_BASE' in MRIO_BASE.__dict__.keys():
        del MRIO_BASE.G_BASE #type: ignore
    # import pdb; pdb.set_trace()

print("--- Exogenous variables: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

# Construct scenario module
Scenario = scenario(MRIO_BASE, scenario_path, Log)
if tax_incidence_file is None:
    Scenario.set_carbon_tax()

# ^ -----------------------------------------------------------------------------
# ^ IV. Read in energy balance and calculate carbon tax incidence (if any)       
# ^ -----------------------------------------------------------------------------

# ! TODO keep files and re-use
Energy_emissions = ener_balance(MRIO_BASE, Scenario)
if tax_incidence_file is None:
    carbon_tax = Energy_emissions.calculate_tax_incidence()
else:
    carbon_tax = Energy_emissions.read_tax_incidence(tax_incidence_file)

# # limit carbon tax to 400% tax rate
carbon_tax = carbon_tax[carbon_tax['delta_tax']!=0].copy()
carbon_tax = carbon_tax[abs(carbon_tax['delta_tax']) > 1].copy()
carbon_tax['delta_tax'] = carbon_tax['delta_tax'].apply(lambda x: x if x < 1000 else 1000) # type: ignore

Scenario.set_tax_rate(carbon_tax)

# ^ -----------------------------------------------------------------------------
# ^ V. Build helpers for various scenario related inputs                         
# ^ -----------------------------------------------------------------------------

rev_split = Scenario.build_rev_split()
payr_tax_split = Scenario.build_payr_tax_split()
rev_proportion = Scenario.build_rev_proportion()
govt_spending = Scenario.build_govt_spending()
inv_spending = Scenario.build_inv_spending()

io_changes = Scenario.set_io_changes()
Scenario.set_cost_shock()
pd.set_option('display.max_rows', None)
# ! set exog inv
Scenario.set_exog_inv()
Scenario.set_supply_constraint()

print("--- Scenario: %s seconds ---" % round(time.time() - module_time, 1))

#%%

# ^ -----------------------------------------------------------------------------
# ^ VI. Energy elasticity and exogenous price change                             
# ^ -----------------------------------------------------------------------------

module_time = time.time()

# Construct energy elasticities module
Ener_model = ener_elas(MRIO_BASE)

# Build energy elasticities dataframe and assign tax rate information
Ener_model.build_ener_elas()

# ! price shock needs to come here if 
# ! (1) includes energy and expects substitution
# ! (2) needs to have tax revenue recycling
tax_rate, tax_rate_hh = Ener_model.assign_price_change(MRIO_BASE, Scenario.tax_rate, Scenario.tax_rate_hh, Scenario.cost_shock)
tax_rate['delta_tax'] = tax_rate['delta_tax'].apply(lambda x: x if x < 5000 else 5000)
Ener_model.assign_tax_rate(MRIO_BASE.IND_BASE, tax_rate)

# tax_cou = list(set(list(tax_rate['REG_imp'].unique()) + list(tax_rate_hh['REG_imp'].unique())))

# Calculate technical and IO coefficients due to energy elasticities

#%%
tech_coef_ener = Ener_model.calc_tech_coef_ener()
ind_ener_cou = Ener_model.assign_IO_coef_cou(
    MRIO_BASE.IND_BASE, tech_coef_ener, tax_rate)
ind_ener_glo = Ener_model.assign_IO_coef_glo(
    MRIO_BASE.IND_BASE, ind_ener_cou)

# Build helper matrices for energy commodities
tax_index, tax_matrix, sec_matrix = Ener_model.build_tax_helper_matrix(ind_ener_cou)

#%%

print("--- Energy module: %s seconds ---" % round(time.time() - module_time, 1))

# ^ -----------------------------------------------------------------------------
# ^ VII. CBAM adjustment and tax revenues calculation                            
# ^ -----------------------------------------------------------------------------

# Construct BTA module
BTA_cou = BTA(Scenario, bta, MRIO_BASE.R, temp, MRIO_BASE)

module_time = time.time()

# Construct tax revenue module
Tax_rev = tax_rev(MRIO_BASE, ind_ener_cou, None, bta=bta)

# import pdb; pdb.set_trace()

tax_rev_cou_base = Tax_rev.calc_tax_rev_base(tax_rate)
tax_rev_cou = Tax_rev.calc_tax_rev(tax_rate, ind_ener_cou)

tax_rev_hh_base = Tax_rev.calc_tax_rev_hh_base(tax_rate_hh)
tax_rev_hh = Tax_rev.calc_tax_rev_hh(tax_rate_hh)

# Calculate revenue needs to be subtracted from BTA export
rev_subtract_exp_base = BTA_cou.calc_rev_subtract_exp_base(tax_rev_cou_base)
rev_subtract_exp = BTA_cou.calc_rev_subtract_exp(tax_rev_cou)

# Calculate tax revenue total (base and after energy elasticities)
tax_rev_prod_base = Tax_rev.calc_tax_rev_prod_base(tax_rev_cou_base)
tax_rev_prod = Tax_rev.calc_tax_rev_prod(tax_rev_cou)

# Calculate revenue recycled into different schemes (base and after energy elasticities)
recyc_rev_base = Tax_rev.calc_recyc_rev_base(
    tax_rev_prod_base, tax_rev_hh_base, rev_subtract_exp_base, rev_split)
recyc_rev = Tax_rev.calc_recyc_rev(
    tax_rev_prod, tax_rev_hh, rev_subtract_exp, rev_split)

print("--- Tax revenue: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

# ^ -----------------------------------------------------------------------------
# ^ VIII. Production cost calculation (! based on tax revenues !)                
# ^ -----------------------------------------------------------------------------

# Construct production module (exogenous production cost)
Prod_cost = prod_cost(MRIO_BASE, Scenario)

# Calculate wage share, employment share, labor compensation, and its national share
wage_share, empl_share, labor_share = Prod_cost.calc_shares()

# Calculate new relative exogenous production cost
exog_prod_cost_base = Prod_cost.calc_prod_cost_base(tax_rev_prod_base, recyc_rev_base)
exog_prod_cost = Prod_cost.calc_prod_cost(tax_rev_prod, recyc_rev)

# ! non-tax type price change (no recycling, no energy substitution)
# ! this only has demand effects!
exog_prod_cost = Prod_cost.prod_cost_impact(Scenario.cost_shock, exog_prod_cost)

print("--- Prod. cost module: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

#%%

# ^ -----------------------------------------------------------------------------
# ^ IX. Calculate new IO (Leontieff) and price impacts                           
# ^ -----------------------------------------------------------------------------


# with alive_bar(monitor=None, stats=None, title="Constructing IO...") as bar:
# Construct Input-Output model
IO_model = IO(MRIO_BASE)
IO_model.initialize()

#! CHANGE BACK!!!!!_

# Calculate changes in Leontief matrix for energy commodities
if dL_ener_file is None:
    dL_ener = IO_model.build_dL_ener(
        tax_index, tax_matrix, sec_matrix)
else:
    with open(dL_ener_file, 'rb') as f:
        dL_ener = pickle.load(f)

# Calculate output change due to energy elasticities
dq_tech_eff = IO_model.calc_dq_energy(dL_ener)

# del tax_index, tax_matrix, sec_matrix

# Construct price model
Price_model = price(MRIO_BASE, IO_model.L_BASE, BTA_cou)
v_base = Price_model.build_prod_cost_base_vector(exog_prod_cost_base)
v_ener = Price_model.build_prod_cost_vector(exog_prod_cost)

dp_base = Price_model.calc_dp_base(v_base)
dp_ener = Price_model.calc_dp_ener(v_ener, dL_ener)

with alive_bar(monitor=None, stats=None, title="Saving dL_ener...") as bar:
    temp.save_to_pickle(dL_ener, "dL_ener")
del dL_ener
gc.collect()

# del dL_ener

cbam_incidence = BTA_cou.calc_cbam_incidence(ind_ener_glo)
dp_pre_trade = Price_model.calc_dp_pre_trade_bta(dp_ener, cbam_incidence)

#%%

print("--- Price pre-trade: %s seconds ---" % round(time.time() - module_time, 1))


# ^ -----------------------------------------------------------------------------
# ^ X. Calculate household final demand impacts                                  
# ^ -----------------------------------------------------------------------------


module_time = time.time()

# Construct household model
HH_model = hh(MRIO_BASE)
HH_model.build_hh_elas()
# TODO ---> ERROR HERE MEMORY!!!
HH_price = HH_model.build_hh_price(dp_pre_trade, tax_rate_hh)
# ! EH
HH_price = HH_price.astype({'TRAD_COMM':'int'})

#%%
HH_price_eff, HH_inc_eff = HH_model.calc_hh_demand_change(HH_price, recyc_rev)

dy_hh_price = IO_model.build_dy_hh_price(HH_price_eff)
dy_hh_inc = IO_model.build_dy_hh_inc(HH_inc_eff)

print("--- Household module: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

# ^ -----------------------------------------------------------------------------
# ^ XI. Government                                                               
# ^ -----------------------------------------------------------------------------


# Construct government model
GOV_model = gov(MRIO_BASE, Scenario)
GOV_model.calc_trade_share()
GOV_recyc = GOV_model.calc_gov_demand_change(recyc_rev)

# dy_gov_recyc = IO_model.build_dy_gov_recyc(GOV_recyc)

dy_gov_recyc = MRIO_df_to_vec(GOV_recyc.reset_index(), 'REG_exp', 'TRAD_COMM', 'delta_y_gov', MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())

if recyc_rev['recyc_govt'].sum() != dy_gov_recyc.sum():
    ratio = dy_gov_recyc.sum() / recyc_rev['recyc_govt'].sum()
    print("#############")
    print("### WARNING: government expenditures [dy_gov_recyc] from recycling are not fully spent; only {:.0%} is spent".format(ratio))
    print("#############")

print("--- Government module: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

# Construct trade model
Trade_model = trade(MRIO_BASE)
Trade_model.build_trade_elas()
ind_trade = Trade_model.calc_IO_coef(ind_ener_glo, dp_pre_trade)

# Build new A matrix due to trade (import) substitution
A_trade = IO_model.build_A_trade(ind_trade)

print("--- Trade module: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

# Calculate output changes for each driver of output change
dq_IO_eff = IO_model.calc_dq_IO(A_trade)
A_trade_original = A_trade
y0_original = IO_model.y0

# dq_trade_eff = dq_IO_eff - dq_tech_eff
dq_trade_eff = IO_model.calc_dq_trade(dq_IO_eff, dq_tech_eff)

dq_hh_price, dq_hh_inc = IO_model.calc_dq_hh(A_trade, dy_hh_price, dy_hh_inc)

# ! add in exog FD
#%%
dy_hh_exog_fd = MRIO_df_to_vec(Scenario.fd_exog.query("PROD_COMM == 'FD_1'"), 
                                                     'REG_exp', 'TRAD_COMM', 'dy', 
                                                     MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())

dq_hh_exog_fd = IO_model.calc_dq_exog(dy_hh_exog_fd)
dy_gov_exog_fd = MRIO_df_to_vec(Scenario.fd_exog.query("PROD_COMM == 'FD_3'"), 
                                                     'REG_exp', 'TRAD_COMM', 'dy', 
                                                     MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())
dq_gov_exog_fd = IO_model.calc_dq_exog(dy_gov_exog_fd)
dy_fcf_exog_fd = MRIO_df_to_vec(Scenario.fd_exog.query("PROD_COMM == 'FD_4'"), 
                                                     'REG_exp', 'TRAD_COMM', 'dy', 
                                                     MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())
dq_fcf_exog_fd = IO_model.calc_dq_exog(dy_fcf_exog_fd)

#%%

# INV_orig = MRIO_BASE.INV_CONV
# MRIO_BASE.INV_CONV = INV_orig

#%%
from SourceCode.scenario import scenario

# Introduce supply constraints
supply_constraint = IO_model.calc_dq_supply_constraint(A_trade, Scenario.supply_constraint)
dq_supply_constraint = supply_constraint['dq_supply_constraint']
# ! FEEDBACK from supply constraint to consumption is missing
# ! i.e. y0 is not changing as it should 
# TODO

#%%
dq_gov_recyc = IO_model.calc_dq_gov(A_trade, dy_gov_recyc)
# import pdb; pdb.set_trace()
print("--- Quantity module: %s seconds ---" % round(time.time() - module_time, 1))

# Calculate price changes
module_time = time.time()

dp_trade = Price_model.calc_dp_trade(A_trade, dp_ener, v_ener)

print("--- Price post-trade: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

# ! set investment converter
from SourceCode.scenario import scenario

INV_CONV = Scenario.set_inv_conv_adj(MRIO_BASE) #type:ignore

# Construct investment model
INV_model = invest(MRIO_BASE, INV_CONV, Scenario)
inv_output_elas = INV_model.build_inv_output_elas()

# ! realign investment converter for AGRI based on output
# INV_model.adjust_INV_CONV_AGRI()
INV_model.calc_inv_share()

# Calculate new final demand due to investment
# ! add inv
INV_model.calc_dy_inv_recyc(recyc_rev)
INV_model.calc_dy_inv_exog(Scenario.inv_exog)

dy_inv_recyc = MRIO_df_to_vec(INV_model.dy_inv_recyc,"REG_imp", "TRAD_COMM",
                             "dy", MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())


if recyc_rev['recyc_inv'].sum() != dy_inv_recyc.sum():
    ratio = dy_inv_recyc.sum() / recyc_rev['recyc_inv'].sum()
    print("#############")
    print("### WARNING: government investments [dy_inv_recyc] from recycling are not fully spent; only {:.0%} is spent".format(ratio))
    print("#############")

dy_inv_exog = MRIO_df_to_vec(INV_model.dy_inv_exog, "REG_imp", "TRAD_COMM",
                             "dy", MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())

# Calculate output changes due to investment
dq_inv_induced, dq_inv_recyc, dq_inv_exog = IO_model.calc_dq_inv(
    A_trade, np.zeros_like(dy_inv_recyc), dy_inv_recyc, dy_inv_exog)

INV_model.calc_dy_inv_induced(IO_model, [dq_hh_exog_fd, dq_fcf_exog_fd, dq_gov_exog_fd])

dy_inv_induced = MRIO_df_to_vec(INV_model.dy_inv_induced,"REG_exp", "TRAD_COMM",
                                "dy", MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())    

dq_inv_induced, dq_inv_recyc, dq_inv_exog = IO_model.calc_dq_inv(
    A_trade, dy_inv_induced, dy_inv_recyc, dy_inv_exog)

print("--- Investment module: %s seconds ---" % round(time.time() - module_time, 1))

module_time = time.time()

# Build employment model
Empl_model = empl(MRIO_BASE)
Empl_model.build_empl_coef()
Empl_model.calc_empl_multiplier(MRIO_df_to_vec(Prod_cost.empl_base,"REG_imp","PROD_COMM","vol_total",MRIO_BASE.R['Region_acronyms'].to_list(),MRIO_BASE.P['Lfd_Nr'].to_list()), IO_model.q_base)



#%%

# Calculate employment changes due to output changes
dq_total = (dq_IO_eff + dq_hh_price + dq_hh_inc + dq_gov_recyc +
            dq_inv_induced + dq_inv_recyc + dq_inv_exog + dq_hh_exog_fd + dq_fcf_exog_fd + dq_gov_exog_fd + dq_supply_constraint)

[dempl_total, dempl_tech_eff, dempl_trade_eff, dempl_hh_price,
dempl_hh_inc, dempl_gov_recyc, dempl_inv_induced, dempl_inv_recyc,
dempl_inv_exog, dempl_hh_exog_fd, dempl_fcf_exog_fd, dempl_gov_exog_fd, dempl_supply_constraint] = Empl_model.calc_dempl(
    [dq_total, dq_tech_eff, dq_trade_eff, dq_hh_price, dq_hh_inc, dq_gov_recyc,
      dq_inv_induced, dq_inv_recyc, dq_inv_exog, dq_hh_exog_fd,
      dq_fcf_exog_fd, dq_gov_exog_fd, dq_supply_constraint])

# import pdb; pdb.set_trace()

print("--- Employment module: %s seconds ---" % round(time.time() - module_time, 1))

dq_total_iter = pd.concat([MRIO_BASE.mrio_id, pd.DataFrame(
    dq_total, columns = ["dq_0"])], axis=1)
dempl_total_iter = pd.concat([MRIO_BASE.mrio_id, pd.DataFrame(
    dempl_total, columns = ["dempl_0"])], axis=1)
dlabor_iter = pd.concat([MRIO_BASE.mrio_id, pd.DataFrame(
    np.zeros(dq_total.shape), columns = ["dlabor_0"])], axis=1)


#%%

# Iter_comment:
# Here we change labor income by using the % change in employment
# and multiply it with labor expenditure to get the additional labor income:
# abs_change_employment / empl_base * labor_expenditure      

Inc_model = income(MRIO_BASE, Prod_cost)

iter_run, hh_approx = 1, 0
dtax_rev, dlabor_nat = None, None
labor_diff, tax_diff = 0.07, 0.01

while True:
    iter_time = time.time()
    
    dtax_rev = Tax_rev.calc_tax_iter_cond(tax_rev_prod, dtax_rev)
    
    output = Inc_model.calc_output(dq_total)
    ind_ener_cou = Inc_model.collect_ener_flow(ind_trade, None, tax_rate)
    tax_rev_cou = Tax_rev.calc_tax_rev(tax_rate, ind_ener_cou)
    
    # Tax revenue from changes in household demand
    ind_ener_hh = Inc_model.collect_ener_flow_hh(HH_model, None, tax_rate_hh)
    tax_rev_hh = Tax_rev.calc_tax_rev_hh(tax_rate_hh, ind_ener_hh)
    
    labor_nat_base = Inc_model.calc_labor_nat_base()
    dlabor_sec = Inc_model.calc_labor_comp_change(dempl_total)
    dlabor_nat = Inc_model.calc_labor_iter_cond(dlabor_sec, dlabor_nat)
    dlabor_sec.columns = ["REG_imp", "PROD_COMM", f"dlabor_{iter_run}"]

    # rev_subtract_exp = BTA_cou.calc_rev_subtract_exp(tax_rev_cou)
    tax_rev_prod = Tax_rev.calc_tax_rev_prod(tax_rev_cou)
    recyc_rev = Tax_rev.calc_recyc_rev(
        tax_rev_prod, tax_rev_hh, rev_subtract_exp, rev_split)
    
    dtax_rev = Tax_rev.calc_tax_iter_cond(tax_rev_prod, dtax_rev)

    exog_prod_cost = Prod_cost.calc_prod_cost(tax_rev_prod, recyc_rev)

    # ! non-tax type price change (no recycling, no energy substitution)
    # ! this only has demand effects!
    exog_prod_cost = Prod_cost.prod_cost_impact(Scenario.cost_shock, exog_prod_cost)
    
    v_ener = Price_model.build_prod_cost_vector(exog_prod_cost)
    dL_ener = temp.read_from_pickle("dL_ener")
    dp_ener = Price_model.calc_dp_ener(v_ener, dL_ener)
    temp.save_to_pickle(dL_ener, "dL_ener")
    del dL_ener

    cbam_incidence = BTA_cou.calc_cbam_incidence(ind_ener_glo)
    dp_pre_trade = Price_model.calc_dp_pre_trade_bta(dp_ener, cbam_incidence)

    HH_price = HH_model.build_hh_price(dp_pre_trade, tax_rate_hh)
    # ! EH
    HH_price = HH_price.astype({'TRAD_COMM':'int'})
    HH_price_eff, HH_inc_eff = HH_model.calc_hh_demand_change(
        HH_price, recyc_rev, dlabor_nat)
    
    dy_hh_price = IO_model.build_dy_hh_price(HH_price_eff)
    dy_hh_inc = IO_model.build_dy_hh_inc(HH_inc_eff)

    # dy_hh_damage = IO_model.build_dy_hh_inc(HH_inc_eff)

    dy_hh_cons_change = IO_model.build_dy_hh_inc(HH_inc_eff)

    # Construct government model
    GOV_recyc = GOV_model.calc_gov_demand_change(recyc_rev)
    # dy_gov_recyc = IO_model.build_dy_gov_recyc(GOV_recyc)
    dy_gov_recyc = MRIO_df_to_vec(GOV_recyc.reset_index(), 'REG_exp', 'TRAD_COMM', 'delta_y_gov', MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())
    
    ind_trade = Trade_model.calc_IO_coef(ind_ener_glo, dp_pre_trade)
    # put the IO changes here, for no particular reason
    ind_trade = IO_model.io_change(io_changes, ind_trade)
    # Build new A matrix due to trade (import) substitution
    A_trade = IO_model.build_A_trade(ind_trade)
    # Print out the final A matrix (io coeff) 
    A_trade_out = pd.DataFrame(A_trade, index=IO_model.A_id, columns=IO_model.A_id)
    temp.write_to_csv(A_trade_out, "A_matrix_{}".format(scenario_name))
   
    # Calculate output changes for each driver of output change
    dq_IO_eff = IO_model.calc_dq_IO(A_trade)
    
    #print(np.allclose(A_trade, A_trade_original))
    #print(np.allclose(IO_model.y0, y0_original))
    
    dq_trade_eff = IO_model.calc_dq_trade(dq_IO_eff, dq_tech_eff)
    dq_hh_price, dq_hh_inc = IO_model.calc_dq_hh(A_trade, dy_hh_price, dy_hh_inc)
    dq_gov_recyc = IO_model.calc_dq_gov(A_trade, dy_gov_recyc)
    # import pdb; pdb.set_trace()

    dp_trade = Price_model.calc_dp_trade(A_trade, dp_ener, v_ener)

    # Calculate new final demand due to investment

    INV_model.calc_dy_inv_recyc(recyc_rev)
    dy_inv_recyc = MRIO_df_to_vec(INV_model.dy_inv_recyc,"REG_imp", "TRAD_COMM",
                                "dy", MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())

    # Calculate output changes due to investment
    dq_inv_induced, dq_inv_recyc, dq_inv_exog = IO_model.calc_dq_inv(
        A_trade, np.zeros_like(dy_inv_recyc), dy_inv_recyc, dy_inv_exog)

    INV_model.calc_dy_inv_induced(IO_model, [dq_hh_exog_fd, dq_fcf_exog_fd, dq_gov_exog_fd])
    
    dy_inv_induced = MRIO_df_to_vec(INV_model.dy_inv_induced,"REG_exp", "TRAD_COMM",
                                "dy", MRIO_BASE.R['Region_acronyms'].to_list(), MRIO_BASE.P['Lfd_Nr'].to_list())   
    
    dq_inv_induced, dq_inv_recyc, dq_inv_exog = IO_model.calc_dq_inv(
        A_trade, dy_inv_induced, dy_inv_recyc, dy_inv_exog)

    # TODO

    # Re-calculate dq_total
    dq_total = (dq_IO_eff + dq_hh_price + dq_hh_inc + dq_gov_recyc +
                dq_inv_induced + dq_inv_recyc + dq_inv_exog + dq_hh_exog_fd +
                  dq_fcf_exog_fd + dq_gov_exog_fd + dq_supply_constraint)

    [dempl_total, dempl_tech_eff, dempl_trade_eff, dempl_hh_price,
    dempl_hh_inc, dempl_gov_recyc, dempl_inv_induced, dempl_inv_recyc,
    dempl_inv_exog, dempl_supply_constraint, dempl_hh_exog_fd, 
    dempl_fcf_exog_fd, dempl_gov_exog_fd] = Empl_model.calc_dempl(
        [dq_total, dq_tech_eff, dq_trade_eff, dq_hh_price, dq_hh_inc, dq_gov_recyc,
          dq_inv_induced, dq_inv_recyc, dq_inv_exog, dq_supply_constraint, dq_hh_exog_fd,
          dq_fcf_exog_fd, dq_gov_exog_fd])
    
    dq_total_iter = pd.concat([dq_total_iter, pd.DataFrame(
        dq_total, columns = [f"dq_{iter_run}"])], axis=1)

    dempl_total_iter = pd.concat([dempl_total_iter, pd.DataFrame(
        dempl_total, columns = [f"dempl_{iter_run}"])], axis=1)
    
    dlabor_iter = pd.concat([dlabor_iter, pd.DataFrame(
        dlabor_sec, columns = [f"dlabor_{iter_run}"])], axis=1)
    
    if iter_run > 1:
        labor_cond_q1 = abs(
            dlabor_nat["dlabor"]/dlabor_nat["dlabor_before"] - 1).quantile(0.25)
        labor_cond_q3 = abs(
            dlabor_nat["dlabor"]/dlabor_nat["dlabor_before"] - 1).quantile(0.75)
        labor_cond = labor_cond_q3 + 1.5 * (labor_cond_q3 - labor_cond_q1)
    else:
        labor_cond = np.inf
    
    if dtax_rev["tax_rev_prod"].sum() == 0:	
        tax_rev_cond = 0	
    else:	
        dtax_rev_ = dtax_rev[dtax_rev['tax_rev_before']!=0]
        tax_rev_cond = max(np.nan_to_num(abs(	
            dtax_rev_["tax_rev_prod"]/dtax_rev_["tax_rev_before"] - 1), nan=0.0))
    
    print(f"--- Iteration #{iter_run}: {round(time.time() - iter_time, 1)} seconds ---")
    print(f"--- Labor compensation relative diff.: {round(labor_cond * 100, 1)}% ---")
    print(f"--- Tax revenue relative diff.: {round(tax_rev_cond * 100, 1)}% ---")
    
    if (labor_cond < labor_diff and tax_rev_cond < tax_diff):
        break
    
    iter_run += 1

module_time = time.time()
    
GDP_model = GDP(IO_model)
gdp_base = GDP_model.calc_gdp_base()

#%%

[dgdp_total, dgdp_tech_eff, dgdp_trade_eff, dgdp_hh_price,
dgdp_hh_inc, dgdp_gov_recyc, dgdp_inv_induced, dgdp_inv_recyc,
dgdp_inv_exog, dgdp_supply_constraint, dgdp_hh_exog_fd,  
dgdp_fcf_exog_fd, dgdp_gov_exog_fd] = GDP_model.calc_gdp_changes(
    [dq_total, dq_tech_eff, dq_trade_eff, dq_hh_price, dq_hh_inc, dq_gov_recyc,
      dq_inv_induced, dq_inv_recyc, dq_inv_exog, dq_supply_constraint, dq_hh_exog_fd,
      dq_fcf_exog_fd, dq_gov_exog_fd], A_trade)

print("--- GDP module: %s seconds ---" % round(time.time() - module_time, 1))
    
# Output changes
output_change = pd.concat([MRIO_BASE.mrio_list, pd.DataFrame(
    IO_model.q_base, columns = ["q_base"])], axis=1)
dq_list = ["dq_tech_eff", "dq_trade_eff", "dq_hh_price", "dq_hh_inc","dq_gov_recyc",
           "dq_inv_induced", "dq_inv_recyc", "dq_inv_exog", "dq_supply_constraint", 
           "dq_hh_exog_fd","dq_fcf_exog_fd","dq_gov_exog_fd","dq_total"]

for i in dq_list:
    output_change = pd.concat(
        [output_change, pd.DataFrame(globals()[i], columns = [i])], axis=1)
    
# Employment changes
empl_change = MRIO_BASE.mrio_list.merge(	
    Prod_cost.empl_base, how='left', left_on = ["Reg_ID", "Sec_ID"],	
    right_on = ["REG_imp", "PROD_COMM"])	
empl_change = empl_change.drop(columns=["REG_imp", "PROD_COMM"])
empl_change = empl_change.rename(columns={"vol_total":"empl_base"})
dempl_list = ["dempl_tech_eff", "dempl_trade_eff", "dempl_hh_price", "dempl_hh_inc",
              "dempl_gov_recyc", "dempl_inv_induced", "dempl_inv_recyc", "dempl_inv_exog",
              "dempl_supply_constraint","dempl_hh_exog_fd", "dempl_fcf_exog_fd", "dempl_gov_exog_fd", "dempl_total"]

for i in dempl_list:
    empl_change = pd.concat(
        [empl_change, pd.DataFrame(globals()[i], columns = [i])], axis=1)

# GDP changes
gdp_change = pd.concat([MRIO_BASE.mrio_list, pd.DataFrame(
    gdp_base, columns = ["gdp_base"])], axis=1)
dgdp_list = ["dgdp_tech_eff", "dgdp_trade_eff", "dgdp_hh_price", "dgdp_hh_inc",
             "dgdp_gov_recyc", "dgdp_inv_induced", "dgdp_inv_recyc", "dgdp_inv_exog",
             "dgdp_supply_constraint", "dgdp_hh_exog_fd", "dgdp_fcf_exog_fd", "dgdp_gov_exog_fd", "dgdp_total"]

for i in dgdp_list:
    gdp_change = pd.concat(
        [gdp_change, pd.DataFrame(globals()[i], columns = [i])], axis=1)

# Price changes
price_change = MRIO_BASE.mrio_list.copy()
price_list = ["dp_base", "dp_ener", "dp_trade"]

for i in price_list:
    price_change = pd.concat(
        [price_change, pd.DataFrame(globals()[i], columns = [i])], axis=1)

total_revenue = Tax_rev.build_tax_rev_result(tax_rev_prod, tax_rev_hh)
total_revbase = Tax_rev.build_tax_rev_result(
    tax_rev_prod_base.rename(columns = {"tax_rev_prod_base": "tax_rev_prod"}),
    tax_rev_hh_base.rename(columns = {"tax_rev_hh_base": "tax_rev_hh"}))
total_revbase = total_revbase.rename(columns = {"tax_rev_prod": "tax_rev_prod_base"})
total_revenue = total_revenue.merge(total_revbase, how="left", on =["REG_imp", "PROD_COMM"])
total_revenue = total_revenue.rename(columns = {'REG_imp':'Reg_ID','PROD_COMM':'Sec_ID'})

dy_inv_induced_vec = INV_model.dy_inv_induced\
    .groupby(['REG_imp','TRAD_COMM']).agg({'dy':'sum'}).reset_index()\
    .rename(columns={'REG_imp':'Reg_ID','TRAD_COMM':'Sec_ID','dy':'dy_inv_induced'})\
    [['Reg_ID','Sec_ID','dy_inv_induced']].astype({'Sec_ID':'int16'})
dy_inv_recyc_vec = INV_model.dy_inv_recyc\
    .groupby(['REG_imp','TRAD_COMM']).agg({'dy':'sum'}).reset_index()\
    .rename(columns={'REG_imp':'Reg_ID','TRAD_COMM':'Sec_ID','dy':'dy_inv_recyc'})\
    [['Reg_ID','Sec_ID','dy_inv_recyc']].astype({'Sec_ID':'int16'})
dy_inv_exog_vec = INV_model.dy_inv_exog\
    .groupby(['REG_imp','TRAD_COMM']).agg({'dy':'sum'}).reset_index()\
    .rename(columns={'REG_imp':'Reg_ID','TRAD_COMM':'Sec_ID','dy':'dy_inv_exog'})\
    [['Reg_ID','Sec_ID','dy_inv_exog']].astype({'Sec_ID':'int16'})
dy_hh_price_vec = MRIO_vec_to_df(dy_hh_price, "dy_hh_price", MRIO_BASE.R)\
    .rename(columns={'target-country-iso3':'Reg_ID','target-sector':'Sec_ID'})\
    [['Reg_ID','Sec_ID','dy_hh_price']].astype({'Sec_ID':'int16'})
dy_hh_inc_vec = MRIO_vec_to_df(dy_hh_inc, "dy_hh_inc", MRIO_BASE.R)\
    .rename(columns={'target-country-iso3':'Reg_ID','target-sector':'Sec_ID'})\
    [['Reg_ID','Sec_ID','dy_hh_inc']].astype({'Sec_ID':'int16'})
dy_hh_exog_fd_vec = MRIO_vec_to_df(dy_hh_exog_fd, "dy_hh_exog_fd", MRIO_BASE.R)\
    .rename(columns={'target-country-iso3':'Reg_ID','target-sector':'Sec_ID'})\
    [['Reg_ID','Sec_ID','dy_hh_exog_fd']].astype({'Sec_ID':'int16'})
dy_gov_exog_fd_vec = MRIO_vec_to_df(dy_gov_exog_fd, "dy_gov_exog_fd", MRIO_BASE.R)\
    .rename(columns={'target-country-iso3':'Reg_ID','target-sector':'Sec_ID'})\
    [['Reg_ID','Sec_ID','dy_gov_exog_fd']].astype({'Sec_ID':'int16'})
dy_fcf_exog_fd_vec = MRIO_vec_to_df(dy_fcf_exog_fd, "dy_fcf_exog_fd", MRIO_BASE.R)\
    .rename(columns={'target-country-iso3':'Reg_ID','target-sector':'Sec_ID'})\
    [['Reg_ID','Sec_ID','dy_fcf_exog_fd']].astype({'Sec_ID':'int16'})
dy_gov_recyc_vec = MRIO_vec_to_df(dy_gov_recyc, "dy_gov_recyc", MRIO_BASE.R)\
    .rename(columns={'target-country-iso3':'Reg_ID','target-sector':'Sec_ID'})\
    [['Reg_ID','Sec_ID','dy_gov_recyc']].astype({'Sec_ID':'int16'})

dy_df = dy_hh_inc_vec.merge(dy_hh_price_vec, how="outer").merge(dy_inv_exog_vec, how="outer")\
    .merge(dy_inv_recyc_vec, how="outer").merge(dy_inv_induced_vec, how="outer")\
        .merge(dy_hh_exog_fd_vec, how='outer').merge(dy_gov_exog_fd_vec, how='outer')\
            .merge(dy_fcf_exog_fd_vec,how='outer').merge(dy_gov_recyc_vec, how='outer').fillna(0)

hh_change = pd.concat(
    [HH_model.HH, HH_model.dHH_inc, HH_model.dHH_price], axis=1)
hh_change.columns = ["HH_base", "dHH_inc_eff", "dHH_price_eff"]
hh_change = hh_change.groupby(["REG_imp", "TRAD_COMM"]).sum().reset_index()

hh_change = MRIO_BASE.mrio_list.merge(
    hh_change, how="left", left_on=["Reg_ID", "Sec_ID"],
    right_on=["REG_imp", "TRAD_COMM"])
hh_change = hh_change.drop(columns=["REG_imp", "TRAD_COMM"]).fillna(0)
#%% 
del ind_ener_glo
# del ind_trade
del INV_model
gc.collect()

#%%

Energy_emissions = ener_balance(MRIO_BASE, Scenario)
emissions = Energy_emissions.delta_emissions(dq_total, A_trade, IO_model.A_BASE, IO_model.q_base)
emissions = emissions.astype({'target-sector':'int16'})
emissions = MRIO_BASE.mrio_list.merge(emissions, how='left', left_on=['Reg_ID','Sec_ID'], right_on=['target-country-iso3','target-sector'])
emissions = emissions.drop(columns=['target-country-iso3','target-sector']).fillna(0)
emissions = emissions.groupby(['Reg_ID','Sec_ID']).agg({'deltaPollutant':'sum', 'qPollutant':'sum',
                                                                                    'deltaProcess':'sum', 'qProcess':'sum', 
                                                                                    'deltaPollutant_nostructuralchange':'sum'}).reset_index()

# this only if emissions are NOT needed
# dummy_emissions = pd.DataFrame(columns=['Reg_ID','Sec_ID','deltaPollutant','qPollutant','deltaProcess','deltaPollutant_nostructuralchange'])
# emissions = dummy_emissions

Results = results(scenario=scenario_name,regions=MRIO_BASE.R)
results_list = [output_change, empl_change, gdp_change, hh_change, dy_df, price_change, total_revenue, emissions]
iter_list = [dq_total_iter, dempl_total_iter]

# adjust with residuals from endogenous baseline
results_list_adj = Results.adj_residuals(results_list,residuals_file, 2019) #type: ignore

Results.save_change(None, results_list_adj, iter_list, 2019)

#%%

# Export IND_BASE new; we're cheating
# first we multiple A matrix from down (i.e., column-wise)
# total_output = IO_model.q_base + dq_total
# IND_BASE_new = A_trade * total_output
# Results.save_INDBASE(IND_BASE_new, total_output, "GLORIA_db\\IND_BASE_new.pkl")

# del IND_BASE_new

# if scenario_name == 'Botswana&Namibia_S2_2050_supply_dryhot':

#     # 1st BASE
#     MRIO_1 = IO_model.A_BASE * IO_model.q_base.T
#     Results.save_io(MRIO_1, "MRIO_base")
#     del MRIO_1
#     MRIO_2 = IO_model.A_BASE * (IO_model.q_base + dq_total).T
#     Results.save_io(MRIO_2, "MRIO_impact_old_IO", append_to_file="GLORIA_results\\io_{}_{}.parquet".format(scenario_name, "MRIO_1"))
#     del MRIO_2
#     MRIO_3 = A_trade * (IO_model.q_base + dq_total).T
#     Results.save_io(MRIO_3, "MRIO_impact_new_IO", append_to_file="GLORIA_results\\io_{}_{}.parquet".format(scenario_name, "MRIO_2"))
#     del MRIO_3
#     MRIO_4 = A_trade * IO_model.q_base.T
#     Results.save_io(MRIO_4, "MRIO_noimpact_new_IO", append_to_file="GLORIA_results\\io_{}_{}.parquet".format(scenario_name, "MRIO_3"))
#     del MRIO_4
    
    # save IO and effect disaggregation

print("--- Model run: %s seconds ---" % round(time.time() - start_time, 1))
