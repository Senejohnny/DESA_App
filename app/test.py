import os
from pathlib import Path
from DESA import LoadEpitopeDB, DataPreparation


EpitopeDB = LoadEpitopeDB.load_EpitopeDB('../data/Epitope_DB_Expossure.xlsx')
EpitopeDB = DataPreparation.prep_EpitopeDB(EpitopeDB)
# print(EpitopeDB.drop(['PolymorphicResidues', 'Frequency', 'StructEpitope'], axis=1))
Allel_type = 'AllAlleles'
Exposure = 'Exposed'
Reactivity = 'All' #'Confirmed'
ElliPro_Score = 'All'
EpitopeDB2 = DataPreparation.EpvsHLA2HLAvsEp(EpitopeDB, Allel_type, Exposure, Reactivity, ElliPro_Score)
    
# print({'Exposed' : 'Yes', 'Not Exposed': 'No',}.get(Exposure))
print(EpitopeDB2)

def timeit(func):
        import time
        import functools

    @functools.wraps(func) # Without the use of this decorator factory, the name of the example function would have been 'wrapper', 
                           # and the docstring of the original example() would have been lost.
    def wrapper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        diff = tic - time.perf_counter()
        print(f'Function {func.__name__} executed in {diff}')
    return result
return wrapper

def logit(method):
        import logging
        import functools
        logging.basicConfig(filename=f'./logging/{method.__name__}.log', level=logging.INFO)
        
        @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f'Ran with args: {args}, and kwargs {kwargs}')
    return method(*args, **kwargs)
return wrapper




