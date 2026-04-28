# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 16:10:16 2023

@author: wb582890
"""

countries = ["IDN", "COL", "MEX", # ["BRA", "TUR", 
             "PAK", "PHL", "THA", "EGY", "ZAF"]

for country in countries:
    
    import numpy as np
    import pandas as pd
    import time
    # import gc

    from SourceCode.exog_vars_loop import exog_vars
    from SourceCode.scenario import scenario
    from SourceCode.ener_elas import ener_elas 
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

    start_time = time.time()

    module_time = time.time()

    iter_results, full_results = 1, 0
    bta = 0 # no BTA

    # RE inv. type: Turn off line 217 and 220 if not applied
    re_inv = "Wind offshore" 

    # INITIALIZE exogenous variables (excluding scenario variables)
    MRIO_BASE = exog_vars(country)
    print(f"Studied country: {country}")

    print("--- Exogenous variables: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Construct scenario module
    Scenario = scenario(MRIO_BASE.scenario_path)
    tax_rate, tax_rate_hh = Scenario.set_tax_rate()
    tax_cou = Scenario.enlist_tax_cou()
    rev_split = Scenario.build_rev_split()
    payr_tax_split = Scenario.build_payr_tax_split()
    rev_proportion = Scenario.build_rev_proportion()
    govt_spending = Scenario.build_govt_spending()
    inv_spending = Scenario.build_inv_spending()

    print("--- Scenario: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Construct energy elasticities module
    Ener_model = ener_elas(MRIO_BASE)

    # Build energy elasticities dataframe and assign tax rate information
    Ener_model.build_ener_elas()
    Ener_model.assign_tax_cou(tax_cou)
    Ener_model.assign_tax_rate(MRIO_BASE.IND_BASE, tax_rate)

    # Calculate technical and IO coefficients due to energy elasticities
    tech_coef_ener = Ener_model.calc_tech_coef_ener()
    ind_ener_cou = Ener_model.assign_IO_coef_cou(
        MRIO_BASE.IND_BASE, tech_coef_ener)
    ind_ener_glo = Ener_model.assign_IO_coef_glo(
        MRIO_BASE.IND_BASE, ind_ener_cou)

    # Build helper matrices for energy commodities
    tax_index, tax_matrix, sec_matrix = Ener_model.build_tax_helper_matrix(ind_ener_cou)

    print("--- Energy module: %s seconds ---" % round(time.time() - module_time, 1))

    # Construct BTA module
    BTA_cou = BTA(Scenario, bta)

    module_time = time.time()

    # Construct tax revenue module
    Tax_rev = tax_rev(MRIO_BASE, ind_ener_cou, tax_cou)

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

    # Construct production module (exogenous production cost)
    Prod_cost = prod_cost(MRIO_BASE, Scenario)

    # Construct Input-Output model
    IO_model = IO(MRIO_BASE)
    IO_model.initialize()

    # Build employment model
    Empl_model = empl(MRIO_BASE)
    Empl_model.build_empl_coef()

    # Calculate wage share, employment share, labor compensation, and its national share
    wage_share, empl_share, labor_share = Prod_cost.calc_shares()

    empl_multiplier = Empl_model.calc_empl_multiplier(
        Prod_cost.empl_base, IO_model.q_base)

    empl_multiplier_base = empl_multiplier.copy()

    # Calculate new relative exogenous production cost
    exog_prod_cost_base, empl_multiplier_payroll_base = Prod_cost.calc_prod_cost_base(
        tax_rev_prod_base, recyc_rev_base, empl_multiplier_base)
    exog_prod_cost, empl_multiplier_payroll = Prod_cost.calc_prod_cost(
        tax_rev_prod, recyc_rev, empl_multiplier_base)

    Empl_model.assign_empl_multiplier(empl_multiplier_payroll)

    print("--- Prod. cost module: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Calculate changes in Leontief matrix for energy commodities
    dL_ener = IO_model.build_dL_ener(
        tax_index, tax_matrix, sec_matrix)
    # Calculate output change due to energy elasticities
    dq_tech_eff = IO_model.calc_dq_energy(dL_ener)

    del tax_index, tax_matrix, sec_matrix

    print("--- IO module: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Construct price model
    Price_model = price(MRIO_BASE, IO_model.L_BASE, BTA_cou)
    v_base = Price_model.build_prod_cost_base_vector(exog_prod_cost_base)
    v_ener = Price_model.build_prod_cost_vector(exog_prod_cost)

    dp_base = Price_model.calc_dp_base(v_base)
    dp_ener = Price_model.calc_dp_ener(v_ener, dL_ener)

    del v_base, dL_ener

    if bta != 0:
        dp_pre_trade = Price_model.calc_dp_pre_trade_bta(dp_ener)
    else:
        dp_pre_trade = Price_model.calc_dp_pre_trade(dp_ener)

    print("--- Price pre-trade: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Construct household model
    HH_model = hh(MRIO_BASE)
    HH_model.build_hh_elas()
    HH_price = HH_model.build_hh_price(dp_pre_trade, tax_rate_hh)
    HH_price_eff, HH_inc_eff = HH_model.calc_hh_demand_change(HH_price, recyc_rev)

    dy_hh_price = IO_model.build_dy_hh_price(HH_price_eff)
    dy_hh_inc = IO_model.build_dy_hh_inc(HH_inc_eff)

    print("--- Household module: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Construct government model
    GOV_model = gov(MRIO_BASE, Scenario)
    GOV_model.calc_trade_share()
    GOV_recyc = GOV_model.calc_gov_demand_change(recyc_rev)

    dy_gov_recyc = IO_model.build_dy_gov_recyc(GOV_recyc)

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
    dq_trade_eff = IO_model.calc_dq_trade(dq_IO_eff, dq_tech_eff)
    dq_hh_price, dq_hh_inc = IO_model.calc_dq_hh(A_trade, dy_hh_price, dy_hh_inc)
    dq_gov_recyc = IO_model.calc_dq_gov(A_trade, dy_gov_recyc)

    print("--- Quantity module: %s seconds ---" % round(time.time() - module_time, 1))

    # Calculate price changes
    module_time = time.time()

    dp_trade = Price_model.calc_dp_trade(A_trade, dp_ener, v_ener)

    print("--- Price post-trade: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Construct investment model
    INV_model = invest(MRIO_BASE, Scenario)
    inv_output_elas = INV_model.build_inv_output_elas()
    # re_invest = INV_model.build_re_inv("OECD")

    inv_conv = INV_model.build_inv_conv()
    # inv_conv = INV_model.assign_ely_tech(re_inv)

    inv_share = INV_model.calc_inv_share()

    # Calculate new final demand due to investment
    INV_induced = INV_model.calc_dy_inv_induced(IO_model) 
    INV_recyc = INV_model.calc_dy_inv_recyc(recyc_rev)
    INV_added = INV_model.calc_dy_inv_added()

    dy_inv_induced = IO_model.build_dy_inv(INV_induced)
    dy_inv_recyc = IO_model.build_dy_inv(INV_recyc)
    dy_inv_added = IO_model.build_dy_inv(INV_added)

    # Calculate output changes due to investment
    dq_inv_induced, dq_inv_recyc, dq_inv_added = IO_model.calc_dq_inv(
        A_trade, dy_inv_induced, dy_inv_recyc, dy_inv_added)

    print("--- Investment module: %s seconds ---" % round(time.time() - module_time, 1))

    module_time = time.time()

    # Calculate employment changes due to output changes
    dq_total = (dq_IO_eff + dq_hh_price + dq_hh_inc + dq_gov_recyc +
                dq_inv_induced + dq_inv_recyc + dq_inv_added)

    [dempl_total, dempl_tech_eff, dempl_trade_eff, dempl_hh_price,
    dempl_hh_inc, dempl_gov_recyc, dempl_inv_induced, dempl_inv_recyc,
    dempl_inv_added] = Empl_model.calc_dempl(
        [dq_total, dq_tech_eff, dq_trade_eff, dq_hh_price, dq_hh_inc, dq_gov_recyc,
          dq_inv_induced, dq_inv_recyc, dq_inv_added])

    print("--- Employment module: %s seconds ---" % round(time.time() - module_time, 1))

    dq_total_iter = pd.concat([MRIO_BASE.mrio_id, pd.DataFrame(
        dq_total, columns = ["dq_0"])], axis=1)
    dempl_total_iter = pd.concat([MRIO_BASE.mrio_id, pd.DataFrame(
        dempl_total, columns = ["dempl_0"])], axis=1)
    dlabor_iter = pd.concat([MRIO_BASE.mrio_id, pd.DataFrame(
        np.zeros(dq_total.shape), columns = ["dlabor_0"])], axis=1)

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
        ind_ener_cou = Inc_model.collect_ener_flow(ind_trade, tax_cou, tax_rate)
        tax_rev_cou = Tax_rev.calc_tax_rev(tax_rate, ind_ener_cou)
        del ind_trade
        
        # Tax revenue from changes in household demand
        ind_ener_hh = Inc_model.collect_ener_flow_hh(HH_model, tax_cou, tax_rate_hh)
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

        exog_prod_cost, empl_multiplier_payroll = Prod_cost.calc_prod_cost(
            tax_rev_prod, recyc_rev, empl_multiplier_base)

        Empl_model.assign_empl_multiplier(empl_multiplier_payroll)

        v_ener = Price_model.build_prod_cost_vector(exog_prod_cost)
        # dp_ener = Price_model.calc_dp_ener(v_ener, dL_ener)

        if bta != 0:
            dp_pre_trade = Price_model.calc_dp_pre_trade_bta(dp_ener)
        else:
            dp_pre_trade = Price_model.calc_dp_pre_trade(dp_ener)

        HH_price = HH_model.build_hh_price(dp_pre_trade, tax_rate_hh)
        HH_price_eff, HH_inc_eff = HH_model.calc_hh_demand_change(
            HH_price, recyc_rev, dlabor_nat)

        dy_hh_price = IO_model.build_dy_hh_price(HH_price_eff)
        dy_hh_inc = IO_model.build_dy_hh_inc(HH_inc_eff)

        # Construct government model
        GOV_recyc = GOV_model.calc_gov_demand_change(recyc_rev)
        dy_gov_recyc = IO_model.build_dy_gov_recyc(GOV_recyc)
        
        ind_trade = Trade_model.calc_IO_coef(ind_ener_glo, dp_pre_trade)

        # Build new A matrix due to trade (import) substitution
        A_trade = IO_model.build_A_trade(ind_trade)

        # Calculate output changes for each driver of output change
        dq_IO_eff = IO_model.calc_dq_IO(A_trade)
        dq_trade_eff = IO_model.calc_dq_trade(dq_IO_eff, dq_tech_eff)
        dq_hh_price, dq_hh_inc = IO_model.calc_dq_hh(A_trade, dy_hh_price, dy_hh_inc)
        dq_gov_recyc = IO_model.calc_dq_gov(A_trade, dy_gov_recyc)

        dp_trade = Price_model.calc_dp_trade(A_trade, dp_ener, v_ener)

        # Calculate new final demand due to investment
        INV_induced = INV_model.calc_dy_inv_induced(IO_model) 
        INV_recyc = INV_model.calc_dy_inv_recyc(recyc_rev)

        dy_inv_induced = IO_model.build_dy_inv(INV_induced)
        dy_inv_recyc = IO_model.build_dy_inv(INV_recyc)

        # Calculate output changes due to investment
        dq_inv_induced, dq_inv_recyc, dq_inv_added = IO_model.calc_dq_inv(
            A_trade, dy_inv_induced, dy_inv_recyc, dy_inv_added)

        # Calculate employment changes due to output changes
        dq_total = (dq_IO_eff + dq_hh_price + dq_hh_inc + dq_gov_recyc +
                    dq_inv_induced + dq_inv_recyc + dq_inv_added)

        [dempl_total, dempl_tech_eff, dempl_trade_eff, dempl_hh_price,
        dempl_hh_inc, dempl_gov_recyc, dempl_inv_induced, dempl_inv_recyc,
        dempl_inv_added] = Empl_model.calc_dempl(
            [dq_total, dq_tech_eff, dq_trade_eff, dq_hh_price, dq_hh_inc, dq_gov_recyc,
              dq_inv_induced, dq_inv_recyc, dq_inv_added])
        
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
            tax_rev_cond = max(np.nan_to_num(abs(	
                dtax_rev["tax_rev_prod"]/dtax_rev["tax_rev_before"] - 1), 0))
        
        print(f"--- Iteration #{iter_run}: {round(time.time() - iter_time, 1)} seconds ---")
        print(f"--- Labor compensation relative diff.: {round(labor_cond * 100, 1)}% ---")
        print(f"--- Tax revenue relative diff.: {round(tax_rev_cond * 100, 1)}% ---")
        
        if (labor_cond < labor_diff and tax_rev_cond < tax_diff):
            break
        
        del dq_trade_eff, dq_hh_price, dq_hh_inc, dq_gov_recyc, dq_inv_induced, dq_inv_recyc, dq_inv_added
        del dempl_tech_eff, dempl_trade_eff, dempl_hh_price, dempl_hh_inc, dempl_gov_recyc, dempl_inv_induced, dempl_inv_recyc, dempl_inv_added
        
        iter_run += 1

    module_time = time.time()
        
    GDP_model = GDP(IO_model)
    gdp_base = GDP_model.calc_gdp_base()

    [dgdp_total, dgdp_tech_eff, dgdp_trade_eff, dgdp_hh_price,
    dgdp_hh_inc, dgdp_gov_recyc, dgdp_inv_induced, dgdp_inv_recyc,
    dgdp_inv_added] = GDP_model.calc_gdp_changes(
        [dq_total, dq_tech_eff, dq_trade_eff, dq_hh_price, dq_hh_inc, dq_gov_recyc,
          dq_inv_induced, dq_inv_recyc, dq_inv_added], A_trade)

    print("--- GDP module: %s seconds ---" % round(time.time() - module_time, 1))
        
    # Output changes
    output_change = pd.concat([MRIO_BASE.mrio_list, pd.DataFrame(
        IO_model.q_base, columns = ["q_base"])], axis=1)
    dq_list = ["dq_tech_eff", "dq_trade_eff", "dq_hh_price", "dq_hh_inc","dq_gov_recyc",
               "dq_inv_induced", "dq_inv_recyc", "dq_inv_added", "dq_total"]

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
                  "dempl_gov_recyc", "dempl_inv_induced", "dempl_inv_recyc", "dempl_inv_added",
                  "dempl_total"]

    for i in dempl_list:
        empl_change = pd.concat(
            [empl_change, pd.DataFrame(globals()[i], columns = [i])], axis=1)

    # GDP changes
    gdp_change = pd.concat([MRIO_BASE.mrio_list, pd.DataFrame(
        gdp_base, columns = ["gdp_base"])], axis=1)
    dgdp_list = ["dgdp_tech_eff", "dgdp_trade_eff", "dgdp_hh_price", "dgdp_hh_inc",
                 "dgdp_gov_recyc", "dgdp_inv_induced", "dgdp_inv_recyc", "dgdp_inv_added",
                 "dgdp_total"]

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

    hh_change = pd.concat(
        [HH_model.HH, HH_model.dHH_inc, HH_model.dHH_price], axis=1)
    hh_change.columns = ["HH_base", "dHH_inc_eff", "dHH_price_eff"]
    hh_change = hh_change.groupby(["REG_imp", "TRAD_COMM"]).sum().reset_index()

    hh_change = MRIO_BASE.mrio_list.merge(
        hh_change, how="left", left_on=["Reg_ID", "Sec_ID"],
        right_on=["REG_imp", "TRAD_COMM"])
    hh_change = hh_change.drop(columns=["REG_imp", "TRAD_COMM"]).fillna(0)

    Results = results()
    results_list = [output_change, empl_change, gdp_change, hh_change, price_change, total_revenue]
    iter_list = [dq_total_iter, dempl_total_iter]

    Results.save_change(tax_cou, results_list, iter_list)

    print("--- Model run: %s seconds ---" % round(time.time() - start_time, 1))
    
    gl = globals().copy()
    
    for var in gl:
        if var == 'countries': continue
        if var == 'country': continue
        
        # if 'func' in str(globals()[var]): continue
        # if 'module' in str(globals()[var]): continue

        del globals()[var]
    
    del gl
    
    import gc
    
    gc.collect()
    
    print(f"Country done: {country}")
