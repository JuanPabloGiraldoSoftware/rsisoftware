import pathlib
import os
import pd as pandas

"""
name: get_datasets_source()
params: none
return: datasets parent directory
"""
def get_datasets_source():
    current_source=pathlib.Path(__file__).parent.resolve()
    absolute=os.path.abspath(os.path.join(current_source,os.pardir))
    return absolute+"/datasets"

"""
name: get_data()
params: csv file name
return: DataFrame object 
"""
def get_data(dfile):
    return pd.read_csv("{}/{}.csv".format(DATASETS_SOURCE,dfile))