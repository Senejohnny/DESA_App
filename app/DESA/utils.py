import numpy as np
import regex as re
import io
from typing import Union
import csv
from detect_delimiter import detect
######################################################
    # Check the length of HLA
###################################################### 
def HLAlengthcheck(HLA:str) -> str:
    """
    This function is used pre_HLA, which gets an HLA and makes sure that the HLA does not have more information than Allel by truncating 
    the specific HLA protein and further details. This means if, e.g. the HLA DRB1*13:01:01 is passed in the returned 
    truncated string is  DRB1*13:01
    """

    colon_location = [m.start() for m in re.finditer(':', HLA)] 
    # The method re.finditer returns an object with methods (m.start(), m.end(), m.group(0)) 
    colon_number = len(colon_location)
    if colon_number > 1:
        colon_second = colon_location[1] # get the locatio of the second colon
        HLA = HLA[0:colon_second] # Keep the string until the second colon 
    return HLA

######################################################
# List of sets or set of sets to set
###################################################### 
def return_set(input:Union[str,set]) -> set:
    """
    This function returns a set from the values in the set of set or list of sets. e.g. {a, b, c, d } from {{a}, {b,c}, {d}} or [{a}, {b,c}, {d}] 
    """
    return set([value for Set in input for value in Set])


def detectdelimiter(file): 
    """
    this will detect the famous delimiters [',', ';', ':', '|', '\t'] 
    The input is _io.StringIO object. 
    """

    first_line = file.getvalue().split('\n')[0] # get the first line of the StringIO object
    return detect(first_line)   # apply the detect method