"""
Check what's actually in the .pkl files
"""
import pickle

# Check COU_ID
try:
    with open('GLORIA_db/v57/2019/parsed_db_original/cid.pkl', 'rb') as f:
        cid = pickle.load(f)
    print("=" * 80)
    print("COU_ID from cid.pkl:")
    print("=" * 80)
    print(f"Type: {type(cid)}")
    print(f"Length: {len(cid)}")
    print(f"First 10: {cid[:10]}")
    print(f"Contains BGR: {'BGR' in cid}")
    print(f"Contains ROW: {'ROW' in cid}")
    print()
except Exception as e:
    print(f"Error reading cid.pkl: {e}")

# Check SEC_ID
try:
    with open('GLORIA_db/v57/2019/parsed_db_original/sid.pkl', 'rb') as f:
        sid = pickle.load(f)
    print("=" * 80)
    print("SEC_ID from sid.pkl:")
    print("=" * 80)
    print(f"Type: {type(sid)}")
    print(f"Length: {len(sid)}")
    print()
except Exception as e:
    print(f"Error reading sid.pkl: {e}")

# Check IND_BASE structure
try:
    import pandas as pd
    IND_BASE = pd.read_pickle('GLORIA_db/v57/2019/parsed_db_original/IND_sparse.pkl')
    print("=" * 80)
    print("IND_BASE from IND_sparse.pkl:")
    print("=" * 80)
    print(f"Shape: {IND_BASE.shape}")
    print(f"Index names: {IND_BASE.index.names}")
    reg_exp_unique = IND_BASE.index.get_level_values('REG_exp').unique()
    print(f"Unique REG_exp: {len(reg_exp_unique)} regions")
    print(f"Sample: {sorted(reg_exp_unique.tolist())[:10]}")
    print()
except Exception as e:
    print(f"Error reading IND_sparse.pkl: {e}")
