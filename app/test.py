
import os
import sys
print(sys.path)
from DESA import Loading, DataPreparation, Analysis
from DESA.Loading import _Load_HLADF, _Load_MFIDF
# from DESA.Analysis import *

""" 
The below script assumes that the imported data frames are not null and in good shape. Relevant checks will be done in a separate place.
"""
# test code to for Epitope DB
EpitopeDB = Loading.load_EpitopeDB('../data/Epitope_DB_Expossure.xlsx')
EpitopeDB = DataPreparation.prep_EpitopeDB(EpitopeDB)
# print(EpitopeDB.drop(['PolymorphicResidues', 'Frequency', 'StructEpitope'], axis=1))
Allel_type = 'AllAlleles'
Exposure = 'Exposed'
Reactivity = 'All' #'Confirmed'
ElliPro_Score = 'All'
HLAvsEpitope = DataPreparation.EpvsHLA2HLAvsEp(EpitopeDB, Allel_type, Exposure, Reactivity, ElliPro_Score)
print(HLAvsEpitope)
"""
The MFI only takes into account the ManConcl_Immucor information 
"""
MFI = _Load_MFIDF('~/UMCUtrecht/RawData/MFI.csv')
MFI = DataPreparation.prep_MFI(MFI, Exclude_Locus=['DP'])

HLA = _Load_HLADF('~/UMCUtrecht/ProcessedData/UpscaledHLA.xlsx')
HLA = DataPreparation.prep_HLA(HLA)
print(MFI.Locus.value_counts())

final_df = Analysis.write_DESAdf(HLA, MFI, HLAvsEpitope)
final_df.to_pickle('result.pickle')
# print(final_df)
# 'No HLA Antibodies are available for the Transplant ID {TransplantID}'

# from collections import defaultdict
# DESA = defaultdict(list)
# DESA['TransplantID'].append(1)
# print(DESA)