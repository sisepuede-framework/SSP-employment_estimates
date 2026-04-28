:: ---------------------------------------------------------------
:: Base
:: ------------------------------------------------------------
python RunMINDSET_dynamic.py "Testing_BA" "True"
copy "GLORIA_results\\FullResults_Testing_BA.xlsx" "GLORIA_results\\baseline_residuals.xlsx" /y
:: ---------------------------------------------------------------
:: S1
:: ------------------------------------------------------------
@REM python RunMINDSET_dynamic.py "Sweden_carbon_tax" "True" "GLORIA_results\\SWE_baseline_residuals.xlsx"
python RunMINDSET_dynamic.py "Testing_Cprice" "True" "GLORIA_results\\baseline_residuals.xlsx"