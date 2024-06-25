''' Case Study Line Plots '''

import pandas as pd
import numpy as np
import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import LabelSet, ColumnDataSource, MultiChoice, Select, CustomJS, Spacer, Div, Button, HoverTool, Panel, widgets
from bokeh.plotting import figure
from config_lin import *

from jsmol_bokeh_extension import JSMol

## Functions needed
# Use the user options to extract the required data
def get_dataset(region, source, process, utility):
    # Extract the abbreviations from the .yml file
    global case_yml
    reg = case_yml["Region"][region]
    cas = case_yml["Source"][source]
    uti = case_yml["Utility"][utility]
    pro = case_yml["Process"][process]

    if utility == "w/ Heat Extraction":
        df_kpi_0 = pd.read_csv("data/" + cas + "_Storage_" + reg + "_" + pro + "-wet.csv")
    else:
        df_kpi_0 = pd.read_csv("data/" + cas + "_Storage_" + reg + "_" + uti + "_" + pro + "-wet.csv")

    df_kpi = df_kpi_0.drop(to_drop, axis=1)

    df_wrc0 = pd.read_csv("data/Water_" + cas + "-Simulated.csv")
    df_wrc = df_wrc0.iloc[:, [0, -1]]

    df_mat.sort_values(by=['MOF'], inplace=True)
    df_wrc.sort_values(by=['MOF'], inplace=True)
    df_kpi.sort_values(by=['MOF'], inplace=True)
    dataset0 = pd.merge(df_mat, df_wrc, on="MOF")
    dataset = pd.merge(dataset0, df_kpi, on="MOF")
    dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    if cas == "Cement":
        dataset["LCOE"]=[0]*dataset.shape[0]
        dataset.dropna(axis=0, inplace=True)
        dataset["spec_cool"]=list(np.array(dataset["spec_cool"])*-1)
    else:
        dataset.dropna(axis=0, inplace=True)
        dataset["spec_cool"]=list(np.array(dataset["spec_cool"])*-1)

    return dataset

# Use the user options to prepare the data for plotting
def prep_data_plot(data_source, wlabel, xlabel, ylabel, zlabel, df_keys, top):
    # Get the full list of KPIs and it's length 
    KPIs = [df_keys["KPI"][df_keys["Label"]==i].iloc[0] for i in wlabel + xlabel + ylabel + zlabel]
    order_KPIs = [df_keys["Order"][df_keys["KPI"]==i].iloc[0] for i in KPIs]
    len_KPIs = len(KPIs)
    
    # Clean and remove all negative data
    data_source_pos = data_source
    for i in KPIs:
        data_source_pos = data_source_pos[data_source_pos[i] > 0]

    # Update the material list
    MOFs = list(data_source_pos["MOF"])
    material_select.options = MOFs
    
    # Arrange in order based on each KPI
    Rank = []
    top_str = []
    for i in range(len_KPIs):
        Rank.append([])
        top_str.append([])
        data_sort = data_source_pos.sort_values(KPIs[i], ascending=order_KPIs[i])
        data_sort.reset_index(drop=True, inplace=True)
        
        for j in MOFs:
            Rank[i].append(data_sort.index[data_sort["MOF"]==j][0]+1)
            if data_sort.index[data_sort["MOF"]==j][0]+1 <= top:
                top_str[i].append(j)

    # Prepare the data for plotting
    x = []
    y = []
    for i in range(len(MOFs)):
        x.append([k+1 for k in range(len_KPIs)])
        y.append([])
        for j in range(len_KPIs):
            y[i].append(Rank[j][i])
    
    return {"MOF":MOFs, "X":x, "Y":y}, top_str 

# A standard script for bokeh plotting
def make_plot(data_source:pd.DataFrame, matKPIsLabels:list, procKPIsLabels:list, teKPIsLabels:list, lcaKPIsLabels:list, material:list, df_keys:pd.DataFrame, kpi:str, top:int = 10):
    # source of the data
    """Standard script for bokeh plotting
    
    Parameters: 
    -----------
    data_source: pd.DataFrame
        data to plot

    matKPIsLabels: list
        list of material KPIs to display

    procKPIsLabels: list
        list of process KPIs to display

    teKPIsLabels:list 
        list of techno-economic KPIs to display
    
    lcaKPIsLabels:list
        list of lca KPIs to display
    
    material: list
        selected materials to highlight in blue on the plot
    
    df_keys: pd.Dataframe
        dataframe containing all the KPIs (columns: KPI, Label, Unit, Order)
    
    kpi:str
        selected KPI of interest; top 10 will be indicated in red
    
    top: int, default: 10
        n top materials to display for a given KP of interest
    """
    source_data, structures = prep_data_plot(data_source, matKPIsLabels, procKPIsLabels, teKPIsLabels, lcaKPIsLabels, df_keys, top)

    source = ColumnDataSource(data=source_data)
    hover = HoverTool(tooltips= [("MOF", "@MOF")])

    label_tot = matKPIsLabels + procKPIsLabels + teKPIsLabels + lcaKPIsLabels
    label_full = [i + " (" + df_keys["Unit"][df_keys["Label"]==i].iloc[0] + ")" for i in label_tot]
    xticker = [i+1 for i in range(len(label_tot))]
    
    p = figure(height=HEIGHT, width=WIDTH, toolbar_location='above',
               tools=['pan', 'wheel_zoom', 'box_zoom', 'save', 'reset', hover], active_drag='box_zoom')

    # If a KPI of interest is chosen
    if kpi != "None":
        ind = label_tot.index(kpi)
        structures_top = structures[ind]
        for i in range(len(list(source.data["MOF"]))):
            if list(source.data["MOF"])[i] in structures_top:
                p.line(source.data["X"][i], source.data["Y"][i], name=list(source.data["MOF"])[i], color="red", line_width=2, alpha=1)

    # If a material of interest is chosen
    x_val = []
    y_val = []
    label_val = []
    for i in range(len(list(source.data["MOF"]))):
        if list(source.data["MOF"])[i] in material:
            p.line(source.data["X"][i], source.data["Y"][i], name=list(source.data["MOF"])[i], color="blue", line_width=2, alpha=1)
            x_val.append(1)
            y_val.append(source.data["Y"][i][0])
            label_val.append(list(source.data["MOF"])[i])



    p.ygrid.visible = False
    p.xaxis.ticker = xticker
    p.yaxis.ticker = [1, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    p.xaxis.major_label_overrides = {xticker[i]:label_full[i] for i in range(len(xticker))}
    p.xaxis.major_label_text_font_size = FONT_SIZE_AXIS
    p.yaxis.major_label_text_font_size = FONT_SIZE_AXIS
    p.xaxis.major_label_orientation = LABEL_OR
    p.multi_line("X", "Y", source=source, color = "gray", line_width=DATA_SIZE, alpha=0.05)
    p.y_range.flipped = True
    source_label = ColumnDataSource(data=dict(xval=x_val,yval=y_val,labelval=label_val))
    labels = LabelSet(x='xval', y= 'yval', x_offset=-20, text='labelval', source=source_label, text_font_size="7pt", text_color="black") #adding names of the selected MOFs
    p.add_layout(labels)

    help_button_width = 50
    total_lenght = WIDTH - (len(label_tot)*help_button_width)
    helps = []
    for i in label_tot:
        if i in ['Henry Selectivity', 'Purity', 'Productivity', 'nCAC', 'Climate Change', 'Material Resources: Metals/Minerals']:

            help_button = Button(label = 'video', width = help_button_width)
            youtube_video_url = HELPS[i]
            js_code = f"window.open('{youtube_video_url}', '_blank', 'popup=yes');"

            help_button.js_on_click(CustomJS(code=js_code))

            helps.append(help_button)
        else:
            helps.append(Spacer(width = help_button_width))
        helps.append(Spacer(width = int(total_lenght/int(len(label_tot)))))

    a = column(p, row(helps))
    return a

# Update the layout given the different options 
def update_source(attr, old, new):
    region = region_select.value
    source = source_select.value

    if region == "Switzerland" or region == "United Kingdom 2022":
        source_select.options = [sources[0], sources[2]]
        if source != "Cement":
            source_select.value = source_select.options[0]
    else:
        source_select.options = sources

def update_utility(attr, old, new):
    region = region_select.value
    source = source_select.value

    if region == "Switzerland":
        utility_select.visible = True
        if source == "Cement":
            utility_select.options = utilities[:2]
            utility_select.value = utility_select.options[0]
        elif source == "Natural Gas Power Plant":
            utility_select.options = utilities[:4]
            utility_select.value = utility_select.options[0]

    elif region == "United Kingdom":
        if source != "Cement":
            utility_select.visible = True
            utility_select.options = utilities[4:6]
            utility_select.value = utility_select.options[0]
        else:
            utility_select.visible = False
            utility_select.value = "w/ Heat Extraction"

    else:
        utility_select.visible = False
        utility_select.value = "w/ Heat Extraction"

# Update the plot given the different options
def update_plot(attrname, old, new):
    print("\nUPDATING PLOT")

    regionval = region_select.value
    sourceval = source_select.value
    utilityval = utility_select.value
    processval = process_select.value

    mat_kpis_val = mat_kpis.value
    proc_kpis_val = proc_kpis.value
    te_kpis_val = te_kpis.value
    lca_kpis_val = lca_kpis.value

    materialval = material_select.value

    kpi_select.options = ["None"] + mat_kpis_val + proc_kpis_val + te_kpis_val + lca_kpis_val
    kpival = kpi_select.value

    src = get_dataset(regionval, sourceval, processval, utilityval)
    plot_data.update(src)
    layout.children[0].children[2] = make_plot(plot_data, mat_kpis_val, proc_kpis_val, te_kpis_val, lca_kpis_val, materialval, df_keys, kpival, TOP)

    if attrname != 'fromStructures':
        tabs = Update_structureTabs(CURRENT_STRUCTURES)
        layout.children[0].children[3].children[3].tabs = tabs
    
def get_cif_content_from_disk(filename):
    """ Load CIF content from disk """
    with open(filename, 'r') as f:
        content = f.read()
    return content

def get_applet(cifcontent):
    '''Get JSmol applet from cifcontent'''
    script_source_new = ColumnDataSource()
    info_new = dict(
        height='100%',
        width='100%',
        serverURL='https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php',
        use='HTML5',
        j2sPath='https://chemapps.stolaf.edu/jmol/jsmol/j2s',
        script=JSMOL_SCRIPT.format(cifcontent)
    )
    return JSMol(
        width=300,
        height=300,
        script_source=script_source_new,
        info=info_new,
        #js_url='detail/static/jsmol/JSmol.min.js',
    )

def on_structure_change(attr, old, new):
    if len(new) == 0:
        layout.children[0].children[3].children[3].visible = False
    else:
        layout.children[0].children[3].children[3].visible = True

    global CURRENT_STRUCTURES
    CURRENT_STRUCTURES = new[::-1]
    print(f"The list is changed from {old} to {new}")
    tabs = Update_structureTabs(CURRENT_STRUCTURES)
    layout.children[0].children[3].children[3].tabs = tabs
    update_plot('fromStructures', None, None)

def create_LinkedButton(url:str, width = 25, height = 30):
    button = Button(label = 'video', width = width, height = height)
    js_code = f"window.open('{url}', '_blank', 'popup=yes', 'width=100,height=400');"

    button.js_on_click(CustomJS(code=js_code))
    return button

def create_tabPanel(structureName:str):
    cifname= structureName
    ciffile = f'{cifname}.cif'
    ciffile =  os.path.join('./data/CIFs', ciffile)
    if os.path.exists(ciffile):
        print(f'\t{ciffile} found!')
    else:
        return
    cifcontent_new = get_cif_content_from_disk(ciffile)

    applet_new = get_applet(cifcontent_new)
    nameDisplay = Div(text= f'<p><a href=Structure?name={cifname} target="_blank">{cifname}</a></p>',
                        align = 'center',
                        )
    tab_col = column(nameDisplay, applet_new)
    panel = Panel(child = tab_col, title = structureName)
    return panel

def Update_structureTabs(structures_names:list, focusTab = None):
    '''
    create a list of tabs to display

    Parameters:
    -----------
    structures_names: list of strings
            list of structure names
    '''
    global layout
    tabs = []
    for i, structure in enumerate(structures_names):
        if i == 0:
            print(f'Creating Display pannel for {i, structure}')
            panel = create_tabPanel(structure)
        else:
            print(f'Creating Dummy pannel for {i, structure}')
            panel = Panel(child = Spacer(height= 2), title = structure)

        tabs.append(panel)
    return tabs

def on_tab_change(attr, old, new):
    print(f'Tab changed from {old} to {new}')
    if new == 0:
        print('New value is 0 so no action needed.')
        return
    global CURRENT_STRUCTURES
    print(CURRENT_STRUCTURES)

    new_strucutre = CURRENT_STRUCTURES.pop(new)
    print(f'New structure display: {new_strucutre}')
    CURRENT_STRUCTURES.insert(0, new_strucutre)

    print(f'New order of Structures: {CURRENT_STRUCTURES}')
    
    tabs = Update_structureTabs(CURRENT_STRUCTURES)
    layout.children[0].children[3].children[3].tabs = tabs

    layout.children[0].children[3].children[3].active = 0

    
    
### Lay out ###
## Initialize the dictionaries
labels = {label_keys[i]:list_keys[i] for i in range(len(list_keys))}
materials = list(get_dataset(DEFAULTS[0], DEFAULTS[1], DEFAULTS[2], DEFAULTS[9])["MOF"])

## Initialize the select column
region_select = Select(title='Region', options=regions, value=DEFAULTS[0], width=WWIDTH)
source_select = Select(title='Source', options=sources, value=DEFAULTS[1], width=WWIDTH)
utility_select = Select(title='Utility', visible=False, value=DEFAULTS[9], width=WWIDTH)
process_select = Select(title='Process Type', options=processes, value=DEFAULTS[2], width=WWIDTH)
mat_kpis = MultiChoice(title="Material KPIs", options=list(labels.keys())[:KPI_count[0]], value=DEFAULTS[3], width=WWIDTH)
proc_kpis = MultiChoice(title="Process KPIs", options=list(labels.keys())[KPI_count[0]:KPI_count[1]], value=DEFAULTS[4], width=WWIDTH)
te_kpis = MultiChoice(title="Techno-Economic KPIs", options=list(labels.keys())[KPI_count[1]:KPI_count[2]], value=DEFAULTS[5], width=WWIDTH)
lca_kpis = MultiChoice(title="Life Cycle Assessment KPIs", options=list(labels.keys())[KPI_count[2]:], value=DEFAULTS[6], width=WWIDTH)
material_select = MultiChoice(title='Structure(s) of Interest', options=materials, value=DEFAULTS[7], width=WWIDTH)
kpi_select = Select(title='KPI of Interest', options=kpis, value=DEFAULTS[8], width=WWIDTH)

## Get the initial plot data
plot_data = get_dataset(DEFAULTS[0], DEFAULTS[1], DEFAULTS[2], DEFAULTS[9])

controls = column(region_select, source_select, utility_select, process_select, mat_kpis, proc_kpis, te_kpis,
                  lca_kpis)

## Dynamic changes to the layout
region_select.on_change('value', update_source)
for widget in [region_select, source_select]:
    widget.on_change('value', update_utility)

applet = Spacer(height = 5)

tab = Panel(child = Spacer(height= 2), title = 'nan')
tabs_structure = widgets.Tabs(tabs=[tab], visible = False)
tabs_structure.on_change('active', on_tab_change)

help_case = create_LinkedButton(HELPS_EXTRA['CaseStudies'])
help_process = create_LinkedButton(HELPS_EXTRA['TVSA'])
help_KPI_mat= create_LinkedButton(HELPS_EXTRA['KPIs_material'])
help_KPI_pro= create_LinkedButton(HELPS_EXTRA['KPIs_process'])
help_KPI_TEA= create_LinkedButton(HELPS_EXTRA['KPIs_TEA'])
help_KPI_LCA= create_LinkedButton(HELPS_EXTRA['KPIs_LCA'])

helps = column(help_case, Spacer(height = 80), 
               help_process, Spacer(height = 20, width = 70), 
               help_KPI_mat, Spacer(height = 60), 
               help_KPI_pro, Spacer(height = 55), 
               help_KPI_TEA, Spacer(height = 40), 
               help_KPI_LCA)

for w in [region_select, source_select, utility_select, process_select, mat_kpis, proc_kpis, te_kpis,
          lca_kpis, kpi_select]:
    w.on_change('value', update_plot)
    pass

material_select.on_change('value', on_structure_change)

## Generate the page

layout = column(row(helps, 
                    controls, 
                    column(make_plot(plot_data, DEFAULTS[3], DEFAULTS[4], DEFAULTS[5], DEFAULTS[6], DEFAULTS[7],
                                               df_keys, DEFAULTS[8], TOP)
                            ), 
                    column(material_select, 
                           kpi_select, 
                           Spacer(height = 100), 
                           tabs_structure
                            )
                    )
                )

curdoc().add_root(layout)
curdoc().title = "KPI-Line"