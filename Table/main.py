""" MOF entries in a datatable """

import bokeh.models as bmd
import pandas as pd
import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from config_tab import *
from os.path import dirname, join
from .helpers import importing_data, clean_dataframe

# js scripts
dowload_csv = open(join(dirname(__file__), "static/js/download_csv.js")).read()
download_cif_js = open(join(dirname(__file__), 'static', 'js', 'download_cif.js')).read()
properties_direct = open(join(dirname(__file__), 'static', 'js', 'properties_direct.js')).read()
table_direct = open(join(dirname(__file__), 'static', 'js', 'table_direct.js')).read()
structure_direct = open(join(dirname(__file__), 'static', 'js', 'structure_direct.js')).read()

# Importing and Cleaning Data
df = importing_data(DATA_FILE, verbose=VERBOSE)
DF_LEN = len(df)
df = clean_dataframe(df, verbose=VERBOSE)

def get_name_from_url(df:pd.DataFrame)-> str:
    """Get structure name from URL parameter. 
    Returns:
    --------
    name: str
        name of the MOF extracted from the URL 
        If no 'Label' parameter, returns a dummy MOF (CALF20)
    """
    freeze = False
    args = curdoc().session_context.request.arguments

    try:
        name = args.get('name')[0]
        if isinstance(name, bytes):
            name = name.decode()
            freeze = True
    except (TypeError, KeyError) as e:
        freeze = False
        name = 'CALF20'

    entry = df.loc[df['Label'] == name]
    index = entry.index
    df_ = df.drop(index)
    new_df = pd.concat([entry, df_], ignore_index = True)

    return new_df, freeze

df, freeze_BOOL = get_name_from_url(df)

def create_table(dataframe:pd.DataFrame) -> bmd.DataTable:
    '''Creating main table from pandas dataframe\n
    - clickable link on DOI if present; else plain text
    - numbers in table to FONTSIZE
    - strings in table to FONTSSIZE
    - reorder columns; first all string columns (['Label', 'Type', 'Formula']), DOI column and number columns 
    - create table with hardcoded settings
    '''
    global  source, data_table
    source = bmd.ColumnDataSource(dataframe)

    template_doilink = """
        <a style = "font-size: 13px;
                    <%= 
                        (function format(){
                            if(value == 'Not Available'){
                                return("pointer-events: none; color: black; cursor:default; text-decoration: none;")}
                            else{return("pointer-events: auto; color: blue")}
                                }()) %>; 
                    "
            href="https://doi.org/<%= value %>" 
            target=”_blank">
            <%= value %>
        </a>
                """

    template_column = f"""
                        <div style = "font-size: {FONTSIZE}px;"> <%= value %> </div>
                        """

    bokeh_columns = []
    for column in HEADER_ORDER:

        if column not in dataframe.columns:
            continue
        
        if column == 'Label':
            column_obj = bmd.TableColumn(field = 'Label', title = 'Label', 
                                    formatter = bmd.HTMLTemplateFormatter(template=template_column))

        elif column == 'Link to Publication':
            column_obj = bmd.TableColumn(field = 'Link to Publication', title = 'Link to Publication', 
                                    formatter = bmd.HTMLTemplateFormatter(template=template_doilink))

        else:
            column_obj = bmd.TableColumn(field= column, title = column,
                                    formatter = bmd.HTMLTemplateFormatter(template = template_column))
            
        bokeh_columns.append(column_obj)

    data_table = bmd.DataTable(source=source,
                           columns=bokeh_columns,
                           width=1500,
                           height=TABLE_HEIGHT,
                           background = '#aaadad',
                           index_position=None,
                           autosize_mode= 'force_fit',
                           frozen_rows = 0,
                           frozen_columns = 1,
                           reorderable = True,
                           selectable = True,
                           sortable = True,
                           scroll_to_selection = False,
                           css_classes = ['table'])
    if freeze_BOOL:
        data_table.frozen_rows = 1

    return data_table

# Create inital datatable
datatable = create_table(df)

# Compare Button
def change_selection(verbose = VERBOSE):
    """Compare button handler\n\n
    - Adding: extract current selection, moves to top of dataframe and freeze number of rows
    - Deleting: extract current selection and delete them from freezing rows
    - if frozen selection, column sorting disabled (will sort selection with it and ruins frozen rows)
    - updates comparison info text
    """
    global df, ignore_index_change
    
    selected_ix = datatable.source.selected.indices

    deleting_counter = 0
    all_selected_rows= selected_ix
    if type(datatable.frozen_rows) == type(10):
        frozen_ix = list(range(datatable.frozen_rows))
        all_selected_rows = frozen_ix + selected_ix       
        for index in selected_ix:
            if index<datatable.frozen_rows:
                all_selected_rows.remove(index)
                deleting_counter += 1
    else:
        pass
    
    selected_df = df.loc[all_selected_rows]

    df_dropped = df.drop(df.index[all_selected_rows])

    df = pd.concat([selected_df, df_dropped], ignore_index=True)

    datatable.source.data = df
    datatable.frozen_rows = len(all_selected_rows) - deleting_counter

    ignore_index_change = True
    datatable.source.selected.indices  = [len(df) -2 , len(df)-1]
   
    if datatable.frozen_rows == 0:
        sorting_switch.active = [0,1]
        button_copy.disabled = True
        button_selection_csv.disabled = True

    else:
        sorting_switch.active = [1]
        button_copy.disabled = False
        button_selection_csv.disabled = False

    button_copy.label="Copy Selection ({}) to Clipboard".format(datatable.frozen_rows)
    button_selection_csv.label = "Download Selection ({})".format(datatable.frozen_rows)

    # Sanity check 
    if len(df) != DF_LEN:
        raise ValueError("LENGHT OF DF HAS CHANGED!")

# Sorting Switch
def switch_handler(attr, old, new):
    '''if activated, frozen rows to 0 and sorting via column allowed'''
    if new == [0,1]:
        data_table.sortable = True
        data_table.frozen_rows = 0
        sorting_switch.labels = ['Sorting Allowed']
        
    if new == [1]:
        data_table.sortable = False
        sorting_switch.labels = ['Sorting Disabled']
        
sorting_switch = bmd.CheckboxButtonGroup(labels = ['Allow Sorting'], active = [1], width = 10)
sorting_switch.on_change('active', switch_handler)


previous_selected_index = [0,0]
ignore_index_change = False
def selection_handler_doubleclick2(attr, old, new):
    global previous_selected_index, ignore_index_change
    if ignore_index_change:
        ignore_index_change = False
        return
    
    if len(new) > 2:
        ignore_index_change=True
        return

    first_selected = new[0]

    if first_selected == previous_selected_index[0]:
        datatable.source.selected.indices = [first_selected]
        change_selection()
    else:
        datatable.source.selected.indices = [first_selected, len(df)-1]
        previous_selected_index = [first_selected, len(df)-1]

def selection_handler_cif(attr, old, new):
    global selected
    entry_name = datatable.source.data['Label'][new[0]]
    name_cif_file = '{}.cif'.format(entry_name)
    cif_directory = os.path.join(CIF_DIR, name_cif_file)
    if os.path.exists(cif_directory):
        btn_download_cif.disabled = False
        with open(cif_directory, 'r') as f:
            content = f.read()
        name_cif_file = '{}.cif'.format(entry_name)
        btn_download_cif.tags = [content, name_cif_file]
    else:
        btn_download_cif.disabled = True

    btn_properties.disabled = False
    btn_download_cif.label = "Download CIF ({})".format(entry_name)
    btn_properties.tags = [entry_name]

    btn_structure.disabled = False
    btn_structure.label = "View structure ({})".format(entry_name)
    btn_structure.tags = [entry_name]

source.selected.on_change('indices', selection_handler_doubleclick2)
source.selected.on_change('indices', selection_handler_cif)

# Copy button
def copy_handler():
    '''Copies current selection to clipboard (data copy in table is not possible in bokeh)'''
    copied_df = df.head(data_table.frozen_rows)
    try:
        copied_df.to_clipboard()
    except:
        print('Could not copy data to clipboard (see https://pyperclip.readthedocs.io/en/latest/#not-implemented-error)...')
        
button_copy = bmd.Button(label="Copy Selection to Clipboard", disabled = True, width=WWIDTH)
button_copy.on_click(copy_handler)

# Selection to csv Button
button_selection_csv = bmd.Button(label = "Download Selection", disabled = True, tags = [0], width=WWIDTH)
button_selection_csv.js_on_click(bmd.CustomJS(args = dict(source = datatable.source, csv_file_name = 'SelectedMOFs'),
                                              code = dowload_csv))
# To csv file button
botton_csv = bmd.Button(label="Download all data", tags = [DF_LEN], width=WWIDTH)
botton_csv.js_on_click(bmd.CustomJS(args = dict(source = datatable.source, csv_file_name = 'AllMOFdata'), code = dowload_csv))

# Frozen row on change handler
def frozen_rows_handler(attr, old, new):
    button_selection_csv.label = "Download Selection"
    button_copy.label = "Copy Selection to Clipboard"
    sort_selection_select.title = 'Sort selection by:'
    button_selection_csv.tags = [new]
    if new == 0:
        button_copy.disabled = True
        button_selection_csv.disabled = True

datatable.on_change('frozen_rows', frozen_rows_handler)

# Search MOF input
def search_handler(attr, old, new):
    '''Changes to index of MOF upon change'''   
    global ignore_index_change

    index = list(df['Label']).index(new)

    ignore_index_change = True
    datatable.source.selected.indices = [index]

    change_selection()
    
search_function = bmd.AutocompleteInput(title = 'Search for MOF: ', completions = list(df['Label']), width=WWIDTH)
search_function.on_change('value', search_handler)

# Sort selection
# Sorting not possible on frozen row https://github.com/bokeh/bokeh/issues/3564
def sort_selection(attr, old, new):
    selection = datatable.frozen_rows
    df_selection = df.head(selection)
    df_rest = df.iloc[selection:]
    
    key = None
    if new == 'Label':
        key = lambda new: new.str.lower()
    df_selection = df_selection.sort_values(by = [new], key = key)
    df_rest = df_rest.sort_values(by = [new], key = key)

    sorted_dataframe = pd.concat([df_selection, df_rest], ignore_index=False)
    datatable.source.data = sorted_dataframe

sort_selection_select = bmd.Select(title = 'Sort selection by:', value = 'Label', options = SORTING_OPTIONS, width=WWIDTH)
sort_selection_select.on_change('value', sort_selection)

# Download cif
btn_download_cif = bmd.Button(label='Download CIF', button_type='primary', tags = ['Nothing Selected', 'None.cif'],
                              disabled = True, width=410)
btn_download_cif.css_classes = ['custom_button_1']
btn_download_cif.js_on_click(bmd.CustomJS(code=download_cif_js))

# Go to properties
btn_properties = bmd.Button(label='Adsorption Properties', button_type='primary', tags = ['Nothing Selected'],
                            disabled = True, width=410)
btn_properties.css_classes = ['custom_button_1']
btn_properties.js_on_click(bmd.CustomJS(code=table_direct))

# Go to structure
btn_structure = bmd.Button(label='View Structure', button_type='primary', tags = ['Nothing Selected/Structure'],
                            disabled = True, width=410)
btn_structure.js_on_click(bmd.CustomJS(code=structure_direct))

# Document Layout
curdoc().title = 'Database'
top_row = row(search_function, sort_selection_select)
sorting_option = row(sorting_switch)
selection_options = row(button_copy, button_selection_csv)
curdoc().add_root(column(top_row, datatable, sorting_option, selection_options, botton_csv, btn_download_cif, btn_properties, btn_structure))