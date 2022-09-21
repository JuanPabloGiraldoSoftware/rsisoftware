from utils import data_selector as ds

DATASETS_SOURCE=""

def main():
    global DATASETS_SOURCE
    DATASETS_SOURCE=ds.get_datasets_source()
    df = ds.get_data(DATASETS_SOURCE,"WATCHLIST")
    print(df)

main()