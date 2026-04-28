import sys
sys.path.insert(0, '.')
from SourceCode.exog_vars_SSP import exog_vars
from SourceCode.scenario import scenario

class MockLog:
    def log_to_csv(self, *args, **kwargs): pass

output_file = 'Claude Code/temp/key_sectors_conversion.txt'

with open(output_file, 'w') as f:
    MRIO = exog_vars()
    Scen = scenario(MRIO, 'GLORIA_template/Scenarios/Strategy_1004_MEX.xlsx', MockLog())
    INV = Scen.set_inv_conv_adj(MRIO)

    for sector in ['55', '89', '90']:
        f.write(f'Sector {sector} (MEX) converts to:\n')
        f.write('-'*60 + '\n')
        d = INV[(INV['PROD_COMM']==sector) & (INV['REG_imp']=='MEX') & (INV['input_coeff']>0)]
        f.write(d[['TRAD_COMM','input_coeff']].sort_values('input_coeff', ascending=False).to_string(index=False))
        f.write('\n\n')

print(f'Output written to {output_file}')
