# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 14:11:05 2023

@author: wb582890
"""

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, csr_matrix
import scipy.io
import scipy.linalg
import time
from SourceCode.utils import MRIO_df_to_vec

from datetime import datetime

class IO:
    """
    A class used to reconstruct new Input-Output (IO) matrices and calculate 
    output changes from new IO matrix and Final Demand (FD) vectors.

    Attributes
    ----------
    exog_vars : class
        a formatted string to print out what the  says
    name : str
        the name of the 
    sound : str
        X
    num_legs : int
        X

    Methods
    -------
    says(sound=None)
        X
    
    """
    def __init__(self, exog_vars):
        """
        Test

        Parameters
        ----------
        exog_vars : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.mrio_id = exog_vars.mrio_id
        self.A_id = exog_vars.A_id
        self.IND_BASE = exog_vars.IND_BASE
        self.IO_PATH = exog_vars.IO_PATH
        self.year = 2019
        self.GLORIAv = exog_vars.GLORIAv

        self.CRITICALITY = exog_vars.GLORIA_CRITICALITY.astype({'Nr_Input':'int16','Nr_Ind':'int16'})\
            .rename(columns={'Nr_Input':'TRAD_COMM','Nr_Ind':'PROD_COMM'})[['PROD_COMM','TRAD_COMM','Criticality']]

        self.HH_BASE = exog_vars.HH_BASE
        self.GOV_BASE = exog_vars.GOV_BASE
        self.FCF_BASE = exog_vars.FCF_BASE
        self.NPISH_BASE = exog_vars.NPISH_BASE
        self.INV_BASE = exog_vars.INV_BASE

        self.R_list = exog_vars.R['Region_acronyms'].tolist()
        self.P_list = exog_vars.P['Lfd_Nr'].to_list()

        self.DIMS = len(self.R_list) * len(self.P_list)
        
        try:
            self.Y_BASE = exog_vars.Y_BASE
        except AttributeError:
            pass
        try:
            self.L_BASE = exog_vars.L_BASE
        except AttributeError:
            pass
        try:
            self.G_BASE = exog_vars.G_BASE
        except AttributeError:
            pass

    def io_change(self, io_change_data, sparse_matrix):
        # sparse_matrix structure is 
        # REG_imp	PROD_COMM	REG_exp	TRAD_COMM	IO_coef_trade
        # for now trade shock is implemented on exports

        # io_change_data structure is
        # REG_imp PROD_COMM REG_exp TRAD_COMM Type Value

        # for now ignore type, replace values always
        # keep other values intact
        # do impact
        io_change_data = io_change_data.astype({'TRAD_COMM':'int','PROD_COMM':'int'})
        
        # Get the list of type, keeping the order as in the template
        types = io_change_data['Type'].drop_duplicates().to_list()
            
        # Based on the order of types, do the impact 
        if len(types)>0:
            for t in types:
                sparse_matrix = sparse_matrix.merge(io_change_data[io_change_data['Type']==t],how='left', on=['REG_exp','TRAD_COMM','REG_imp','PROD_COMM'])
                sel = (~sparse_matrix['Value'].isna())
                if t == "replace":
                    sparse_matrix.loc[sel,'IO_coef_trade'] = sparse_matrix.loc[sel,'Value']
                if t == "rel":
                    sparse_matrix.loc[sel,'IO_coef_trade'] = sparse_matrix.loc[sel, 'IO_coef_trade'] * (1 + sparse_matrix.loc[sel, 'Value'])
                sparse_matrix = sparse_matrix.drop(columns=['Value','Type'])
    
            sparse_matrix = sparse_matrix.set_index(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])
        else:
            sparse_matrix=sparse_matrix
        return sparse_matrix

    def load_L_base(self):
        module_time = time.time()
        self.build_A_base()
        # print("--- Load_L_base#1 %s seconds ---" % round(time.time() - module_time, 1))
        if 'L_BASE' in dir(self):
            self.L_BASE = self.L_BASE["L_base"] # type: ignore
        else:
            self.invert_A_base()
        # print("--- Load_L_base#2 %s seconds ---" % round(time.time() - module_time, 1))

    def load_G_base(self):
        module_time = time.time()
        # print("--- Load_G_base#1 %s seconds ---" % round(time.time() - module_time, 1))
        if 'G_BASE' in dir(self):
            self.G_BASE = self.G_BASE["G_base"]
        else:
            self.build_B_base()
            self.invert_B_base()
        # print("--- Load_G_base#2 %s seconds ---" % round(time.time() - module_time, 1))

    def build_B_base(self):
        # Compute B or output coefficient matrix
        # this will be used to create the G (Ghosh) matrix or G_base
        # this is a matrix where row totals are 1, row elements are shares of this

        # TO account for criticality we're erasing or reducing those flows for the 
        # B matrix calculation which are not critical
        B_BASE_df = self.IND_BASE.reset_index()
        B_BASE_df = B_BASE_df.merge(self.CRITICALITY, how='left', on=['PROD_COMM','TRAD_COMM'])
        B_BASE_df['z_bp'] = B_BASE_df['z_bp'] * B_BASE_df['Criticality']
        B_BASE_df = B_BASE_df[['REG_imp','PROD_COMM','REG_exp','TRAD_COMM','z_bp']].copy()
        B_BASE_df = B_BASE_df.set_index(['REG_imp','PROD_COMM','REG_exp','TRAD_COMM'])

        B_BASE_df = B_BASE_df.unstack(level=["REG_imp","PROD_COMM"])
        B_BASE_df.columns = B_BASE_df.columns.droplevel(0)

        B_temp = pd.DataFrame(
            np.zeros((self.DIMS,self.DIMS)), index=self.A_id, columns=self.A_id)
        B_temp.loc[B_BASE_df.index, B_BASE_df.columns] = B_BASE_df

        B_BASE = B_temp.fillna(0)
        B_BASE = B_BASE.to_numpy()
        
        # actual calculation
        B_BASE = (B_BASE.T/(B_BASE.sum(axis=1)+self.y0)).T
        B_BASE[np.isnan(B_BASE)] = 0

        # if in the diagonal the element is 1.0 then when we subtract from the identity matrix
        # we will get a singular matrix and will not be able to do the inverse
        # not that a 1.0 diagonal element makes too much sense anywa
        # it was particularly bad in Gabon 32-35 sectors
        # so we replace if 1.0 in diagonal with 0.99

        d_ = B_BASE.diagonal().copy()
        d_[d_==1] = 0.99
        np.fill_diagonal(B_BASE, d_)

        # test for determinant anyway
        if np.linalg.slogdet(np.identity(len(B_BASE)) - B_BASE)[1] == -np.inf:
            print("Determinant is zero, cannot proceed")
            exit()
        
        self.B_BASE = B_BASE

    def invert_B_base(self):
        # to get the G (Ghoshian) matrix
        convert_time = time.time()

        I = np.identity(len(self.B_BASE))

        inverse_time = datetime.now()

        self.G_BASE = np.linalg.inv(I - self.B_BASE)

        print("G_base inversion: " + str(datetime.now() - inverse_time)[2:7] + " mins")

        scipy.io.savemat(
            self.IO_PATH + f"GLORIA_db\\{self.GLORIAv}\\{str(self.year)}\\GLORIA_G_Base_{str(self.year)}.mat",
            {"G_base": self.L_BASE})
        
        print("--- G_base parsing: %s s ---" % round(time.time() - convert_time, 1))

    def build_A_base(self):
        # Compute A or input coefficient matrix
        # this will be used to create the L (Leontief) matrix or L_base
        A_BASE_df = self.IND_BASE.loc[:, ["a_bp"]]

        A_BASE_df = A_BASE_df.unstack(level=["REG_imp","PROD_COMM"])
        A_BASE_df.columns = A_BASE_df.columns.droplevel(0)

        A_temp = pd.DataFrame(np.zeros((self.DIMS,self.DIMS)), index=self.A_id, columns=self.A_id)
        A_temp.loc[A_BASE_df.index, A_BASE_df.columns] = A_BASE_df

        A_BASE = A_temp.fillna(0)
        A_BASE = A_BASE.to_numpy()

        self.A_BASE = A_BASE
    
    def invert_A_base(self):
        convert_time = time.time()
        
        I = np.identity(len(self.A_BASE))

        inverse_time = datetime.now()

        # Compute L_base
        self.L_BASE = np.linalg.inv(I - self.A_BASE)

        print("L_base inversion: " + str(datetime.now() - inverse_time)[2:7] + " mins")

        # Save L_base to file
        scipy.io.savemat(
            self.IO_PATH + f"GLORIA_db\\{self.GLORIAv}\\{str(self.year)}\\GLORIA_L_Base_{str(self.year)}.mat",
            {"L_base": self.L_BASE})
        print("--- L_base parsing: %s s ---" % round(time.time() - convert_time, 1))

    def load_Y_base(self):
        if 'Y_BASE' in dir(self):
            y0, y_hh0 = self.Y_BASE["y0"], self.Y_BASE["y_hh0"]
            y_gov0, y_fcf0 = self.Y_BASE["y_gov0"], self.Y_BASE["y_fcf0"]
            y_npish, y_inv = self.Y_BASE["y_npish"], self.Y_BASE["y_inv"]

            self.y0, self.y_hh0 = y0[0], y_hh0[0]
            self.y_gov0, self.y_fcf0 = y_gov0[0], y_fcf0[0]
            self.y_npish, self.y_inv = y_npish[0], y_inv[0]

        else:
            convert_time = time.time()

            y_hh0 = MRIO_df_to_vec(self.HH_BASE.groupby(['REG_exp','TRAD_COMM']).agg({'VIPA':'sum'}).reset_index(), 'REG_exp', 'TRAD_COMM', 'VIPA', self.R_list,  self.P_list)
            y_gov0 = MRIO_df_to_vec(self.GOV_BASE.groupby(['REG_exp','TRAD_COMM']).agg({'VIGA':'sum'}).reset_index(), 'REG_exp', 'TRAD_COMM', 'VIGA', self.R_list,  self.P_list)
            y_fcf0 = MRIO_df_to_vec(self.FCF_BASE.groupby(['REG_exp','TRAD_COMM']).agg({'VDFA':'sum'}).reset_index(), 'REG_exp', 'TRAD_COMM', 'VDFA', self.R_list,  self.P_list)
            y_inv = MRIO_df_to_vec(self.INV_BASE.groupby(['REG_exp','TRAD_COMM']).agg({'INV':'sum'}).reset_index(), 'REG_exp', 'TRAD_COMM', 'INV', self.R_list,  self.P_list)
            y_npish = MRIO_df_to_vec(self.NPISH_BASE.groupby(['REG_exp','TRAD_COMM']).agg({'NPISH':'sum'}).reset_index(), 'REG_exp', 'TRAD_COMM', 'NPISH', self.R_list,  self.P_list)

            y0 = y_hh0 + y_gov0 + y_fcf0 + y_npish + y_inv

            # Save Y_base to file
            scipy.io.savemat(
                self.IO_PATH + f"GLORIA_db\\{self.GLORIAv}\\{str(self.year)}\\GLORIA_Y_Base_{str(self.year)}.mat",
                {"y0": y0, "y_hh0": y_hh0, "y_npish": y_npish,
                 "y_gov0": y_gov0, "y_fcf0": y_fcf0, "y_inv": y_inv})

            self.y0, self.y_hh0 = y0, y_hh0
            self.y_gov0, self.y_fcf0 = y_gov0, y_fcf0
            self.y_npish, self.y_inv = y_npish, y_inv

            print("--- Y_base parsing: %s s ---" % round(time.time() - convert_time, 1))
    
    def calc_init_q(self):
        # Calculate baseline output
        self.q_base = np.dot(self.L_BASE, self.y0)

        # Calculate output due to household consumption
        self.q_hh = np.dot(self.L_BASE, self.y_hh0)

        # Calculate output due to non-profit institution
        self.q_npish = np.dot(self.L_BASE, self.y_npish)

        # Calculate output due to government final demand
        self.q_gov = np.dot(self.L_BASE, self.y_gov0)

        # Calculate output due to capital formation
        self.q_fcf = np.dot(self.L_BASE, self.y_fcf0)

        # Calculate due to inventory
        self.q_inv = np.dot(self.L_BASE, self.y_inv)
        
    def initialize(self):
        self.load_L_base()
        self.load_Y_base()
        self.load_G_base()
        self.calc_init_q()

    def build_dL_ener(self, tax_index, tax_matrix, sec_matrix):
        # Calculate dL0_1
        dL0_1 = np.linalg.inv(
            np.identity(len(tax_index)) - np.dot(
                np.dot(sec_matrix, self.L_BASE), tax_matrix))

        # Calculate dL0_2
        dL0_2 = np.dot(self.L_BASE, np.dot(tax_matrix, dL0_1))

        # Calculate dL0_3
        dL0_3 = np.dot(dL0_2, np.dot(sec_matrix, self.L_BASE))
        
        return dL0_3
    
    def calc_dq_energy(self, dL_ener):
        # Calculate total output as a result of energy elasticities
        self.dq_energy = np.dot(dL_ener, self.y0)

        return self.dq_energy
    
    def build_dy_hh_price(self, HH_price_effect):
        # Household demand change due to price changes
        y = pd.DataFrame(self.A_id)
        y["EXP_SEC"] = list(zip(y[0], y[1]))
        y = pd.DataFrame(y.loc[:,"EXP_SEC"])

        HH_price_effect = HH_price_effect.reset_index(drop=False)

        dy_hh_price = HH_price_effect.loc[:,["REG_exp","TRAD_COMM","REG_imp","delta_y_price"]]
        dy_hh_price["EXP_SEC"] = list(zip(dy_hh_price["REG_exp"], dy_hh_price["TRAD_COMM"]))
        dy_hh_price = dy_hh_price.loc[:,["EXP_SEC","REG_imp","delta_y_price"]]
        dy_hh_price = dy_hh_price.pivot(index="EXP_SEC", columns="REG_imp",
                            values="delta_y_price")
        dy_hh_price = y.merge(dy_hh_price, how="left", on=["EXP_SEC"])
        dy_hh_price = pd.concat([y, dy_hh_price.sum(numeric_only=True,axis=1)], axis=1)
        
        self.dy_hh_price = dy_hh_price.iloc[:,1].to_numpy()
        
        return self.dy_hh_price
    
    def build_dy_hh_inc(self, HH_inc_effect):
        # Household demand change due to income change
        y = pd.DataFrame(self.A_id)
        y["EXP_SEC"] = list(zip(y[0], y[1]))
        y = pd.DataFrame(y.loc[:,"EXP_SEC"])

        HH_inc_effect = HH_inc_effect.reset_index(drop=False)

        dy_hh_inc = HH_inc_effect.loc[:,["REG_exp","TRAD_COMM","REG_imp","delta_y_inc"]]
        dy_hh_inc["EXP_SEC"] = list(zip(dy_hh_inc["REG_exp"], dy_hh_inc["TRAD_COMM"]))
        dy_hh_inc = dy_hh_inc.loc[:,["EXP_SEC","REG_imp","delta_y_inc"]]
        dy_hh_inc = dy_hh_inc.pivot(index="EXP_SEC", columns="REG_imp", values="delta_y_inc")
        dy_hh_inc = y.merge(dy_hh_inc, how="left", on=["EXP_SEC"])
        dy_hh_inc = pd.concat([y, dy_hh_inc.sum(numeric_only=True,axis=1)], axis=1)
        self.dy_hh_inc = dy_hh_inc.iloc[:,1].to_numpy()
        
        return self.dy_hh_inc
    
    def build_dy_gov_recyc(self, GOV_recyc):
        y = pd.DataFrame(self.A_id)
        y["EXP_SEC"] = list(zip(y[0], y[1]))
        y = pd.DataFrame(y.loc[:,"EXP_SEC"])

        GOV_recyc = GOV_recyc.reset_index(drop=False)

        dy_gov = GOV_recyc.loc[:,["REG_exp","TRAD_COMM","REG_imp","delta_y_gov"]]
        dy_gov["EXP_SEC"] = list(zip(dy_gov["REG_exp"], dy_gov["TRAD_COMM"]))
        dy_gov = dy_gov.loc[:,["EXP_SEC","REG_imp","delta_y_gov"]]
        dy_gov = dy_gov.pivot(index="EXP_SEC", columns="REG_imp", values="delta_y_gov")
        dy_gov = y.merge(dy_gov, how="left", on=["EXP_SEC"])
        dy_gov = pd.concat([y, dy_gov.sum(numeric_only=True,axis=1)], axis=1)
        
        self.dy_gov = dy_gov.iloc[:,1].to_numpy()
        
        return self.dy_gov
    
    def build_A_trade(self, ind_trade):
        test_time = time.time()

        A1_df = ind_trade.unstack(level=["REG_imp","PROD_COMM"]).astype({'IO_coef_trade':'float16'})
        A1_df.columns = A1_df.columns.droplevel(0)

        A_temp = pd.DataFrame(np.zeros((self.DIMS,self.DIMS), dtype="float16"), index=self.A_id, columns=self.A_id)
        A_temp.loc[A1_df.index, A1_df.columns] = A1_df.values

        A1 = A_temp.fillna(0)
        A1 = A1.to_numpy(dtype="float16")
        
        print("Re-building A1: %s s" % round(time.time() - test_time, 1))

        return A1
    
    def q_iterate(self, A_matrix, q_est, y, tol=5e-4, steps=200):
        q_iter1 = q_est.copy()
        q_iter2 = np.dot(A_matrix, q_iter1) + y
        
        i = 0
        
        while np.sum(
                np.divide(abs(q_iter2 - q_iter1), q_iter1,
                          out=np.zeros_like(q_iter1),
                          where=q_iter1!=0)) >= tol and i <= steps:
            q_iter1 = q_iter2.copy()
            q_iter2 = np.dot(A_matrix, q_iter1) + y
            i += 1
        
        if i >= steps:
            print("Iteration does not converge after %s steps" % steps)
        # else: # Turn on when debugging
        #     print("Iteration passes")
        
        return q_iter2
    
    def calc_dq_IO(self, A_trade):
        q_final = self.q_iterate(A_trade, self.q_base, self.y0)
        self.dq_IO_eff = q_final - self.q_base

        # import pdb; pdb.set_trace()
        
        return self.dq_IO_eff
    
    def calc_dq_trade(self, dq_IO_eff, dq_tech_eff):
        self.dq_trade = dq_IO_eff - dq_tech_eff
        
        return self.dq_trade

    def calc_dq_exog(self, dy):
        dq_exog_fd = np.dot(self.L_BASE, dy)
        
        return dq_exog_fd
    
    def calc_dq_hh(self, A_trade, dy_hh_price, dy_hh_inc):
        self.q_hh_IO = self.q_iterate(A_trade, self.q_hh, self.y_hh0)
        dq_hh_price = self.q_iterate(A_trade, self.q_hh_IO, self.y_hh0 + dy_hh_price)
        dq_hh_price -= self.q_hh_IO
        self.dq_hh_price = dq_hh_price
        
        dq_hh_inc = self.q_iterate(A_trade, self.q_hh_IO, self.y_hh0 + dy_hh_inc)

        dq_hh_inc -= self.q_hh_IO
        self.dq_hh_inc = dq_hh_inc
        
        return self.dq_hh_price, self.dq_hh_inc
    
    def calc_dq_gov(self, A_trade, dy_gov_recyc):
        self.q_gov_IO = self.q_iterate(A_trade, self.q_gov, self.y_gov0)
        
        dq_gov_recyc = self.q_iterate(A_trade, self.q_gov_IO, self.y_gov0 + dy_gov_recyc)
        dq_gov_recyc -= self.q_gov_IO
        
        self.dq_gov_recyc = dq_gov_recyc
        
        return self.dq_gov_recyc
    
    def calc_dq_inv(self, A_trade, dy_inv_induced, dy_inv_recyc, dy_inv_exog):
        # ! added investment, recycling, induced, exog should NOT decrease output in 
        # ! other areas therefore this needs to be revised 
        # ! BKD revision as of 5/3/2024

        # INDUCED
        # initial GFCF induced Q
        dq_inv_induced = np.dot(self.L_BASE, dy_inv_induced)
        self.dq_inv_induced = dq_inv_induced
        
        # RECYCLED from govt
        if sum(dy_inv_recyc) != 0:
            dq_inv_recyc = np.dot(self.L_BASE, dy_inv_recyc)
            self.dq_inv_recyc = dq_inv_recyc
        else:
            self.dq_inv_recyc = np.zeros(dq_inv_induced.shape)
            
        # EXOG added
        if sum(dy_inv_exog) != 0:
            dq_inv_exog = np.dot(self.L_BASE, dy_inv_exog)
            self.dq_inv_exog = dq_inv_exog
        else:
            self.dq_inv_exog = np.zeros(dq_inv_induced.shape)
        
        return self.dq_inv_induced, self.dq_inv_recyc, self.dq_inv_exog
    

    def calc_dq_supply_constraint(self, A_trade, supply_constraint):
        # supply_constraint
        # REG_imp PROD_COMM Value Type
        # TODO: non-percent type

        # dy = sum(dy_array)

        sc_ = supply_constraint[supply_constraint['Type'].str.contains("rel")].copy()
        sc_ = sc_.astype({'PROD_COMM':'int16'})

        if len(sc_) > 0:
            sc_['id'] = list(zip(sc_['REG_imp'],sc_['PROD_COMM']))
            sc_ = sc_.set_index('id')

            sc_temp = pd.DataFrame(np.zeros((self.DIMS,1)), index=self.A_id, columns=['Value'])
            sc_temp.loc[sc_.index, 'Value'] = sc_['Value'].values
            
            sc_max = sc_temp.fillna(np.inf)['Value'].to_numpy()
            sc_temp = sc_temp.fillna(0)['Value'].to_numpy()

            q_max = (self.q_base) * (1 + sc_max)
            dq_impact = (self.q_base) * sc_temp
            
            # 19680 array of supply constraint modifiers
            # now let's iterate conditional on the new q_max

            # ! the thing is if there are multiple impacts from different sectors, we want to keep the minimum
            # ! but we don't want to duplicate the effects, so we need to iterate on dq_impact

            dq_impact_in = None
            for i in range(0, len(dq_impact)):
                dq_impact_ = np.zeros(len(dq_impact))
                dq_impact_[i] = dq_impact[i]
                if dq_impact_in is None:
                    dq_impact_in = dq_impact_
                else:
                    dq_impact_in = np.vstack([dq_impact_in, dq_impact_])

            dq_impact_out = None
            for i in range(0,len(dq_impact)):
                dq_impact_out_ = np.dot(self.G_BASE.T, dq_impact_in[i])
                if dq_impact_out is None:
                    dq_impact_out = dq_impact_out_
                else:
                    dq_impact_out = np.vstack([dq_impact_out, dq_impact_out_])
                    
            idx = np.abs(dq_impact_out).argmax(axis=0)
            dq_impact = dq_impact_out[idx, np.arange(dq_impact_out.shape[1])]
            
            del dq_impact_in, dq_impact_out

            # should not go beyond 100%
            dq_impact[(dq_impact * -1) > self.q_base] = self.q_base[(dq_impact * -1) > self.q_base] * -0.90
            # import pdb; pdb.set_trace()

            # import pdb; pdb.set_trace()

            # do while we have sector where q is higher than q_max
            # q_est = self.q_iterate(A_trade, (self.q_base + dq_total_pos + dq_impact), (self.y0))

            # i = 0
            # steps = 10
            # print('Supply constraint calc started')

            # while len(q_est[q_est > q_max]) > 0 and i <= steps:
            #     print("At step: %s" % i)
            #     y_est = q_est
            #     y_est[q_est < q_max] = 0
            #     y_est[q_est > q_max] = q_max[q_est > q_max] - q_est[q_est > q_max]
            #     q_est = self.q_iterate(A_trade, q_est, (self.y0 + y_est), steps=50)
            #     i += 1

            # if i >= steps:
            #     print("Supply constraint iteration does not converge after %s steps" % steps)

            # result = {'dq_supply_constraint': (q_est - (self.q_base + dq_total_pos)),
                    #   'dy_supply_constraint': y_est}
        else:
            dq_impact = np.zeros(len(self.q_base))

        result = {'dq_supply_constraint': dq_impact,
                  'dy_supply_constraint': None}
        
        self.dq_supply_constraint = dq_impact
        
        return result

