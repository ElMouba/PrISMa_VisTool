''' MOF Adsorption Properties '''
import bokeh.models as bmd
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Whisker, Range1d, Spacer, ColumnDataSource, Select, StringFormatter, DataTable, TableColumn, Button
from bokeh.plotting import figure 
from config_ads import *
from decimal import Decimal
from os.path import join, dirname

## Java Scripts
#dowload_csv = open(join(dirname(__file__), "static/js/download.js")).read()

## Input Data
# Adsorption data
df = pd.read_csv(DATA_FILE)
#df_special = df[df["structure"]=="AlTBAPy"]

# Structures[]
list_structures = sorted(list(set(df["structure"])))

# Units and Labels
df_keys = pd.DataFrame({"Property": KEYS, "Label": LABELS, "Unit": UNITS, "Color": COLORS})

## Functions
# Get the name from the URL
def get_name_from_url()-> str:
    """Get structure name from URL parameter. 
    Returns:
    --------
    name: str
        name of the COF extracted from the URL 
        If no 'name' parameter (in bytes), returns a dummy COF (linker91_CH_linker92_N_clh_relaxed)
    """
    args = curdoc().session_context.request.arguments

    try:
        name = args.get('name')[0]
        if isinstance(name, bytes):
            name = name.decode()
    except (TypeError, KeyError):
        name = 'AlTBAPy'

    return name

def get_dataset(structure, molecule):
    """Extract henry and adsorption data based on user selection"""
    # Henry data
    Kh = df["henry"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0]
    Kh_stdev = df["henry_stdev"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0]
    Q_Kh = df["heat_henry"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0]
    Q_Kh_stdev = df["heat_henry_stdev"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0]

    # Adsorption data
    pre = pd.eval(df["pressure"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0])
    upt = pd.eval(df["uptake"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0])
    upt_stdev = pd.eval(df["uptake_stdev"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0])
    hea = pd.eval(df["heat"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0])
    hea_stdev = pd.eval(df["heat_stdev"][(df['structure']==structure) & (df['molecule']==molecule)].iloc[0])

    # Whisker data (error bars)
    upt_lower = [upt[i] - upt_stdev[i] for i in range(len(upt))]
    upt_upper = [upt[i] + upt_stdev[i] for i in range(len(upt))]
    hea_lower = [hea[i] - hea_stdev[i] for i in range(len(hea))]
    hea_upper = [hea[i] + hea_stdev[i] for i in range(len(hea))]

    # Output
    henry_data = {"henry": ["Henry Coefficient (mol.kg\u207B\xB9.Pa\u207B\xB9)", "{:.2E}".format(Decimal(Kh)) + ' \u00B1 ' + "{:.2E}".format(Decimal(Kh_stdev)),
                          'Henry Heat of Adsorption (kJ.mol\u207B\xB9)', "%.2f"%Q_Kh + ' \u00B1 ' + "%.2f"%Q_Kh_stdev]}
    adsor_data = {"pressure":pre, "uptake":upt, "uptake_lower":upt_lower, "uptake_upper":upt_upper, "heat":hea,
                  "heat_lower":hea_lower, "heat_upper":hea_upper}
    
    return ColumnDataSource(data=henry_data), adsor_data

def csv_Row_to_Column(df:pd.DataFrame):
    LIST_COLUMNS = ['pressure', 'uptake', 'uptake_stdev', 'heat', 'heat_stdev']
    SINGLEVALUE_COLUMNS = ['henry','henry_stdev', 'heat_henry', 'heat_henry_stdev']
    max_lenght = 0

    #searching max lenght of list columns
    for i, serie in df.iterrows():
        for column, data in serie.items():
            if column in LIST_COLUMNS:
                data = list(pd.eval(data))
                if len(data) > max_lenght:
                    max_lenght = len(data)

    new_dict = {}
    
    for _, serie in df.iterrows():
    
        molecule = serie['molecule']
        for column, data in serie.items():
            column_name = '_'.join([molecule, column])

            if column in SINGLEVALUE_COLUMNS:
                extra_none = max_lenght - 1
                extra_list = extra_none *['']
                final_list = [str(data)] + extra_list
                new_dict.update({column_name:final_list})
        
            elif column in LIST_COLUMNS:
                data_list = list(pd.eval(data))
                if len(data_list) < max_lenght:
                    extra_none = max_lenght - len(data_list)
                    extra_list = extra_none * ['']
                    print(type(data_list))
                    data_list = data_list + extra_list
                new_dict.update({column_name: data_list})

    new_df = pd.DataFrame(new_dict)

    return new_df 

def Download_properties_handler(structure):
    df = pd.read_csv(DATA_FILE)

    df_MOF = df[df['structure'] == structure ]

    new_df = csv_Row_to_Column(df_MOF)
    lenght_DF = len(new_df)

    df_bokeh = bmd.ColumnDataSource(new_df)

    try:    
        download_button.tags = [lenght_DF, df_bokeh, structure]
    except Exception as e:
        print('tags of download_button not changed ({})'.format(e))
        
    return df_bokeh

def make_plot(data_source, ylabel, df_keys):
    """A Bokeh script"""
    source = bmd.ColumnDataSource(data=data_source)
    source_error = ColumnDataSource(data=dict(base=data_source["pressure"], lower=data_source[ylabel+"_lower"],
                                              upper=data_source[ylabel+"_upper"]))
    
    if ylabel == "uptake":
        ylim_min = -0.15
        ylim_max = max(data_source[ylabel+"_upper"]) + 0.15
    else:
        ylim_min = min(data_source[ylabel+"_lower"]) - 0.15
        ylim_max = max(data_source[ylabel+"_upper"]) + 0.15

    p = figure(height=HEIGHT, width=WIDTH, toolbar_location='above',
               tools=['pan', 'wheel_zoom', 'box_zoom', 'save', 'reset'], active_drag='box_zoom')

    p.xaxis.axis_label = "Pressure (bar)"
    yax = df_keys["Label"][df_keys["Property"]==ylabel].iloc[0] + " (" + df_keys["Unit"][df_keys["Property"]==ylabel].iloc[0] + ")" 
    p.yaxis.axis_label = yax
    p.xaxis.axis_label_text_font_size = FONT_SIZE_LABEL
    p.yaxis.axis_label_text_font_size = FONT_SIZE_LABEL
    p.xaxis.major_label_text_font_size = FONT_SIZE_AXIS
    p.yaxis.major_label_text_font_size = FONT_SIZE_AXIS
        
    p.circle("pressure", ylabel, size=DATA_SIZE, color=df_keys["Color"][df_keys["Property"]==ylabel].iloc[0], source=source,
             alpha=0.5)
    p.add_layout(Whisker(source=source_error, base="base", upper="upper", lower="lower"))
    p.y_range = Range1d(ylim_min, ylim_max)

    return p

# Update the plot given the different options
def update_plot(attrname, old, new):
    structure = structure_select.value
    molecule = molecule_select.value
    ylabel = ylabel_select.value

    structureval = structures[structure]
    moleculeval = molecules[molecule]
    ylabelval = ylabels[ylabel]

    src0, src = get_dataset(structureval, moleculeval)
    table_data.data.update(src0.data)
    plot_data.update(src)

    download_button.disabled = False
    Download_properties_handler(structureval)

    layout.children[0].children[1] = column(make_plot(plot_data,ylabelval,df_keys), Spacer(margin=(0, 0, 30, 0)), row(Spacer(margin=(0, 300, 0, 0)), table))

## Initialize the dictionaries
structures = {i:i for i in list_structures}
molecules = {i:i for i in MOLECULES}
ylabels = {LABELS[i]:KEYS[i] for i in range(len(KEYS))}

## Default values
structure0 = list_structures[0]
molecule0 = 'CO2'
ylabel0 = 'Uptake'

## Initialize the select column
structure_select = Select(title='Structure', options=list(structures.keys()), value=get_name_from_url(), width=WWIDTH)
molecule_select = Select(title='Molecule', options=list(molecules.keys()), value=molecule0, width=WWIDTH)
ylabel_select = Select(title="Label (y-axis)", options=list(ylabels.keys()), value=ylabel0, width=WWIDTH)
download_button = bmd.Button(label="Download Properties", button_type='primary', tags = [27, None , 'None'], disabled = True, width=WWIDTH)
download_button.js_on_click(bmd.CustomJS(code=open(join(dirname(__file__), "static/js/download_csv.js")).read()))

## Get the initial plot data
table_data, plot_data = get_dataset(structures[get_name_from_url()], molecules[molecule0])

## Make the table
columns = [TableColumn(field='henry',title='Henry Regime Properties',formatter=StringFormatter(text_align="center"))]
table = DataTable(source=table_data, columns=columns, width=250, header_row=False, index_position=None)
     
for w in [structure_select,molecule_select,ylabel_select]:
    w.on_change('value', update_plot)

controls = column(structure_select,molecule_select,ylabel_select,download_button)

## Generate the page
layout = column(row(controls, column(make_plot(plot_data,ylabels[ylabel0],df_keys), Spacer(margin=(0, 0, 30, 0)), row(Spacer(margin=(0, 300, 0, 0)), table))))
curdoc().add_root(layout)
curdoc().title = "Adsorption Properties"