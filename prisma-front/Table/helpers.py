from os.path import exists
import pandas as pd

from .config_tab import *

def importing_data(csv_file: str, verbose:bool = True) -> pd.DataFrame:
    '''Returning pandas Dataframe from csv file'''
    if not exists(csv_file):
        raise FileExistsError("Could not find {}".format(csv_file))
    df = pd.read_csv(csv_file,
                     low_memory=False)

    if verbose:
        print('Importing dataframe from {} ({} entries; {} columns)'.format(csv_file, len(df), len(df.columns)))
    return df

def clean_dataframe(df:pd.DataFrame, verbose = True):
    '''Cleaning MOF pandas dataframe by\n
        - deleting leadin/trailing spaces in columns names
        - deleting columns by prefix (['[US', '[GB' , '[CN', '[CH', 'Henr', 'IAST', 'TS'])
        - deleting columns by column name (['A', 'B', 'C', 'Alpha', 'Beta', 'Gamma', 'WR', 'Heat_Avg', 'Uptake_IAST', 'Di', 'Dif'])
        - renaming columns names: Df to PLD / unit
        - chaningin significant numbers to 4
        - deleting trailing spaces in data for string columns names (['name', 'Type', 'Formula', 'DOI'])
        - adding units to columns from given col_dict (from yml file)
        '''

    #deleting leadin/trailing spaces in columns names
    renaming_cols = {ori_col : ori_col.strip() for ori_col in df.columns}
    df.rename(columns=renaming_cols, inplace= True)
    if verbose:
        print('Renaming: Deleting trailing spaces in {} columns'.format(len(renaming_cols)))

    #significant numbers
    df = df.round(4)

    #deleting trailing spaces in data for string columns names
    str_columns = ['Label', 'Source', 'Formula', 'Link to Publication']
    for column in str_columns:
        df[column] = df[column].str.strip()
    if verbose:
        print('Deleted: spaces from data entries removed from str columns ({})'.format(str_columns))

    df = df[HEADER_ORDER]

    return df