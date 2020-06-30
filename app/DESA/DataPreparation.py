import pandas as pd
import numpy as np 
import sys
from app.DESA.decorators import timer 
from typing import Union, List
from app.DESA.utils import HLAlengthcheck

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
# Preprocess the HLA Data Frame from Donor and Recipient 
#####################################################################################
def prep_HLA(df:pd.DataFrame) -> pd.DataFrame:
    """ 
    Cleaning steps: 1) Remove the letter G from the data frame if exist and split the HLA's and put them in a set, 2) check the length 
    of HLA and tailor it down to  the rqeuired detail (no more information than Allel by truncating the specific HLA protein and 
    further details). For example, the HLA DRB1* 13:01:01 is changed into DRB1* 13:01.
    """

   
    column_names = df.columns.tolist()
    df = df.rename(columns={column_names[0]: 'TransplantID', column_names[1]: 'Recipient_HLA', column_names[2] : 'Donor_HLA' })
    # Remove character 'G' from the data set 
    df['Recipient_HLA'] = df['Recipient_HLA'].apply(lambda x: set(x.replace('G','').split()))
    df['Donor_HLA'] = df['Donor_HLA'].apply(lambda x: set(x.replace('G','').split()))
    
    # Clean the HLA's that are longer than normal (Have more detail, i.e. twice the character ':')
    df['Recipient_HLA'] = [set([HLAlengthcheck(HLA) for HLA in Set]) for Set in df['Recipient_HLA']]
    df['Donor_HLA'] = [set([HLAlengthcheck(HLA) for HLA in Set]) for Set in df['Donor_HLA']]
    return df

#####################################################################################
# Preprocess the MFI Data Frame 
#####################################################################################
def prep_MFI(MFI:pd.DataFrame, Exclude_Locus:List[str]=['DP']) -> pd.DataFrame:
    """
    Filter the MFI data based on HLA Locus. 
    Parameters:
        MFI: The MFI Data Frame
        Exclude_Locus: A  list of Locuses at which we are not interested, possible choices ['A', 'B', 'C', 'DR', 'DQ', 'DP'] 
    """

    MFI['Specificity'] = MFI['Specificity'].apply(lambda x: set(x.split(',')))
    MFI = MFI.drop(['SampleID', 'CatalogID', 'Gate_LUM', 'Analyte_LUM', 'MedianFI', 'TMeanFI', 'Probe77_MedianFI', 'Probe77_TMeanFI',
                'CON1_MedianFI', 'CON1_TMeanFI'], axis=1)
    if len(Exclude_Locus)!=0:
        ind_dp = MFI['Locus'].apply(lambda x: x in Exclude_Locus)
        return MFI[~ind_dp] 
    else:
        return MFI

#####################################################################################
# Filter and then reorder the EpitopeDB [Epitope vs HLA] to [HLA vs Epitope] Table 
#####################################################################################
def filter_EpitopeDB(
    EpitopeDB:pd.DataFrame, 
    Allel_type:str, 
    DB_Opts:Union[List[str],str], 
    Reactivity:str, 
    ) -> pd.DataFrame:
    """
    The input is EpitopevsHLA table, typ of HLA that we would like to take into account. The output is a data frame containing the HLAvsEpitope Table, with a HLA and Epitope Column
    
    Allel_type: {Luminex Allel, All Alleles}
    DB_opts: if Epitope DB is based on Exposure, value is either 'Exposed' or 'All'(Exposed & not Exposed). 
    If the Epitope DB is based on Ellipro score, value is a list of {'High', intermediate, Low, Very Low}
    Reactivity: {Confirmed, All'}         
    """
    # Filter the EpitopeDB with Exposure informmation
    if 'Exposed' in EpitopeDB.columns:  # Then DB_opts is a string
        if DB_Opts != 'All':  # If Exposure is not All then it is Exposed
            ind_exp = EpitopeDB['Exposed'] ==  'Yes'    #{'Exposed' : 'Yes', 'Not Exposed': 'No',}.get(DB_opts)
            EpitopeDB = EpitopeDB[ind_exp]
        if Reactivity == 'Confirmed':
            ind_reac = EpitopeDB['AntibodyReactivity'] == Reactivity
            EpitopeDB = EpitopeDB[ind_reac]

    # Filter the EpitopeDB with ElliPro informmation
    if 'ElliProScore' in EpitopeDB.columns: # Then DB_opts is a list of strings
        if set(['High', 'Intermediate', 'Low', 'Very Low']) != set(DB_Opts) : 
            ind_scr = EpitopeDB['ElliProScore'].apply(lambda x: x in DB_Opts)
            EpitopeDB = EpitopeDB[ind_scr]
        if Reactivity == 'Confirmed':
            ind_reac = EpitopeDB['AntibodyReactivity'] == 'Yes'
            EpitopeDB = EpitopeDB[ind_reac]
    Allel_type = Allel_type.replace(' ','') # Remove white space from Allel_type name  
    return EpitopeDB[['Epitope', Allel_type]]

@timer
def EpvsHLA2HLAvsEp(EpitopeDB:pd.DataFrame, Allel_type:str) -> pd.DataFrame:
    """
    The input is EpitopevsHLA table, typ of HLA that we would like to take into account. 
    The output is a data frame containing the HLAvsEpitope Table, with a HLA and Epitope Column         
    """

    Allel_type = Allel_type.replace(' ','')
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


