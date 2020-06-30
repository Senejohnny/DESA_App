import pandas as pd
from typing import Tuple, Union, List
from tqdm import tqdm
from app.DESA.utils import return_set
from app.DESA.decorators import timer, logger, debug
from collections import defaultdict
##############################################################
# Per Transplant ID get the Donor and Recipient HLA separately
##############################################################
# @debug
def get_DonorRecipient_HLA(HLA:pd.DataFrame, TransplantID:int) -> Tuple[set, set]:
    """
    Parameters:
        HLA: pd. DataFrame
            High reseloution HLA Dataframe, with 3 columns TransplantID, Recipient_HLA, and Donor_HLA, respectively. 
        TransplantID: int
    """
    ind_HLA = HLA['TransplantID'] == TransplantID
    Recipient_HLA = HLA[ind_HLA]['Recipient_HLA'].values[0]
    Donor_HLA = HLA[ind_HLA]['Donor_HLA'].values[0]
    return Donor_HLA, Recipient_HLA

##############################################################
# Per Transplant ID find Mismatched Epitopes 
##############################################################
# @debug
def mismatched_Epitopes(Donor_HLA:set, Recipient_HLA:set, HLAvsEpitope:pd.DataFrame) -> Tuple[set, set, set]:
    """
    This function get Donor and Recipient HLA, find their Epitopes and return {Donor Epitopes} - {Recipient Epitopes} 
    Parameters:
        Donor_HLA: set
        Recipient_HLA: set
        HLAvsEpitope: pandas Dataframe
        TransplantID:int
    """

    # Find all the epitopes in Recipient 
    ind_recipient = HLAvsEpitope['HLA'].apply(lambda x: x in Recipient_HLA)
    Recipient_Epitopes = return_set(HLAvsEpitope[ind_recipient]['Epitope'].values)
    # Find all the epitopes in Donor 
    ind_donor = HLAvsEpitope['HLA'].apply(lambda x: x in Donor_HLA)
    Donor_Epitopes = return_set(HLAvsEpitope[ind_donor]['Epitope'].values)
    return Donor_Epitopes - Recipient_Epitopes

##############################################################
# Find HLA on Positive and Negative Beads
##############################################################
# @debug
def Separate_HLA_Beads(MFI:pd.DataFrame, TransplantID:int) -> Tuple[set, set]:
    """
    This function gets Luminex data and finds the HLA's on the positive and negative beads.
    Parameters:
        MFI : Luminex Dataset
        TransplantID: TransplantID
    """

    # filter the MFI based on Translpant ID
    ind_Tx = MFI['TransplantID'] == TransplantID
    if ind_Tx.sum() == 0:
        return 'No HLA Antibodies'
    # Get the HLA's that are on the Positive and [Weak + Negative] Beads
    ind_pos_bead = MFI['ManConcl_Immucor'] == 'Positive'
    ind_neg_weak_bead = MFI['ManConcl_Immucor'] != 'Positive'  # Important to know that there are also weak and negative beads. 
    HLA_Pos_Bead = MFI[ind_Tx & ind_pos_bead]['Specificity'].values
    HLA_Neg_Bead = MFI[ind_Tx & ind_neg_weak_bead]['Specificity'].values
    return return_set(HLA_Pos_Bead), return_set(HLA_Neg_Bead)

##############################################################
# Positive Epitopes from the Beads 
##############################################################
# @debug
def positive_Epitopes(HLAvsEpitope:pd.DataFrame, HLA_on_Bead:set) -> Tuple[set, set, str]:
    """
    Find the corresponding Epitope from HLAs on positive and non positive beads. 
    """
    HLA_on_PosBead, HLA_on_NegBead = HLA_on_Bead[0], HLA_on_Bead[1]
    # Partition HLA versus Epitope table (data frame) for HLAs on + and non+ Beads
    HLAvsEpitope_PosBead = HLAvsEpitope[HLAvsEpitope['HLA'].apply(lambda x: x in HLA_on_PosBead)]
    HLAvsEpitope_NegBead = HLAvsEpitope[HLAvsEpitope['HLA'].apply(lambda x: x in HLA_on_NegBead)]
    # Find the HLA's Epitopes and put them into a set
    Epitope_PosBead = return_set(HLAvsEpitope_PosBead['Epitope'].values)
    Epitope_NegBead = return_set(HLAvsEpitope_NegBead['Epitope'].values) 
    Positive_Epitope = Epitope_PosBead - Epitope_NegBead
    return Positive_Epitope, Epitope_PosBead, HLAvsEpitope_PosBead

##############################################################
# Find DESA
##############################################################
# @debug
def find_DESA(Mismatched_Epitopes:set, Positive_Epitope:set) -> set:
    return Mismatched_Epitopes.intersection(Positive_Epitope)

##############################################################
# Find corresponding_HLA of each DESA
##############################################################

def DESA_corresponding_HLA(DESA:set, Epitope_PosBead:set, HLAvsEpitope_PosBead:pd.DataFrame) -> set:
    from collections import defaultdict
    desa_corresponding_HLA = defaultdict(set)
    for Epitope in DESA:
        ind = HLAvsEpitope_PosBead['Epitope'].apply(lambda x: Epitope in x)
        desa_corresponding_HLA[Epitope].update(set(HLAvsEpitope_PosBead[ind]['HLA'].values))
    return desa_corresponding_HLA

#############################################################
# Write DESA results into a Data Frame
##############################################################
@timer
def write_DESAdf(
                HLA:pd.DataFrame, 
                MFI:pd.DataFrame, 
                HLAvsEpitope:pd.DataFrame, 
                TxIDs:Union[List[int], None] = None
                ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function writes the final result into a Data Frame

    Parameters:
        HLA: HLA Data Frame
        MFI: MFI Data Frame
        TxIDs: List[int], default is zero 
            The default zero value means go over all the Transplants ID in the Data Frame
    """

    DESAdic = defaultdict(list)
    for TransplantID in tqdm(HLA['TransplantID'] if TxIDs == None else set(TxIDs)):
        Donor_Recipient_HLA = get_DonorRecipient_HLA(HLA, TransplantID)
        HLA_on_Bead = Separate_HLA_Beads(MFI, TransplantID)
        if HLA_on_Bead == 'No HLA Antibodies':
            desa = desa_corresponding_HLA = 0
            Status = 'No HLA-E Abs' 
        else:
            Positive_Epitope, Epitope_PosBead, HLAvsEpitope_PosBead = positive_Epitopes(HLAvsEpitope, HLA_on_Bead)
            Mismatched_Epitopes = mismatched_Epitopes(Donor_Recipient_HLA[0], Donor_Recipient_HLA[1], HLAvsEpitope)
            DESA = find_DESA(Mismatched_Epitopes, Positive_Epitope)
            desa_corresponding_HLA = DESA_corresponding_HLA(DESA, Epitope_PosBead, HLAvsEpitope_PosBead)
            Status = 'DESA' if len(DESA) != 0 else 'No DESA' 
        DESAdic['TransplantID'].append(TransplantID)
        DESAdic['Status'].append(Status)
        DESAdic['DESA_Epitope'].append(DESA)
        DESAdic['#DESA'].append(len(DESA))
        DESAdic['DESA_corresponding_HLA'].append(desa_corresponding_HLA)
    return pd.DataFrame(DESAdic)
