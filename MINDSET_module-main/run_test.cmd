:: ------------------------------------------------------------
:: Init
:: ------------------------------------------------------------
for %%I in (.) do @set _folder=%%~nxI
for /f "delims=" %%# in ('powershell get-date -format "{dd-MMM-yyyy HH:mm}"') do @set _date=%%#
call restore_original_regions.cmd
python "ParseCode\collapse_MRIO.py" "GLORIA_template\Country_groupings\WB_regions_grouping.xlsx"
:: ---------------------------------------------------------------
:: Base
:: ------------------------------------------------------------
python RunMINDSET.py "Testing_BA" Yes
copy "GLORIA_results\\FullResults_Testing_BA.xlsx" "GLORIA_results\\test_baseline_residuals.xlsx" /y
:: ---------------------------------------------------------------
:: S1
:: ------------------------------------------------------------
python RunMINDSET.py "Testing_Demand" Yes "GLORIA_results\\test_baseline_residuals.xlsx"
python RunMINDSET.py "Testing_Supply" Yes "GLORIA_results\\test_baseline_residuals.xlsx"
python RunMINDSET.py "Testing_Cprice" Yes "GLORIA_results\\test_baseline_residuals.xlsx"
:: ---------------------------------------------------------------
:: Generate long-form results
python merge_results_longformat.py "Testing" "testing_results_%_folder%_%_date%"