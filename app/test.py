import os
from pathlib import Path
from DESA import LoadEpitopLoeDB, DataPreparation
from DESA.LoadEpitopLoeDB import _Load_HLADF, _Load_MFIDF
# from DESA.Analysis import 

## test code to for Epitope DB
# EpitopeDB = LoadEpitopeDB.load_EpitopeDB('../data/Epitope_DB_Expossure.xlsx')
# EpitopeDB = DataPreparation.prep_EpitopeDB(EpitopeDB)
# # print(EpitopeDB.drop(['PolymorphicResidues', 'Frequency', 'StructEpitope'], axis=1))
# Allel_type = 'AllAlleles'
# Exposure = 'Exposed'
# Reactivity = 'All' #'Confirmed'
# ElliPro_Score = 'All'
# EpitopeDB2 = DataPreparation.EpvsHLA2HLAvsEp(EpitopeDB, Allel_type, Exposure, Reactivity, ElliPro_Score)

"""
The MFI only takes into account the ManConcl_Immucor information 
"""
MFI = _Load_MFIDF('~/UMCUtrecht/RawData/MFI.csv')
MFI = DataPreparation.prep_MFI(MFI, Exclude_Locus=['DP'])

HLA = _Load_HLADF('~/UMCUtrecht/ProcessedData/UpscaledHLA.xlsx')
HLA = DataPreparation.prep_HLA(HLA)
print(MFI.Locus.value_counts())
