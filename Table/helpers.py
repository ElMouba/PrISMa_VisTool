from os.path import exists, join
import pandas as pd
import yaml

from bokeh.io import curdoc

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

def import_column_info(verbose = True) -> dict:
    '''Importing columns info from yaml file to dict {column:unit}'''
    if not exists(COLFILE):
        raise FileExistsError("Could not find {}".format(COLFILE))

    with open((COLFILE), 'r') as f:
        quantity_list = yaml.full_load(f)
        if verbose:
            print('{} entries in {}'.format(len(quantity_list), COLFILE))

    col_dict = {i['column']: i['unit'] for i in quantity_list}
    return col_dict

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

def adding_cif_directory(dataframe: pd.DataFrame):
    if not exists(CIF_DIR):
        raise NotADirectoryError('Given directory for cif files ({}) not found...'.format(CIF_DIR))
    
    if 'cif_dir' not in dataframe.columns:
        print('cif_dir column not in dataframe, will be added.')
        dataframe['CIF_BOOL'] = False
        dataframe['CIF_dir'] = 'Not Found'

    not_found = 0
    print('Searching cif files in {}'.format(CIF_DIR))
    for index, row in dataframe.iterrows():

        name = (row['name'])
        cif_file = f'{name}.cif'
        cif_file_dir = join(CIF_DIR, cif_file)

        if exists(cif_file_dir):         
            dataframe.at[index, 'CIF_BOOL'] = True
            dataframe.at[index, 'CIF_dir'] = cif_file_dir
        
        else:
            not_found += 1
            dataframe.at[index, 'CIF_BOOL'] = False
            dataframe.at[index, 'CIF_dir'] = 'Not Found'
    
    print('CIF files not found for {}/{} ({} %)'.format(not_found, len(dataframe), round((not_found/len(dataframe)*100), 2)))
    return dataframe
        

def adding_cif_content(dataframe:pd.DataFrame) -> pd.DataFrame:
    for i, row in dataframe.iterrows():
        if row['CIF_BOOL']:
            cif_file = (row['CIF_dir'])
            content = []
            with open(cif_file, 'r+') as f:
                content = f.read()
            
            dataframe.at[i, 'CIF_content'] = content
        else:
            dataframe.at[i, 'CIF_content'] = 'N/A'
    return dataframe

