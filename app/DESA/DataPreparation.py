import pandas as pd
import numpy as np 
from typing import Union, List


#####################################################################################
# Preprocess the Epitope DB
#####################################################################################
def prep_EpitopeDB(EpitopeDB:pd.DataFrame) -> pd.DataFrame:
    """ 
    Get Epitope Dataframe, set the index of dataframe to the Epitopes, and make a set of each Allel column value
    """

    # Make Allels into set
    EpitopeDB['LuminexAlleles'] = EpitopeDB['LuminexAlleles'].apply(lambda x: set(sorted(x.split(sep=','))))
    EpitopeDB['AllAlleles'] = EpitopeDB['AllAlleles'].apply(lambda x: set(sorted(x.split(sep=','))))
    EpitopeDB = EpitopeDB.drop(['PolymorphicResidues', 'Frequency', 'StructEpitope'], axis=1)
    return EpitopeDB
    
#####################################################################################
# Filter and then Convert the EpitopeDB (Epitope vs HLA) to a HLA vs Epitope Table 
#####################################################################################
def EpvsHLA2HLAvsEp(EpitopeDB:pd.DataFrame, Allel_type:str, Exposure:str, Reactivity:str, ElliPro_Score:Union[List[str], str]) -> pd.DataFrame:
    """
    The input is EpitopevsHLA table, typ of HLA that we would like to take into account. The output is a data frame containing the HLAvsEpitope Table, with a HLA and Epitope Column
    
    Allel_type: {LuminexAllel, AllAlleles}
    Exposure: {Exposed, All(Exposed & not Exposed)}
    Reactivity: {Confirmed, Al'}
    ElliPro_Score: {All, High, intermediate, Low, Very Low} default:'All'. Input should be given as a string of 'All' or list or tuple             
    """
    # Filter the EpitopeDB with Exposure informmation
    if 'Exposed' in EpitopeDB.columns:
        if Exposure != 'All':  # If Exposure is not Al then it is Exposed
            ind_exp = EpitopeDB['Exposed'] ==  {'Exposed' : 'Yes', 'Not Exposed': 'No',}.get(Exposure)
            EpitopeDB = EpitopeDB[ind_exp]
        if Reactivity == 'Confirmed':
            ind_reac = EpitopeDB['AntibodyReactivity'] == Reactivity
            EpitopeDB = EpitopeDB[ind_reac]

    # Filter the EpitopeDB with ElliPro informmation
    if 'ElliProScore' in EpitopeDB.columns:
        if ElliPro_Score != 'All': 
            ind_scr = EpitopeDB['ElliProScore'].apply(lambda x: x in ElliPro_Score)
            EpitopeDB = EpitopeDB[ind_scr]
        if Reactivity == 'Confirmed':
            ind_reac = EpitopeDB['AntibodyReactivity'] == 'Yes'
            EpitopeDB = EpitopeDB[ind_reac]

    EpitopeDB = EpitopeDB[['Epitope', Allel_type]]
        
    # Define a dictionary in which the new table will reside 
    HLA_Epitopes = {'HLA': [], 'Epitope': []}
    # Get unique HLA and find all the Epitopes 
    for s in (EpitopeDB[Allel_type].values):
        for HLA in s:
            if HLA not in HLA_Epitopes['HLA']:
                HLA_Epitopes['HLA'].append(HLA)
                ind = EpitopeDB[Allel_type].apply(lambda x: HLA in x)
                Epitope = set(EpitopeDB[ind]['Epitope'].values) # set assignment is taking place here
                HLA_Epitopes['Epitope'].append(Epitope)
    return pd.DataFrame(HLA_Epitopes)

