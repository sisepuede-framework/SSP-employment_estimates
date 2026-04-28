# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 17:36:45 2023

@author: wb582890
"""

import numpy as np

class GDP():
    def __init__(self, IO_model):
        self.A_BASE = IO_model.A_BASE
        self.q_base = IO_model.q_base
    
    def calc_gdp_base(self):
        I = np.identity(len(self.A_BASE))
        # Output is multiplied here with Identity matrix - Input coefficients
        # This derives value added coefficients which are then multiplied with
        # gross output
        self.gdp_base = self.q_base * np.sum(I - self.A_BASE, axis=0)
        
        return self.gdp_base
    
    def calc_gdp_changes(self, dq, A1):
        if type(dq) != list:
            I = np.identity(len(self.A_BASE))
            dgdp = dq * np.sum(I - A1, axis=0)
            return dgdp
        else:
            dgdp = {}
            I = np.identity(len(self.A_BASE))
            
            for i in range(len(dq)):
                dgdp_i = dq[i] * np.sum(I - A1, axis=0)
                dgdp[i] = dgdp_i
            return dgdp.values()
    