from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()
print('Countries in your GLORIA data:')
print(MRIO_BASE.R['Region_acronyms'].to_list())
