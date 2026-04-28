# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 17:06:40 2023

@author: wb582890
"""

import numpy as np
import pandas as pd

class price:
    """
    PriceModel class calculates prices based on exogenous costs.

    Inputs:
    - exog_prod_cost: DataFrame containing exogenous production cost data
    - GLORIA_rp: DataFrame containing GLORIA region and sector identifiers
    - L_base: Base Leontief inverse matrix
    
    Output:
    - delta_p_pm: DataFrame containing calculated price changes
    - delta_p_bta_exim: Dataframe containing domestic price change with no bta

    """
    def __init__(self, exog_vars, L_BASE, BTA_cou):
        self.COU_ID = exog_vars.COU_ID
        self.mrio_id = exog_vars.mrio_id
        self.A_id = exog_vars.A_id
        
        self.L_BASE = L_BASE

        self.R_list = exog_vars.R['Region_acronyms'].tolist()
        self.P_list = exog_vars.P['Lfd_Nr'].to_list()

        self.DIMS = len(self.R_list) * len(self.P_list)
        
        self.bta = BTA_cou.bta
        
        if self.bta == 1:
            self.bta_exp = BTA_cou.bta_exp
        elif self.bta == -1 or self.bta == 0:
            self.bta_imp = BTA_cou.bta_imp
        
    def build_prod_cost_base_vector(self, exog_prod_cost_base):
        """
        
        Parameters
        ----------
        exog_prod_cost_base : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        v_base = exog_prod_cost_base.copy()
        v_base["IMP_SEC"] = list(zip(v_base["REG_imp"], v_base["PROD_COMM"]))
        v_base = v_base.drop(columns=["REG_imp","PROD_COMM"])
        v_base = v_base.set_index(["IMP_SEC"])

        v_temp = pd.DataFrame(np.zeros(self.DIMS), index=self.A_id,
                              columns=["delta_prod_cost_rel_base"])
        v_temp.loc[self.A_id] = v_base
        v_base = v_temp.fillna(1)

        v_base = v_base["delta_prod_cost_rel_base"].to_numpy()
        
        self.v_base = v_base
        
        return self.v_base

    def build_prod_cost_vector(self, exog_prod_cost):
        v_ener = exog_prod_cost.copy()
        v_ener['prod_cost_rel'] = pd.to_numeric(v_ener['prod_cost_rel'])
        mIndex_in = pd.MultiIndex.from_frame(v_ener[['REG_imp','PROD_COMM']])
        v_ener = v_ener.drop(columns=["REG_imp","PROD_COMM"])
        v_ener = v_ener.set_index(mIndex_in)

        mIndex = pd.MultiIndex.from_tuples(self.A_id)
        v_temp = pd.DataFrame(np.empty(self.DIMS), index=mIndex,
                              columns=["delta_prod_cost_rel"])
        v_temp[:] = np.nan
        v_temp.loc[v_ener.index] = v_ener
        v_ener = v_temp.fillna(1)

        v_ener = v_ener["delta_prod_cost_rel"].to_numpy()
        
        self.v_ener = v_ener
        
        return self.v_ener
    
    def calc_dp_base(self, v_base):
        # price effect before any changes to A. Corresponds to Eq. (6i)
        dp_base = np.dot((v_base-1), self.L_BASE)
        # import pdb; pdb.set_trace()
        
        self.dp_base = dp_base
        
        return self.dp_base
    
    def calc_dp_ener(self, v_ener, dL_ener):
        # price effect after technology but before trade effects (IO price model results)
        dp_ener = np.dot((v_ener-1), self.L_BASE) + np.dot((v_ener-1), dL_ener)
        # import pdb; pdb.set_trace()
        # dp_bta_exim['delta_p'] = dp_bta_exim['delta_p'].apply(lambda x: x if x < 5 else 5)

        self.dp_ener = dp_ener
        
        return self.dp_ener
    
    def calc_dp_pre_trade(self, dp_ener):
    
        dp_pre_trade = pd.concat([self.mrio_id, pd.DataFrame(dp_ener)], axis=1)
        dp_pre_trade.columns = ['REG_imp', 'TRAD_COMM', 'delta_p']
        
        self.dp_pre_trade = dp_pre_trade
        
        return self.dp_pre_trade

    def calc_dp_pre_trade_bta(self, dp_ener, cbam_incidence):

        dp_pre_trade = self.calc_dp_pre_trade(dp_ener)
        
        dp_no_bta = pd.DataFrame(columns=['REG_exp', 'TRAD_COMM', 'REG_imp','delta_p'])

        cbam_incidence = cbam_incidence.astype({'TRAD_COMM':'int'})

        # export on DOMESTIC price
        for i in self.COU_ID:
            dp_populate = dp_pre_trade[dp_pre_trade['REG_imp']==i].copy()
            dp_populate = pd.concat([dp_populate]* len(self.R_list))
            dp_populate['REG_exp'] = i
            dp_populate['REG_imp'] = np.repeat(self.COU_ID,120)
            
            dp_no_bta = pd.concat([dp_no_bta, dp_populate])
            
            del(dp_populate)

        dp_no_bta = dp_no_bta.astype({"delta_p": 'float64','TRAD_COMM':'int'})

        dp_bta_exim = dp_no_bta.merge(cbam_incidence, how='left', 
                                      on=['REG_exp','TRAD_COMM','REG_imp'])
        
        dp_bta_exim['delta_cbam'] = dp_bta_exim['delta_cbam'].fillna(0)
        dp_bta_exim['delta_p'] = dp_bta_exim['delta_p'] + dp_bta_exim['delta_cbam']

        # # only domestic price changes
        # dp_bta_diag = dp_no_bta[dp_no_bta["REG_imp"] == dp_no_bta["REG_exp"]]
        # dp_bta_diag = dp_bta_diag.drop(columns=["REG_exp"])
        # dp_bta_diag = dp_bta_diag.rename(columns={"delta_p":"delta_p_dom"})

        # # join delta_p frame with domestic prices
        # dp_bta_exim = dp_no_bta.merge(dp_bta_diag, how='left', on=["REG_imp", "TRAD_COMM"])
        # dp_bta_exim["delta_p_dom"] = dp_bta_exim["delta_p_dom"].fillna(0)

        # # import pdb; pdb.set_trace()

        # # * export BTA don't use
        # if self.bta == 1:
        #     dp_bta_exim = dp_bta_exim.merge(self.bta_exp, how='left',
        #                                     on=['REG_exp', 'TRAD_COMM', 'REG_imp'])
            
        #     dp_bta_on = dp_bta_exim[dp_bta_exim['BTA_exp'] == 1]
        #     dp_bta_off = dp_bta_exim[dp_bta_exim['BTA_exp'] == 0]
        #     dp_bta_on['delta_p'] = 0
            
        #     dp_bta_exim = pd.concat([dp_bta_on, dp_bta_off])

        # # ! IMPORT or no BTA
        # elif self.bta == -1 or self.bta == 0:
        #     dp_bta_exim = dp_bta_exim.merge(self.bta_imp, how='left',
        #                                     on=['REG_exp', 'TRAD_COMM', 'REG_imp'])
        #     # import pdb; pdb.set_trace()
        #     dp_bta_on = dp_bta_exim[dp_bta_exim['cbam'] == 1].copy()
        #     dp_bta_on_no_adjust = dp_bta_on[dp_bta_on['delta_p'] > dp_bta_on['delta_p_dom']].copy()
        #     dp_bta_on_adjust = dp_bta_on[dp_bta_on['delta_p'] <= dp_bta_on['delta_p_dom']].copy()
        #     dp_bta_off = dp_bta_exim[dp_bta_exim['cbam'] == 0].copy()

        #     dp_bta_on_adjust['delta_p'] = dp_bta_on_adjust['delta_p_dom']

        #     dp_bta_exim = pd.concat([dp_bta_on_adjust, dp_bta_on_no_adjust, dp_bta_off])

        # # cap on 500% increase
        # # import pdb; pdb.set_trace()
        # dp_bta_exim = dp_bta_exim.merge(mrio.reset_index()[['TRAD_COMM','REG_imp','REG_exp','z_bp']], how='left', on=['TRAD_COMM','REG_imp','REG_exp'])

        # dp_bta_exim['z_bp'] = dp_bta_exim['z_bp'] / dp_bta_exim.groupby(['TRAD_COMM','REG_imp'])['z_bp'].transform('sum')
        # dp_bta_exim['delta_p'] = dp_bta_exim['delta_p'] * dp_bta_exim['z_bp']
        # dp_bta_exim = dp_bta_exim.groupby(['TRAD_COMM','REG_imp']).agg({'delta_p':'sum'}).reset_index()
        
        dp_bta_exim['delta_p'] = dp_bta_exim['delta_p'].apply(lambda x: x if x < 5 else 5)
        dp_bta_exim = dp_bta_exim[['REG_imp','REG_exp','TRAD_COMM','delta_p']]
            
        self.dp_pre_trade = dp_bta_exim

        # import pdb; pdb.set_trace()

        return self.dp_pre_trade

    def calc_dp_trade(self, A1, dp_ener, v_ener):
        if type(dp_ener) == pd.DataFrame:
            dp_ener = dp_ener["delta_p"].to_numpy()
        
        delta_p1_iter1 = dp_ener.copy()
        delta_p1_iter2 = np.dot(delta_p1_iter1, A1) + (v_ener-1)

        i = 0

        while np.sum(
                np.divide(abs(delta_p1_iter2 - delta_p1_iter1),
                          delta_p1_iter1, out=np.zeros_like(delta_p1_iter1),
                          where=delta_p1_iter1 != 0)) >= 1e-2:
            delta_p1_iter1 = delta_p1_iter2.copy()
            delta_p1_iter2 = np.dot(delta_p1_iter1, A1) + (v_ener-1)
            i += 1

        # price effect after technology and trade effects. Corresponds to Eq (6iii)
        self.delta_p1 = delta_p1_iter2.copy()  

        return self.delta_p1