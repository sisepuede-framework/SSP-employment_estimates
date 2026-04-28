from SourceCode.exog_vars_SSP import exog_vars
MRIO_BASE = exog_vars()
print(f'mrio_id length: {len(MRIO_BASE.mrio_id)}')
print(f'A_id length: {len(MRIO_BASE.A_id)}')
print(f'COU_ID length: {len(MRIO_BASE.COU_ID)}')
print(f'SEC_ID length: {len(MRIO_BASE.SEC_ID)}')
print(f'Expected DIMS: {len(MRIO_BASE.COU_ID) * len(MRIO_BASE.SEC_ID)}')
print(f'IND_BASE unique pairs: {MRIO_BASE.IND_BASE.index.nunique()}')
