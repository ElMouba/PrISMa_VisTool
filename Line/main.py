''' Case Study Line Plots '''

import bokeh.models as bmd
import numpy as np
import pandas as pd
import yaml
import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import LabelSet, ColumnDataSource, MultiChoice, Select, CustomJS, Spacer, Div, Button
from bokeh.plotting import figure
from config_lin import *
from os.path import dirname, join

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

    # Electric energy is only valid when vacuum is added
    # LCOE is only valid in case of power plants
    if pro == "Temperature Swing Adsorption":
        drops = to_drop + ["el_energy"]
    elif cas == "Cement":
        drops = to_drop + ["LCOE"]
    elif pro == "Temperature Swing Adsorption" and cas == "Cement":
        drops = to_drop + ["el_energy", "LCOE"]
    else:
        drops = to_drop
    df_kpi = df_kpi_0.drop(to_drop, axis=1)

    df_wrc0 = pd.read_csv("data/Water_" + cas + "-Simulated.csv")
    df_wrc = df_wrc0.iloc[:, [0, -1]]

    df_mat.sort_values(by=['MOF'], inplace=True)
    df_wrc.sort_values(by=['MOF'], inplace=True)
    df_kpi.sort_values(by=['MOF'], inplace=True)
    dataset0 = pd.merge(df_mat, df_wrc, on="MOF")
    dataset = pd.merge(dataset0, df_kpi, on="MOF")
    dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
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
def make_plot(data_source, wlabel, xlabel, ylabel, zlabel, material, df_keys, kpi, top):
    # source of the data
    source_data = prep_data_plot(data_source, wlabel, xlabel, ylabel, zlabel, df_keys, top)[0]
    structures = prep_data_plot(data_source, wlabel, xlabel, ylabel, zlabel, df_keys, top)[1]

    source = bmd.ColumnDataSource(data=source_data)
    hover = bmd.HoverTool(tooltips= [("MOF", "@MOF")])

    label_tot = wlabel + xlabel + ylabel + zlabel
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
    labels = LabelSet(x='xval', y= 'yval', x_offset=-20, text='labelval', source=source_label, text_font_size="7pt", text_color="black")
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
    print(attrname, old, new)
    regionval = region_select.value
    sourceval = source_select.value
    utilityval = utility_select.value
    processval = process_select.value
    wlabelval = wlabel_select.value
    xlabelval = xlabel_select.value
    ylabelval = ylabel_select.value
    zlabelval = zlabel_select.value
    materialval = material_select.value

    kpi_select.options = ["None"] + wlabelval + xlabelval + ylabelval + zlabelval
    kpival = kpi_select.value
    
    src = get_dataset(regionval, sourceval, processval, utilityval)
    plot_data.update(src)
    layout.children[0].children[2] = make_plot(plot_data, wlabelval, xlabelval, ylabelval, zlabelval, materialval, df_keys, kpival, TOP)

def get_cif_content_from_disk(filename):
    """ Load CIF content from disk """
    with open(filename, 'r') as f:
        content = f.read()
    return content


## Initialize the dictionaries
labels = {label_keys[i]:list_keys[i] for i in range(len(list_keys))}
materials = list(get_dataset(defaults[0], defaults[1], defaults[2], defaults[9])["MOF"])

## Initialize the select column
region_select = Select(title='Region', options=regions, value=defaults[0], width=WWIDTH)
source_select = Select(title='Source', options=sources, value=defaults[1], width=WWIDTH)
utility_select = Select(title='Utility', visible=False, value=defaults[9], width=WWIDTH)
process_select = Select(title='Process Type', options=processes, value=defaults[2], width=WWIDTH)
wlabel_select = MultiChoice(title="Material KPIs", options=list(labels.keys())[:KPI_count[0]], value=defaults[3], width=WWIDTH)
xlabel_select = MultiChoice(title="Process KPIs", options=list(labels.keys())[KPI_count[0]:KPI_count[1]], value=defaults[4], width=WWIDTH)
ylabel_select = MultiChoice(title="Techno-Economic KPIs", options=list(labels.keys())[KPI_count[1]:KPI_count[2]], value=defaults[5], width=WWIDTH)
zlabel_select = MultiChoice(title="Life Cycle Assessment KPIs", options=list(labels.keys())[KPI_count[2]:], value=defaults[6], width=WWIDTH)
material_select = MultiChoice(title='Structure(s) of Interest', options=materials, value=defaults[7], width=WWIDTH)
kpi_select = Select(title='KPI of Interest', options=kpis, value=defaults[8], width=WWIDTH)

## Get the initial plot data
plot_data = get_dataset(defaults[0], defaults[1], defaults[2], defaults[9])

controls = column(region_select, source_select, utility_select, process_select, wlabel_select, xlabel_select, ylabel_select,
                  zlabel_select)

## Dynamic changes to the layout
region_select.on_change('value', update_source)
for widget in [region_select, source_select]:
    widget.on_change('value', update_utility)
wlabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
xlabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
ylabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
zlabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
material_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))

# Chnages to plot
for w in [region_select, source_select, utility_select, process_select, wlabel_select, xlabel_select, ylabel_select,
          zlabel_select, material_select, kpi_select]:
    w.on_change('value', update_plot)

#### JSMOL ###
def run_script(attr, old, new):
    if not new:
        print(new)
        layout.children[0].children[3].children[4]= Spacer(height = 5)
        nameDisplay.text = ''
        return
    print(f'Changing jmol to {new}')
    cifname= new[-1]
    ciffile = f'{cifname}.cif'
    ciffile =  os.path.join('./data/CIFs', ciffile)
    if os.path.exists(ciffile):
        print(f'{ciffile} found!')

    cifcontent_new = get_cif_content_from_disk(ciffile)
    """Run JSMol script specified by user."""
    script_source_new = ColumnDataSource()

    info_new = dict(
        height='100%',
        width='100%',
        serverURL='https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php',
        use='HTML5',
        j2sPath='https://chemapps.stolaf.edu/jmol/jsmol/j2s',
        script="""
set antialiasDisplay ON; background white; set displayCellParameters FALSE; set disablePopupMenu FALSE;
load data "cifstring"
{}
end "cifstring"
    """.format(cifcontent_new)
    )
    applet_new = JSMol(
        width=400,
        height=400,
        script_source=script_source_new,
        info=info_new,
    )

    nameDisplay.text = f'<h2><a href=Structure?name={cifname} target="_blank">{cifname}</a></h2>'

    layout.children[0].children[3].children[4]= applet_new
    print(applet.__dict__)



applet = Spacer(height = 5)
nameDisplay = Div(text= '', align = 'center')

material_select.on_change('value', run_script)

def create_LinkedButton(url:str, width = 25, height = 30):
    button = Button(label = 'video', width = width, height = height)
    js_code = f"window.open('{url}', '_blank', 'popup=yes', 'width=100,height=400');"

    button.js_on_click(CustomJS(code=js_code))
    return button

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
## Generate the page
layout = column(row(helps, controls, 
                    column(make_plot(plot_data, defaults[3], defaults[4], defaults[5], defaults[6], defaults[7],
                                               df_keys, defaults[8], TOP)), 
                    column(material_select, kpi_select, Spacer(height = 250), nameDisplay, applet)))

curdoc().add_root(layout)
curdoc().title = "KPI-Line"