:: ---------------------------------------------------------------
:: Base
:: ------------------------------------------------------------
python RunMINDSET.py "Testing_BA" Yes 
copy "GLORIA_results\\FullResults_Testing_BA.xlsx" "GLORIA_results\\baseline_residuals.xlsx" /y
:: ---------------------------------------------------------------
:: S1
:: ------------------------------------------------------------
@REM python RunMINDSET.py "MDA_Climate_heatstress_2030" Yes "GLORIA_results\\baseline_residuals.xlsx"
@REM python RunMINDSET.py "MDA_Climate_heatstress_2050" Yes "GLORIA_results\\baseline_residuals.xlsx"
@REM python RunMINDSET.py "MDA_Climate_combined_pessimistic_2030" Yes "GLORIA_results\\baseline_residuals.xlsx"
@REM python RunMINDSET.py "MDA_Climate_combined_pessimistic_2050" Yes "GLORIA_results\\baseline_residuals.xlsx"
:: S2
:: ---------------------------------------------------------------
python RunMINDSET.py "MDA_Adaptation_combined_pessimistic_2030" "GLORIA_results\\baseline_residuals.xlsx"
@REM python RunMINDSET.py "MDA_Adaptation_combined_pessimistic_2050" "GLORIA_results\\baseline_residuals.xlsx"
GOTO END
:: ---------------------------------------------------------------
:: Generate long-form results
@REM python merge_results_longformat.py
python GLORIA_results\subtract.py
:: Generate figures with R
"C:\Program Files\R\R-4.3.0\bin\RScript.exe" "Iras_Results_MourningDove.R"


:END