import pandas as pd
import numpy as np


def load_EpitopeDB(path:str) -> pd.DataFrame:
    """
    path: abs path to the Epitope DB
    """
    # Load different sheets from excel as df and then concatenate all df's vertically 
    df_ABC = pd.read_excel(path, sheet_name='ABC')
    df_DRB1 = pd.read_excel(path, sheet_name='DRB1')
    df_DQB1 = pd.read_excel(path, sheet_name='DQB1')
    return pd.concat([df_ABC, df_DRB1, df_DQB1])

    

