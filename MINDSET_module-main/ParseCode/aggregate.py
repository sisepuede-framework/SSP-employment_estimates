# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 23:53:48 2023

@author: ghardadi
"""

# Collected from pySUT written by Konstantin Stadler, Stefan Pauliuk

import numpy as np

def MI_Tuple(value, Is): 
    """
    Define function for obtaining multiindex tuple from index value
    value: flattened index position, Is: Number of values for each index dimension
    Example: MI_Tuple(10, [3,4,2,6]) returns [0,0,1,4]
    MI_Tuple(138, [100,10,5]) returns [2,7,3]
    MI_Tuple is the inverse of Tuple_MI.
    """
    IsValuesRev = []
    CurrentValue = value
    for m in range(0,len(Is)):
        IsValuesRev.append(CurrentValue % Is[len(Is)-m-1])
        CurrentValue = CurrentValue // Is[len(Is)-m-1]
    return IsValuesRev[::-1]    

def Tuple_MI(Tuple, IdxLength): 
    """
    Function to return the absolution position of a multiindex when the index
    tuple and the index hierarchy and size are given.
    Example: Tuple_MI([2,7,3],[100,10,5]) returns 138
    Tuple_MI([0,0,1,4],[3,4,2,6]) returns 10
    Tuple_MI is the inverse of MI_Tuple.
    """
    # First, generate the index position offset values
    IdxShift =  IdxLength[1:] +  IdxLength[:1] # Shift 1 to left
    IdxShift[-1] = 1 # Replace lowest index by 1
    IdxShift.reverse()
    IdxPosOffset = np.cumproduct(IdxShift).tolist()
    IdxPosOffset.reverse()
    Position = np.sum([a*b for a,b in zip(Tuple,IdxPosOffset)])
    return Position

def build_Aggregation_Matrix(Position_Vector): # from PySUT
    """Turn a vector of target positions into a matrix that aggregates 
    or re-arranges rows of the table it is multiplied to from the left 
    (or columns, if multiplied transposed from the right)"""
    # Maximum row number of new matrix (+1 to get the right length,
    # as 0 is the smallest target position entry.)
    AM_length = Position_Vector.max() + 1
    # Number of rows of the to-be-aggregated matrix
    AM_width  = len(Position_Vector)
    Rearrange_Matrix = np.zeros((AM_length,AM_width))
    # place 1 in aggregation matrix at [PositionVector[m],m], so that
    # column m is aggregated with Positionvector[m] in the aggregated matrix
    for m in range(0,len(Position_Vector)):
        Rearrange_Matrix[Position_Vector[m].item(0),m] = 1
    return Rearrange_Matrix

def build_MultiIndex_Aggregation_Matrix(Position_Vectors):
    """Turn a list of vectors of target positions that represent aggregations
    of the different levels of a multi-index of a table into a matrix that
    aggregates or re-arranges rows of the multiindex table it is multiplied to
    from the left (or columns, if multiplied transposed from the right)"""   
    OldLength = [len(i)    for i in Position_Vectors]
    NewLength = [max(i) +1 for i in Position_Vectors]
    Rearrange_Matrix = np.zeros((np.product(NewLength),np.product(OldLength)))
    for m in range(0,np.product(OldLength)):
        # convert running index to tuple (column index)
        OldIndexTuple = MI_Tuple(m,OldLength)
        # convert unaggregated tuple to aggregated tuple
        NewIndexTuple = [Position_Vectors[i][OldIndexTuple[i]] for i in range(
            0,len(OldIndexTuple))]
        # Calculate new running index (row index)
        NewIndexPos   = Tuple_MI(NewIndexTuple, NewLength)
        # Aggregate/resort row m into row NewIndexPos.
        Rearrange_Matrix[NewIndexPos,m] = 1 
    return Rearrange_Matrix
