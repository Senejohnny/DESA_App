import pandas as pd
import numpy as np
import sys
# print(sys.path)
print(__name__)

def load_EpitopeDB(path:str) -> pd.DataFrame:
    """
    path: abs path to the Epitope DB
    """
    # Load different sheets from excel as df and then concatenate all df's vertically 
    df_ABC = pd.read_excel(path, sheet_name='ABC')
    df_DRB1 = pd.read_excel(path, sheet_name='DRB1')
    df_DQB1 = pd.read_excel(path, sheet_name='DQB1')
    return pd.concat([df_ABC, df_DRB1, df_DQB1])

def _Load_HLADF(path:str) -> pd.DataFrame:
    """
    Internal function to just load HLA data
    """
    df = pd.read_excel(path)
    df = df.rename(columns={"RecipientHLAType_PROCAREorNMDP": 'Recipient_HLA', 'DonorHLAType_PROCAREorNMDP' : 'Donor_HLA' })
    return df
    
def _Load_MFIDF(path:str) -> pd.DataFrame:
    """
    Internal function to just load MFI data set
    """
    MFI = pd.read_csv(path, sep=';')
    MFI['Specificity'] = MFI['Specificity'].apply(lambda x: set(x.split(',')))
    MFI = MFI.drop(['SampleID', 'CatalogID', 'Gate_LUM', 'Analyte_LUM', 'MedianFI', 'TMeanFI', 'Probe77_MedianFI', 'Probe77_TMeanFI',
                'CON1_MedianFI', 'CON1_TMeanFI'], axis=1)
    return MFI
