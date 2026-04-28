# MINDSET_module

### Content

- RunMINDSET.py: This file is the MAIN working script to run MINDSET model iteratively (not year-to-year).
- MINDSET.py: This file contains methods to run the prototype year-to-year MINDSET model using script RunMINDSET_yearly.py
- RunMINDSET_stepwise.py: This file is an artifact for non-iterative MINDSET model (Without income loop). Could be useful for testing new functions or changes.
- RunMINDSET_yearly.py: This file is the main working script to run the prototype MINDSET model in year-to-year.
- Results_plot.R: This file is an R script to visualize the results Excel file.
- MINDSET_module.Rproj: This file is an R project file for plot visualization.

### Subfolder SourceCode

## exog_vars.py:
This file contains exog_vars module, extracting all exogenous variables enlisted in Variable_list_MINDSET.xlsx

#### Input:
- var_path: location of root folder containing variable list and exogenous variables in MINDSET model.

#### Output:
Variables in capital letters imply that they are exogenous variables.
- IND_BASE: Interindustry flows (including IO and technical coefficients)
- COU_ID: List of country IDs
- COU_NAME: List of country names
- SEC_ID: List of sector IDs
- SEC_NAME: List of sector names
- VA_BASE: Value-added (capital cons., labor comp., taxes)
- LABOR_BASE: Employment and wage
- HH_BASE: Household consumption final demand
- NPISH_BASE: Non-profit institution consumption final demand
- GOV_BASE: Government consumption final demand
- FCF_BASE: Investment consumption final demand
- EN_OP_ELAS: Own-price energy elasticities
- EN_CP_ELAS_COU: Energy cross-price elasticities of specific countries
- EN_CP_ELAS_ROA: Energy cross-price elasticities in rest of Asia
- EN_CP_ELAS_ROE: Energy cross-price elasticities in rest of Europe
- EN_CP_ELAS_ROW: Energy cross-price elasticities in rest of the world
- EN_CP_ELAS_CONC: Energy cross-price elasticities concordance
- L_BASE: Initial Leontief matrix
- Y_BASE: Initial final demand matrix
- HH_INC_COU_MAP: Country mapping based on income level (for household module)
- HH_INC_ELAS: Household income elasticities data
- HH_OP_ELAS: Household own-price elasticities data
- HH_CP_ELAS_LOW: Household cross-price elasticities data for low-income countries
- HH_CP_ELAS_MID: Household cross-price elasticities data for mid-income countries
- HH_CP_ELAS_HIGH: Household cross-price elasticities data for high-income countries
- TRADE_ELAS: Trade elasticities by industrial sectors
- INV_CONV: Investment conversion matrix (from sectors into commodities)
- INV_OUTPUT_ELAS: Country- and sector-specific investment-output elasticities (induced investment)
- ADD_INV: Added investment exogenously from investment template
- RE_INVEST: Renewable investment conversion matrix (from selected electricity technology into commodities)
- EMPL_COEF: Country- and sector-specific employment-output elasticities

## scenario.py
This file contains scenario module, collecting tax incidence.

#### Input:
- SCENARIO: Scenario template file location

#### Output:
- tax_rate: Carbon tax rate for each fuel and sector
- tax_rate_hh: Carbon tax rate for each fuel in households
- tax_cou: List of countries being taxed
- rev_split: Split of tax revenue into different policy channels
- payr_tax_split: Split of tax revenue into payroll tax by skill (artifact variable)
- rev_proportion: Choice of allocated revenue spending into government (default or user-defined)
- govt_spending: Sectoral split of tax revenue allocated into government spending (user-defined)
- inv_spending: Sectoral split of tax revenue allocated into public investment (user-defined)

## ener_elas.py
This file contains energy elasticities module, simulating energy efficiency and interfuel substitution.

#### Input:
- IND_BASE: Interindustry flows (including IO and technical coefficients)
- EN_OP_ELAS: Own-price energy elasticities
- EN_CP_ELAS_COU: Energy cross-price elasticities of specific countries
- EN_CP_ELAS_ROA: Energy cross-price elasticities in rest of Asia
- EN_CP_ELAS_ROE: Energy cross-price elasticities in rest of Europe
- EN_CP_ELAS_ROW: Energy cross-price elasticities in rest of the world
- EN_CP_ELAS_CONC: Energy cross-price elasticities concordance
- L_BASE: Initial Leontief matrix

#### Output:
- tech_coef_ener: Technical coefficients after energy substitution for taxed countries
- ind_ener_cou: IO coefficients after energy substitution for taxed countries
- ind_ener_glo: IO coefficients after energy substitution (global)
- tax_index: Vector of country and industrial sectors being taxed
- tax_matrix: Tax rate matrix
- sec_matrix: Binary (1-0) matrix containing sectors being taxed

## tax_rev.py
This file contains tax revenue module, calculating tax revenue before and after substitution effects.

#### Input:
- ind_ener_cou: IO coefficients after energy substitution for taxed countries
- tax_cou: List of countries being taxed
- tax_rate: Carbon tax rate for each fuel and sector
- tax_rate_hh: Carbon tax rate for each fuel in households

#### Output:
- tax_rev_cou_base: Tax revenue collected from each industry flow (before output change from energy elasticities)
- tax_rev_cou: Tax revenue collected from each industry flow
- tax_rev_hh_base: Tax revenue collected from households (before consumption change from energy elasticities)
- tax_rev_hh: Tax revenue collected from households
- rev_subtract_exp_base: Tax revenue subtracted from export BTA (before consumption change from energy elasticities)
- rev_subtract_exp: Tax revenue subtracted from export BTA
- tax_rev_prod_base: Tax revenue aggregated for each industrial sector (before output change from energy elasticities)
- tax_rev_prod: Tax revenue aggregated for each industrial sector
- recyc_rev_base: Tax revenue recycled into policy channels (before output change from energy elasticities)
- recyc_rev: Tax revenue recycled into policy channels

## BTA.py
This file contains BTA module, simulating sectors impacted by BTA and substracts the tax revenue accordingly.

#### Input:
- SCENARIO: Scenario template file location
- bta: BTA parameter (0: no BTA, 1: BTA export, -1: BTA import)

#### Output:
- bta: BTA parameter (Export, import, no BTA)
- bta_imp: Dataframe containing countries and sectors implementing BTA import
- bta_exp: Dataframe containing countries and sectors implementing BTA export

## prod_cost.py
This file contains production cost module, calculating production cost changes due to energy price increase.

#### Input:
- VA_BASE: Value-added (capital cons., labor comp., taxes)
- LABOR_BASE: Employment and wage
- output: Sectoral output data
- payr_tax_split: Split of tax revenue into payroll tax by skill (artifact variable)
- rev_proportion: Choice of allocated revenue spending into government (default or user-defined)

#### Output:
- wage_share: Share of wage by industrial sector
- empl_share: Share of employment by industrial sector
- labor_share: Share of labor comp. by industrial sector
- exog_prod_cost_base: Production cost changes before structural changes due to energy elasticities
- exog_prod_cost: Production cost changes after structural changes due to energy elasticities

## InputOutput.py
This file contains Input-Output module, calculating changes in the gross output due to changes into final demands.

#### Input:
- L_BASE: Initial Leontief matrix
- Y_BASE: Initial final demand matrix
- HH_price_eff: Household consumption change due to price effect
- HH_inc_eff: Household consumption change due to income effect (recycled revenue and output changes)
- GOV_recyc: Government expenditure change (recycling effect)
- INV_induced: Capital formation change due to induced effect (output changes)
- INV_recyc: Capital formation change due to revenue recycling into public investment
- INV_added: Capital formation change due to exogenous additional investment

#### Output:
- dL_ener: Changes in Leontief matrix due to energy elasticities
- dq_tech_eff: Output change (absolute) due to energy elasticities
- A_trade: A matrix after tech and trade substitution effects
- dq_IO_eff: Output changes (absolute) as a result of tech (energy elasticities) effect
- dq_trade_eff: Output changes (absolute) as a result of tech (energy elasticities) and trade effect
- dq_hh_price: Output changes (absolute) due to price changes in household goods
- dq_hh_inc: Output changes (absolute) due to income effect (recycling and output changes) into household demand
- dq_gov_recyc: Output changes (absolute) due to revenue recycling into govt. spending
- dq_inv_induced: Output changes (absolute) due to induced effect in capital formation
- dq_inv_recyc: Output changes (absolute) due to revenue recycling into public investment
- dq_inv_added: Output changes (absolute) due to exogenous additional investment
- dq_total: Total output changes (absolute)

## price.py
This file contains price module, calculating commodity price changes due to energy price increase.

#### Input:
- L_BASE: Initial Leontief matrix
- bta: BTA parameter (Export, import, no BTA)
- exog_prod_cost_base: Production cost changes before structural changes due to energy elasticities
- exog_prod_cost: Production cost changes after structural changes due to energy elasticities

#### Output:
- v_base: Production cost changes before structural changes due to energy elasticities
- v_ener: Production cost changes after structural changes due to energy elasticities
- dp_base: Price changes before tech (energy structure) changes
- dp_ener: Price changes after tech (energy structure) changes and before trade effects
- dp_pre_trade: Price changes after tech (energy structure) changes and before trade effects
- dp_trade: Price changes after tech (energy structure) changes and after trade effects

## household.py
This file contains household module, calculating household final demand changes.

#### Input:
- HH_BASE: Household consumption final demand
- HH_INC_COU_MAP: Country mapping based on income level (for household module)
- HH_INC_ELAS: Household income elasticities data
- HH_OP_ELAS: Household own-price elasticities data
- HH_CP_ELAS_LOW: Household cross-price elasticities data for low-income countries
- HH_CP_ELAS_MID: Household cross-price elasticities data for mid-income countries
- HH_CP_ELAS_HIGH: Household cross-price elasticities data for high-income countries
- dp_pre_trade: Price changes after tech (energy structure) changes and before trade effects
- tax_rate_hh: Carbon tax rate for each fuel in households

#### Output:
- HH_price_eff: Household consumption change due to price effect
- HH_inc_eff: Household consumption change due to income effect (recycled revenue and output changes)
- dy_hh_price: Household consumption change due to price effect
- dy_hh_inc: Household consumption change due to income effect (recycled revenue and output changes)

## government.py
This file contains government module, calculating government final demand changes.

#### Input:
- GOV_BASE: Government consumption final demand
- rev_proportion: Choice of allocated revenue spending into government (default or user-defined)
- govt_spending: Sectoral split of tax revenue allocated into government spending (user-defined)

#### Output:
- GOV_recyc: Government expenditure change (recycling effect)
- dy_gov_recyc: Government expenditure change (recycling effect)

## trade.py
This file contains trade module, simulating trade substitution in the MRIO table.

#### Input:
- TRADE_ELAS: Trade elasticities by industrial sectors
- dp_pre_trade: Price changes after tech (energy structure) changes and before trade effects
- ind_ener_glo: IO coefficients after energy substitution (global)

#### Output:
- ind_trade: IO coefficients after trade substitution (global)

## investment.py
This file contains investment module, calculating investment final demand changes.

#### Input:
- FCF_BASE: Investment consumption final demand
- INV_CONV: Investment conversion matrix (from sectors into commodities)
- INV_OUTPUT_ELAS: Country- and sector-specific investment-output elasticities (induced investment)
- ADD_INV: Added investment exogenously from investment template
- RE_INVEST: Renewable investment conversion matrix (from selected electricity technology into commodities)

#### Output:
- inv_share: Share of investment commodities based on producing countries
- INV_induced: Capital formation change due to induced effect (output changes)
- INV_recyc: Capital formation change due to revenue recycling into public investment
- INV_added: Capital formation change due to exogenous additional investment
- dy_inv_induced: Capital formation change due to induced effect (output changes)
- dy_inv_recyc: Capital formation change due to revenue recycling into public investment
- dy_inv_added: Capital formation change due to exogenous additional investment

## employment.py
This file contains employment module, calculating changes in the employment due to changes in output.

#### Input:
- EMPL_COEF: Country- and sector-specific employment-output elasticities
- dq_IO_eff: Output changes (absolute) as a result of tech (energy elasticities) effect
- dq_trade_eff: Output changes (absolute) as a result of tech (energy elasticities) and trade effect
- dq_hh_price: Output changes (absolute) due to price changes in household goods
- dq_hh_inc: Output changes (absolute) due to income effect (recycling and output changes) into household demand
- dq_gov_recyc: Output changes (absolute) due to revenue recycling into govt. spending
- dq_inv_induced: Output changes (absolute) due to induced effect in capital formation
- dq_inv_recyc: Output changes (absolute) due to revenue recycling into public investment
- dq_inv_added: Output changes (absolute) due to exogenous additional investment
- dq_total: Total output changes (absolute)

#### Output:
- empl_multiplier: Employment elasticities multiplied by employment intensity (people per kUSD)
- dempl_total: Total employment changes (absolute)
- dempl_tech_eff: Employment changes (absolute) as a result of tech effect (energy elasticities)
- dempl_trade_eff: Employment changes (absolute) as a result of trade effect (trade elasticities)
- dempl_hh_price: Employment changes (absolute) as a result of household demand changes due to carbon tax-induced price changes  
- dempl_hh_inc: Employment changes (absolute) as a result of household demand changes due to (recycled) income changes
- dempl_gov_recyc: Employment changes (absolute) as a result of additional government spending
- dempl_inv_induced: Employment changes (absolute) as a result of induced final capital formation
- dempl_inv_recyc: Employment changes (absolute) as a result of recycled investment
- dempl_inv_added: Employment changes (absolute) as a result of additional (exogenous) investment

## income.py
This file contains income module, calculating labor income used in the household-income loop.

#### Input:
- dempl_total: Total employment changes (absolute)
- dq_total: Total output changes (absolute)
- ind_trade: IO coefficients after trade substitution (global)
- HH_price_eff: Household consumption change due to price effect
- HH_inc_eff: Household consumption change due to income effect (recycled revenue and output changes)
- tax_rate: Carbon tax rate for each fuel and sector
- tax_rate_hh: Carbon tax rate for each fuel in households

#### Output:
- ener_flow: IO coefficient of energy commodities
- ener_flow_hh: Household consumption of energy commodities
- dlabor_sec: Sectoral changes in labor income (total wage * employment)
- dlabor_nat: National changes in labor income (total wage * employment)

## GDP.py
This file contains GDP module, calculating the GDP changes from changes in technical coefficient and gross output.

#### Input:
- dq_IO_eff: Output changes (absolute) as a result of tech (energy elasticities) effect
- dq_trade_eff: Output changes (absolute) as a result of tech (energy elasticities) and trade effect
- dq_hh_price: Output changes (absolute) due to price changes in household goods
- dq_hh_inc: Output changes (absolute) due to income effect (recycling and output changes) into household demand
- dq_gov_recyc: Output changes (absolute) due to revenue recycling into govt. spending
- dq_inv_induced: Output changes (absolute) due to induced effect in capital formation
- dq_inv_recyc: Output changes (absolute) due to revenue recycling into public investment
- dq_inv_added: Output changes (absolute) due to exogenous additional investment
- dq_total: Total output changes (absolute)

#### Output:
- gdp_base: Initial GDP calculated from output and IO coefficients
- dgdp_total: Total GDP changes (absolute)
- dgdp_tech_eff: GDP changes (absolute) as a result of tech effect (energy elasticities)
- dgdp_trade_eff: GDP changes (absolute) as a result of trade effect (trade elasticities)
- dgdp_hh_price: GDP changes (absolute) as a result of household demand changes due to carbon tax-induced price changes  
- dgdp_hh_inc: GDP changes (absolute) as a result of household demand changes due to (recycled) income changes
- dgdp_gov_recyc: GDP changes (absolute) as a result of additional government spending
- dgdp_inv_induced: GDP changes (absolute) as a result of induced final capital formation
- dgdp_inv_recyc: GDP changes (absolute) as a result of recycled investment
- dgdp_inv_added: GDP changes (absolute) as a result of additional (exogenous) investment

## results.py
This file contains results module, to save the results in the desired format.

#### Output:
- output_change: Output changes for each effect
- empl_change: Employment changes for each effect
- gdp_change: GDP changes for each effect
- price_change: Price changes for tech and trade effect
- total_revenue: Total tax revenue collected from each sector

### Subfolder ParseCode

- IO_mat_table.py: This file extracts IO tables from GLORIA into National IO format.
- Parsing-Gloria-mat.py: This file parses IO tables from GLORIA datasets in .csv format into .mat format.
- Parsing-Gloria-pkl.py: This file parses IO tables from .mat format into .pkl DataFrame format.
- aggregate.py: This file contains methods to aggregate MRIO table into desired regional/sectoral aggregation.
- aggregate_mat.py: This file is the script to aggregate GLORIA-MRIO table.

### Not shown: Subfolder GLORIA_db

Content:

- Subfolder(s): v56\\2019\\parsed_db
(can be adjusted accordingly depending on the GLORIA-MRIO version)
- GLORIA_L_Base_2019.mat: Leontief inverse matrix of A matrix in GLORIA MRIO in .mat format
- GLORIA_Y_Base_2019.mat: Final demand matrix in GLORIA MRIO in .mat format

#### Subfolder parsed_db

- cid.pkl, cou.pkl: List of country IDs and country names
- sid.pkl, sec.pkl: List of sector IDs and sector names
- IND_sparse.pkl: Interindustry flows for each commodity coming into each sector
- VA.pkl: Value-Added components
- HH.pkl: Household final demand flows
- NPISH.pkl: Non-profit institution final demand flows
- GOV.pkl: Government final demand flows
- FCF.pkl: Investment final demand flows
- labor_data.pkl: Sectoral employment and wage dataset

## Not shown: Subfolder GLORIA_template

Content:
- Subfolder(s):

#### Subfolder Elasticities

- OwnPrices.xlsx: Own-price energy elasticities
- EnergyElas_ByCountry.xlsx: Country-specific cross-price energy elasticities
- EnergyElas_ROA.xlsx: Cross-price energy elasticities Rest of Asia
- EnergyElas_ROE.xlsx: Cross-price energy elasticities Rest of Africa
- EnergyElas_ROW.xlsx: Cross-price energy elasticities Rest of World
- FileID.xlsx: Concordance of Cross-price energy elasticities

- Countries_inc_cat.xlsx: Country mapping based on income level (for household module)
- USDA_Table1.xlsx: Household income elasticities data
- USDA_Table2.xlsx: Household own-price elasticities data
- USDA_cpe_low.xlsx: Household cross-price elasticities data for low-income countries
- USDA_cpe_mid.xlsx: Household cross-price elasticities data for mid-income countries
- USDA_cpe_high.xlsx: Household cross-price elasticities data for high-income countries

#### Subfolder Employment

- Empl_coefficient.csv: Country- and sector-specific investment-output elasticities

#### Subfolder Investment

- Inv_conversion.csv: Investment conversion matrix (from sectors into commodities)
- Inv_output.csv: Country- and sector-specific investment-output elasticities (induced investment)
- Inv_added.csv: Manual template for added investment
- Inv_renewables.csv: Renewable investment conversion matrix (from selected electricity technology into commodities)

#### Subfolder modelinputdata

- Countries_USDAtoGLORIA.xlsx: Country mapping from USDA dataset into GLORIA.
- Sectors_USDAtoGLORIA.xlsx: Sector mapping from USDA dataset into GLORIA.

#### Subfolder Scenarios

- Templates_tax_BTA_xxx_GLORIA.xlsx: Scenario file containing (for now: tax incidence)

#### Subfolder Variables

- Variable_list_MINDSET.xlsx: Variable lists in MINDSET model
