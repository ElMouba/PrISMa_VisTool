''' Case Study 3D Plots '''

import bokeh.models as bmd
import numpy as np
import pandas as pd
import yaml

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Title, OpenURL, TapTool, Select, TextInput
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from config_fig import *
from os.path import dirname, join

## Input
# x, y and z keys
df_keys = pd.DataFrame({"KPI": list_keys, "Label": label_keys, "Unit": unit_keys})

## Functions needed
# Use the user options to extract the required data
def get_dataset(region, source, process):
    # Read the .yml file
    with open('Figure/data/data-read.yml') as f:
        data_yaml = yaml.load(f, Loader=yaml.SafeLoader)

    # Extract the abbreviations from the .yml file
    reg = data_yaml["Region"][region]
    cas = data_yaml["Source"][source]
    pro = data_yaml["Process"][process]

    if source == "Natural Gas Power Plant":
        df_mat = pd.read_csv("Figure/data/Material-Low.csv")
    else:
        df_mat = pd.read_csv("Figure/data/Material-High.csv")
    
    df_kpi = pd.read_csv("Figure/data/" + reg + "-" + cas + "-" + pro + ".csv")
    df_kpi1 = df_kpi.drop(['Unnamed: 0', 'product_out', 'n_out_vac', 'time_steps', 'vac_decay', 'spec_heat_tot', 'spec_cool_tot',
                           'spec_power_tot', 'productivity_tea', 'var_OPEX', 'CAC_approx_neg', 'SPECCA_approx_neg', "CCC"], axis=1)

    df_mat.sort_values(by=['MOF'], inplace=True)
    df_kpi1.sort_values(by=['MOF'], inplace=True)
    dataset = pd.merge(df_mat, df_kpi1, on="MOF")

    return dataset

# A standard script for bokeh plotting
def make_plot(dataset, xlabel, ylabel, zlabel, df_keys, xlog, ylog, zlog, material, xref, yref):
    dataset_pos = dataset[(dataset[xlabel] > 0) & (dataset[ylabel] > 0) & (dataset[zlabel] > 0)]
    material_select.options = ["None"] + list(dataset_pos["MOF"])
    
    if zlog == "log":
        dataset_pos[zlabel] = np.log(dataset_pos[zlabel])
    color_by = zlabel

    source = bmd.ColumnDataSource(data=dataset_pos)

    hover = bmd.HoverTool(tooltips= [("MOF", "@MOF")])

    p = figure(height=HEIGHT, width=WIDTH, toolbar_location='above', x_axis_type=xlog, y_axis_type=ylog,
               tools=['pan', 'wheel_zoom', 'box_zoom', 'save', 'reset', 'tap', hover], active_drag='box_zoom')

    xax = df_keys["Label"][df_keys["KPI"]==xlabel].iloc[0] + " (" + df_keys["Unit"][df_keys["KPI"]==xlabel].iloc[0] + ")"
    yax = df_keys["Label"][df_keys["KPI"]==ylabel].iloc[0] + " (" + df_keys["Unit"][df_keys["KPI"]==ylabel].iloc[0] + ")"
    zax = df_keys["Label"][df_keys["KPI"]==zlabel].iloc[0] + " (" + df_keys["Unit"][df_keys["KPI"]==zlabel].iloc[0] + ")"
    p.xaxis.axis_label = xax
    p.yaxis.axis_label = yax
    p.xaxis.axis_label_text_font_size = FONT_SIZE_LABEL
    p.yaxis.axis_label_text_font_size = FONT_SIZE_LABEL
    p.xaxis.major_label_text_font_size = FONT_SIZE_AXIS
    p.yaxis.major_label_text_font_size = FONT_SIZE_AXIS

    colors = np.array(source.data[color_by])
    cmap = bmd.LinearColorMapper(palette=Turbo256, low=min(colors), high=max(colors))

    if material == "None":
        p.circle(xlabel, ylabel, size=DATA_SIZE, source=source, fill_color={'field': color_by, 'transform': cmap}, alpha=0.5)
    else:
        dataset2 = dataset_pos[dataset_pos["MOF"]==material]
        source2 = bmd.ColumnDataSource(data=dataset2)
        p.circle(xlabel, ylabel, size=DATA_SIZE, source=source, fill_color={'field': color_by, 'transform': cmap}, alpha=0.1)
        p.diamond(xlabel, ylabel, size=DATA_SIZE, source=source2, alpha=1.0, line_color="black", fill_color="red")

    if xref:
        p.line([xref, xref], [min(dataset_pos[ylabel]), max(dataset_pos[ylabel])], dash="dashed", color="black", line_width=2.0, alpha=1.0)

    if yref:
        p.line([min(dataset_pos[xlabel]), max(dataset_pos[xlabel])], [yref, yref], dash="dashed", color="black", line_width=2.0, alpha=1.0)

    cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0), major_label_text_font_size="10pt")
    p.add_layout(cbar, 'right')
    p.add_layout(Title(text=zax, align="center", text_font_size="13pt", text_font_style="normal"), "right")
    
    url = "http://localhost:5006/Table?name=@MOF"
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url=url)
    
    return p

# Update the layout given the different options 
def update_layout(attr, old, new):
    region = region_select.value
    if region == "Switzerland":
        source_select.options = [list(sources.keys())[0], list(sources.keys())[2]]
    else:
        source_select.options = list(sources.keys())

    xlayer = xlayer_select.value
    if xlayer == "Material":
        xlabel_select.options = list(xlabels.keys())[:12]
    elif xlayer == "Process":
        xlabel_select.options = list(xlabels.keys())[12:21]
    elif xlayer == "Techno-Economics":
        xlabel_select.options = list(xlabels.keys())[21:30]
    elif xlayer == "Life Cycle Assessment":
        xlabel_select.options = list(xlabels.keys())[30:]

    ylayer = ylayer_select.value
    if ylayer == "Material":
        ylabel_select.options = list(ylabels.keys())[:12]
    elif ylayer == "Process":
        ylabel_select.options = list(ylabels.keys())[12:21]
    elif ylayer == "Techno-Economics":
        ylabel_select.options = list(ylabels.keys())[21:30]
    elif ylayer == "Life Cycle Assessment":
        ylabel_select.options = list(ylabels.keys())[30:]

    zlayer = zlayer_select.value
    if zlayer == "Material":
        zlabel_select.options = list(zlabels.keys())[:12]
    elif zlayer == "Process":
        zlabel_select.options = list(zlabels.keys())[12:21]
    elif zlayer == "Techno-Economics":
        zlabel_select.options = list(zlabels.keys())[21:30]
    elif zlayer == "Life Cycle Assessment":
        zlabel_select.options = list(zlabels.keys())[30:]

# Update the plot given the different options
def update_plot(attrname, old, new):
    region = region_select.value
    source = source_select.value
    process = process_select.value
    xlabel = xlabel_select.value
    ylabel = ylabel_select.value
    zlabel = zlabel_select.value
    xlog = xlog_select.value
    ylog = ylog_select.value
    zlog = zlog_select.value
    material = material_select.value
    xrefval = xref_input.value
    yrefval = yref_input.value

    regionval = regions[region]
    sourceval = sources[source]
    processval = processes[process]
    xlabelval = xlabels[xlabel]
    ylabelval = ylabels[ylabel]
    zlabelval = zlabels[zlabel]
    
    src = get_dataset(regionval, sourceval, processval)
    plot_data.update(src)
    
    layout.children[0].children[1] = make_plot(plot_data, xlabelval, ylabelval, zlabelval, df_keys, xlog, ylog, zlog, material, xrefval, yrefval)
    
## Initialize the dictionaries
regions = {i:i for i in list_regions}
sources = {i:i for i in list_sources}
processes = { i:i for i in list_processes} 
xlayers = {i:i for i in list_layers}
ylayers = {i:i for i in list_layers}
zlayers = {i:i for i in list_layers}
xlabels = {label_keys[i]:list_keys[i] for i in range(len(list_keys))}
ylabels = {label_keys[i]:list_keys[i] for i in range(len(list_keys))}
zlabels = {label_keys[i]:list_keys[i] for i in range(len(list_keys))}

region0 = 'United Kingdoms'
source0 = 'Cement'
process0 = 'Temperature Swing Adsorption'
xlayer0 = 'Process'
ylayer0 = 'Techno-Economics'
zlayer0 = 'Process'
xlabel0 = 'Recovery'
ylabel0 = 'CAC'
zlabel0 = 'Specific Heat'
xlog0 = 'linear'
ylog0 = 'log'
zlog0 = 'linear'
materials = {i:i for i in list(get_dataset(regions[region0], sources[source0], processes[process0])["MOF"])}
material0 = "None"

## Initialize the select column
region_select = Select(title='Region', options=list(regions.keys()), value=region0, width=WWIDTH)
source_select = Select(title='Source', options=list(sources.keys()), value=source0, width=WWIDTH)
process_select = Select(title='Process Type', options=list(processes.keys()), value=process0, width=WWIDTH)
xlayer_select = Select(title='Platform Layer (x-axis)', options=list(xlayers.keys()), value=xlayer0, width=WWIDTH)
xlabel_select = Select(title="Label (x-axis)", options=list(xlabels.keys())[12:21], value=xlabel0, width=WWIDTH)
ylayer_select = Select(title='Platform Layer (y-axis)', options=list(ylayers.keys()), value=ylayer0, width=WWIDTH)
ylabel_select = Select(title="Label (y-axis)", options=list(ylabels.keys())[21:30], value=ylabel0, width=WWIDTH)
zlayer_select = Select(title='Platform Layer (z-axis)', options=list(zlayers.keys()), value=zlayer0, width=WWIDTH)
zlabel_select = Select(title="Label (z-axis)", options=list(zlabels.keys())[12:21], value=zlabel0, width=WWIDTH)
xlog_select = Select(title="Scale (x-axis)", options=["linear", "log"], value=xlog0, width=WWIDTH)
ylog_select = Select(title="Scale (y-axis)", options=["linear", "log"], value=ylog0, width=WWIDTH)
zlog_select = Select(title="Scale (z-axis)", options=["linear", "log"], value=zlog0, width=WWIDTH)
material_select = Select(title="Material of Interest", options=["None"] + list(materials.keys()), value=material0, width=WWIDTH)
xref_input = TextInput(value="", title="Reference (x-axis)", width=WWIDTH)
yref_input = TextInput(value="", title="Reference (y-axis)", width=WWIDTH)

## Get the initial plot data
plot_data = get_dataset(regions[region0], sources[source0], processes[process0])

#selection to csv Button
for w in [region_select,source_select,process_select,xlayer_select,xlabel_select,ylayer_select,ylabel_select,zlayer_select,zlabel_select,xlog_select,ylog_select,zlog_select,material_select,xref_input,yref_input]:
    w.on_change('value', update_plot)

controls1 = column(region_select,source_select,process_select,xlayer_select,xlabel_select,ylayer_select,ylabel_select,zlayer_select,zlabel_select)
controls2 = column(xlog_select,ylog_select,zlog_select,material_select,xref_input,yref_input)

## Dynamic changes to the layout
region_select.on_change('value', update_layout)
source_select.on_change('value', update_layout)
xlayer_select.on_change('value', update_layout)
xlabel_select.on_change('value', update_layout)
ylayer_select.on_change('value', update_layout)
ylabel_select.on_change('value', update_layout)
zlayer_select.on_change('value', update_layout)
zlabel_select.on_change('value', update_layout)

## Generate the page
layout = column(row(controls1, make_plot(plot_data, xlabels[xlabel0], ylabels[ylabel0], zlabels[zlabel0], df_keys, xlog0, ylog0, zlog0, material0, "", ""), controls2))
curdoc().add_root(layout)
curdoc().title = "KPI-3D"