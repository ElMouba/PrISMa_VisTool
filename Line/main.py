''' Case Study Line Plots '''

import bokeh.models as bmd
import pandas as pd
import yaml

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import LabelSet, ColumnDataSource, MultiChoice, Select, CustomJS
from bokeh.plotting import figure
from config_lin import *
from os.path import dirname, join

## Input
df_keys = pd.DataFrame({"KPI": list_keys, "Label": label_keys, "Unit": unit_keys, "Order": order_keys})

## Functions needed
# Use the user options to extract the required data
def get_dataset(region, source, process):
    # Read the .yml file
    with open('Line/data/data-read.yml') as f:
        data_yaml = yaml.load(f, Loader=yaml.SafeLoader)

    # Extract the abbreviations from the .yml file
    reg = data_yaml["Region"][region]
    cas = data_yaml["Source"][source]
    pro = data_yaml["Process"][process]

    if source == "Natural Gas Power Plant":
        df_mat = pd.read_csv("Line/data/Material-Low.csv")
    else:
        df_mat = pd.read_csv("Line/data/Material-High.csv")
    
    df_kpi = pd.read_csv("Line/data/" + reg + "-" + cas + "-" + pro + ".csv")
    df_kpi1 = df_kpi.drop(['Unnamed: 0', 'product_out', 'n_out_vac', 'time_steps', 'vac_decay', 'spec_heat_tot', 'spec_cool_tot',
                           'spec_power_tot', 'productivity_tea', 'var_OPEX', 'CAC_approx_neg', 'SPECCA_approx_neg', "CCC"], axis=1)

    df_mat.sort_values(by=['MOF'], inplace=True)
    df_kpi1.sort_values(by=['MOF'], inplace=True)
    dataset = pd.merge(df_mat, df_kpi1, on="MOF")

    return dataset

# Use the user options to prepare the data for plotting
def prep_data_plot(data_source, wlabel, xlabel, ylabel, zlabel, df_keys, top):
    # Get the full list of KPIs and it's length
    all_kpis = wlabel + xlabel + ylabel + zlabel
    KPIs = [df_keys["KPI"][df_keys["Label"]==i].iloc[0] for i in all_kpis]
    order_KPIs = [df_keys["Order"][df_keys["KPI"]==i].iloc[0] for i in KPIs]
    len_KPIs = len(KPIs)
    
    # Clean and remove all negative data
    data_source_pos = data_source
    for i in KPIs:
        data_source_pos = data_source_pos[data_source_pos[i] > 0]

    material_select.options = list(data_source_pos["MOF"])
    # Get the MOF labels
    MOFs = list(data_source_pos["MOF"])

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

    if kpi != "None":
        ind = label_tot.index(kpi)
        structures_top = structures[ind]
        for i in range(len(list(source.data["MOF"]))):
            if list(source.data["MOF"])[i] in structures_top:
                p.line(source.data["X"][i], source.data["Y"][i], name=list(source.data["MOF"])[i], color="red", line_width=2, alpha=1)

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

    return p

# Update the layout given the different options 
def update_layout(attr, old, new):
    region = region_select.value
    if region == "Switzerland":
        source_select.options = [list(sources.keys())[0], list(sources.keys())[2]]
    else:
        source_select.options = list(sources.keys())

# Update the plot given the different options
def update_plot(attrname, old, new):
    region = region_select.value
    source = source_select.value
    process = process_select.value
    wlabelval = wlabel_select.value
    xlabelval = xlabel_select.value
    ylabelval = ylabel_select.value
    zlabelval = zlabel_select.value
    materialval = material_select.value

    regionval = regions[region]
    sourceval = sources[source]
    processval = processes[process]
    kpi_select.options = ["None"] + wlabelval + xlabelval + ylabelval + zlabelval
    kpival = kpi_select.value
    src = get_dataset(regionval, sourceval, processval)
    plot_data.update(src)

    layout.children[0].children[1] = make_plot(plot_data, wlabelval, xlabelval, ylabelval, zlabelval, materialval, df_keys, kpival, 10) 

## Initialize the dictionaries
regions = {i:i for i in list_regions}
sources = {i:i for i in list_sources}
processes = {i:i for i in list_processes}
wlabels = {label_keys[i]:list_keys[i] for i in range(12)}
xlabels = {label_keys[i]:list_keys[i] for i in range(12,21)}
ylabels = {label_keys[i]:list_keys[i] for i in range(21,30)}
zlabels = {label_keys[i]:list_keys[i] for i in range(30, len(label_keys))}

region0 = 'United Kingdoms'
source0 = 'Cement'
process0 = 'Temperature Swing Adsorption'
wlabel0 = ['IAST Selectivity']
xlabel0 = ['Purity', 'Productivity']
ylabel0 = ['CAC']
zlabel0 = ['Climate Change', 'Material Resources: Metals/Minerals']
materials = {i:i for i in list(get_dataset(region0, source0, process0)["MOF"])}
material0 = []
kpis = ["None"] + wlabel0 + xlabel0 + ylabel0 + zlabel0
kpi0 = "None"

## Initialize the select column
region_select = Select(title='Region', options=list(regions.keys()), value=region0, width=WWIDTH)
source_select = Select(title='Source', options=list(sources.keys()), value=source0, width=WWIDTH)
process_select = Select(title='Process Type', options=list(processes.keys()), value=process0, width=WWIDTH)
wlabel_select = MultiChoice(title="Material KPIs", options=list(wlabels.keys()), value=wlabel0, width=WWIDTH)
xlabel_select = MultiChoice(title="Process KPIs", options=list(xlabels.keys()), value=xlabel0, width=WWIDTH)
ylabel_select = MultiChoice(title="Techno-Economic KPIs", options=list(ylabels.keys()), value=ylabel0, width=WWIDTH)
zlabel_select = MultiChoice(title="Life Cycle Assessment KPIs", options=list(zlabels.keys()), value=zlabel0, width=WWIDTH)
material_select = MultiChoice(title='Structure(s) of Interest', options=list(materials.keys()), value=material0, width=WWIDTH)
kpi_select = Select(title='KPI of Interest', options=kpis, value=kpi0, width=WWIDTH)

## Get the initial plot data
plot_data = get_dataset(regions[region0], sources[source0], processes[process0])

for w in [region_select,source_select,process_select,wlabel_select,xlabel_select,ylabel_select,zlabel_select,material_select,kpi_select]:
    w.on_change('value', update_plot)

controls = column(region_select,source_select,process_select,wlabel_select,xlabel_select,ylabel_select,zlabel_select)

## Dynamic changes to the layout
region_select.on_change('value', update_layout)
source_select.on_change('value', update_layout)
process_select.on_change('value', update_layout)
wlabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
xlabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
ylabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
zlabel_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))
material_select.js_on_change('value', CustomJS(code="""console.log('multi_choice: value=' + this.value, this.toString())"""))

## Generate the page
layout = column(row(controls, column(make_plot(plot_data, wlabel0, xlabel0, ylabel0, zlabel0, material0, df_keys, kpi0, 10)), column(material_select,kpi_select)))
curdoc().add_root(layout)
curdoc().title = "KPI-Line"