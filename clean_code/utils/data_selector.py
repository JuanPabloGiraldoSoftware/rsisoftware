import pathlib
import os
import pandas as pd

"""
name: get_datasets_source()
params: none
return: datasets parent directory
"""
def get_datasets_source():
    current_source=pathlib.Path(__file__).parent.resolve()
    prev_source=os.path.abspath(os.path.join(current_source,os.pardir))
    absolute=os.path.abspath(os.path.join(prev_source,os.pardir))
    return absolute+"/datasets"

"""
name: get_data()
params: datasets absolute path, csv file name
return: DataFrame object 
"""
def get_data(source,dfile):
    return pd.read_csv("{}/{}.csv".format(source,dfile))