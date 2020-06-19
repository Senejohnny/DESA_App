import pandas as pd
from typing import Tuple
from DESA.utils import return_oneset
# return_oneset should be used in Separate_HLA_Beads later
##############################################################
# Per Transplant ID get the Donor and Recipient HLA separately
##############################################################
def get_DonorRecipient_HLA(HLA:pd.DataFrame, TransplantID:int) -> Tuple[set, set]:
    """
    Parameters:
        HLA: pd. DataFrame
            High reseloution HLA Dataframe, with 3 columns TransplantID, Recipient_HLA, and Donor_HLA, respectively. 
        TransplantID: int
    """
    ind_Upscaled_HLA = Upscaled_HLA['TransplantID'] == TransplantID
    if ind_Upscaled_HLA.sum() == 0:
        return f'No Uplscaled_HLA for Donor & Recipient for TransplantID {TransplantID} '
    # get Donor & Recipient HLA 
    Recipient_HLA = Upscaled_HLA[ind_Upscaled_HLA]['Recipient_HLA'].values[0]
    Donor_HLA = Upscaled_HLA[ind_Upscaled_HLA]['Donor_HLA'].values[0]
    return Donor_HLA, Recipient_HLA


##############################################################
# Find Mismatched Epitopes
##############################################################
def mismatched_Epitopes(Donor_HLA:set, Recipient_HLA:set, HLAvsEpitope:pd.DataFrame, TransplantID:int) -> Tuple[set, set, set]:
    """
    This function get Donor and Recipient HLA, find their Epitopes and return {Donor Epitopes} - {Recipient Epitopes} 
    Parameters:
        Donor_HLA: set
        Recipient_HLA: set
        HLAvsEpitope: pandas Dataframe
        TransplantID:int
    """

    # Find all the epitopes in Recipient 
    ind1 = HLAvsEpitope['HLA'].apply(lambda x: x in Recipient_HLA)
    Recipient_Epitopes = set([Epitope for Set in HLAvsEpitope[ind1]['Epitope'].values for Epitope in Set])

    # Find all the epitopes in Donor 
    ind2 = HLAvsEpitope['HLA'].apply(lambda x: x in Donor_HLA)
    Donor_Epitopes = set([Epitope for Set in HLAvsEpitope[ind2]['Epitope'].values for Epitope in Set])

    # Epitope Mismatches
    Mismatched_Epitopes = Donor_Epitopes - Recipient_Epitopes
    return Donor_Epitopes, Recipient_Epitopes, Mismatched_Epitopes

##############################################################
# Find HLA on Positive and Negative Beads
##############################################################
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
        return f'No HLA Antibodies are available for the Transplant ID {TransplantID}'
    # Get the HLA's that are on the Positive and [Weak + Negative] Beads
    ind_pos_bead = MFI['ManConcl_Immucor'] == 'Positive'
    ind_neg_weak_bead = MFI['ManConcl_Immucor'] != 'Positive'  # Important to know that there are also weak and negative beads. 
    Pos_Bead = MFI[ind_Tx & ind_pos_bead]['Specificity'].values
    Neg_Bead = MFI[ind_Tx & ind_neg_weak_bead]['Specificity'].values
    
    # Put all the HLAs on the positive and negative beads into a separate set
    set_HLA_PosBead = set(sorted([HLA for HLAs in Pos_Bead for HLA in HLAs])) 
    set_HLA_NegBead = set(sorted([HLA for HLAs in Neg_Bead for HLA in HLAs])) 
    return set_HLA_PosBead, set_HLA_NegBead
