''' Case Study 3D Plots '''

import pandas as pd
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Title, OpenURL, TapTool, Select, TextInput, Paragraph, ColumnDataSource, HoverTool, LinearColorMapper, ColorBar
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from config_fig import *

## Functions needed
# Use the user options to extract the required data
def get_dataset(region, source, process, utility):
    # Extract the abbreviations from the .yml file
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

# A standard script for bokeh plotting
def make_plot(dataset, xlabel, ylabel, zlabel, df_keys, xlog, ylog, zlog, material, xref, yref):
    # This is to avoid negative data in the case of nCAC and some other TEA KPIs 
    dataset_pos = dataset[(dataset[xlabel] >= 0) & (dataset[ylabel] >= 0) & (dataset[zlabel] >= 0)]
    material_select.options = ["None"] + list(dataset_pos["MOF"])
    
    # use the log for the color coding
    if zlog == "log" and zlabel != "el_energy":
        dataset_pos[zlabel] = np.log(dataset_pos[zlabel])

    color_by = zlabel
    source = ColumnDataSource(data=dataset_pos)
    hover = HoverTool(tooltips= [("MOF", "@MOF")])

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
    cmap = LinearColorMapper(palette=Turbo256, low=min(colors), high=max(colors))

    # Update the plot when you have a structure of interest
    if material == "None":
        p.circle(xlabel, ylabel, size=DATA_SIZE, source=source, fill_color={'field': color_by, 'transform': cmap}, alpha=0.5)
    else:
        dataset_pos_1 = dataset_pos[dataset_pos["MOF"]==material]
        source2 = ColumnDataSource(data=dataset_pos_1)
        p.circle(xlabel, ylabel, size=DATA_SIZE, source=source, fill_color={'field': color_by, 'transform': cmap}, alpha=0.1)
        p.diamond(xlabel, ylabel, size=DATA_SIZE, source=source2, alpha=1.0, line_color="black", fill_color="red")

    # Update the plot of you have any ref values for the x or y axis
    if xref:
        p.line([xref, xref], [min(dataset_pos[ylabel]), max(dataset_pos[ylabel])], dash="dashed", color="black", line_width=2.0, alpha=1.0)
    if yref:
        p.line([min(dataset_pos[xlabel]), max(dataset_pos[xlabel])], [yref, yref], dash="dashed", color="black", line_width=2.0, alpha=1.0)

    cbar = ColorBar(color_mapper=cmap, location=(0, 0), major_label_text_font_size="10pt")
    p.add_layout(cbar, 'right')
    p.add_layout(Title(text=zax, align="center", text_font_size="13pt", text_font_style="normal"), "right")
    
    # Link the data points to the table
    url = "https://prisma.materialscloud.io/Table?name=@MOF"
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url=url)
    
    return p

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

def update_xaxis(attr, old, new):
    update_axis(xlayer_select, xlabel_select)
    
def update_yaxis(attr, old, new):
    update_axis(ylayer_select, ylabel_select)

def update_zaxis(attr, old, new):
    update_axis(zlayer_select, zlabel_select)

def update_axis(layer_select, label_select):
    layer = layer_select.value

    if layer == "Material":
       label_select.options = list(labels.keys())[:KPI_count[0]]
    elif layer == "Process":
        label_select.options = list(labels.keys())[KPI_count[0]:KPI_count[1]]
    elif layer == "Techno-Economics":
        label_select.options = list(labels.keys())[KPI_count[1]:KPI_count[2]]
    elif layer == "Life Cycle Assessment":
        label_select.options = list(labels.keys())[KPI_count[2]:]
    label_select.value = label_select.options[0]

# Update the plot given the different options
def update_plot(attrname, old, new):
    regionval = region_select.value
    sourceval = source_select.value
    utilityval = utility_select.value
    processval = process_select.value

    xlabel = xlabel_select.value
    ylabel = ylabel_select.value
    zlabel = zlabel_select.value
    xlog = xlog_select.value
    ylog = ylog_select.value
    zlog = zlog_select.value
    material = material_select.value
    xrefval = xref_input.value
    yrefval = yref_input.value
    xlabelval = labels[xlabel]
    ylabelval = labels[ylabel]
    zlabelval = labels[zlabel]
    
    src = get_dataset(regionval, sourceval, processval, utilityval)
    plot_data.update(src)
    layout.children[0].children[1] = column(make_plot(plot_data, xlabelval, ylabelval, zlabelval, df_keys, xlog, ylog, zlog,
                                               material, xrefval, yrefval), note_LCA, note_TEA)
    
## Initialize the dictionaries
labels = {label_keys[i]:list_keys[i] for i in range(len(list_keys))}
materials = list(get_dataset(defaults[0], defaults[1], defaults[2], defaults[13])["MOF"])

## Initialize the widgets
region_select = Select(title='Region', options=regions, value=defaults[0], width=WWIDTH)
source_select = Select(title='Source', options=sources, value=defaults[1], width=WWIDTH)
utility_select = Select(title='Utility', visible=False, value=defaults[13], width=WWIDTH)
process_select = Select(title='Process Type', options=processes, value=defaults[2], width=WWIDTH)
xlayer_select = Select(title='Platform Layer (x-axis)', options=layers, value=defaults[3], width=WWIDTH)
ylayer_select = Select(title='Platform Layer (y-axis)', options=layers, value=defaults[4], width=WWIDTH)
zlayer_select = Select(title='Platform Layer (z-axis)', options=layers, value=defaults[5], width=WWIDTH)
xlabel_select = Select(title="Label (x-axis)", options=list(labels.keys())[KPI_count[0]:KPI_count[1]], value=defaults[6], width=WWIDTH)
ylabel_select = Select(title="Label (y-axis)", options=list(labels.keys())[KPI_count[1]:KPI_count[2]], value=defaults[7], width=WWIDTH)
zlabel_select = Select(title="Label (z-axis)", options=list(labels.keys())[KPI_count[0]:KPI_count[1]], value=defaults[8], width=WWIDTH)
xlog_select = Select(title="Scale (x-axis)", options=["linear", "log"], value=defaults[9], width=WWIDTH)
ylog_select = Select(title="Scale (y-axis)", options=["linear", "log"], value=defaults[10], width=WWIDTH)
zlog_select = Select(title="Scale (z-axis)", options=["linear", "log"], value=defaults[11], width=WWIDTH)
material_select = Select(title="Material of Interest", options=["None"] + materials, value=defaults[12], width=WWIDTH)
xref_input = TextInput(value="", title="Reference (x-axis)", width=WWIDTH)
yref_input = TextInput(value="", title="Reference (y-axis)", width=WWIDTH)
note_LCA = Paragraph(text="""* LCA KPIs are per 1 kg of CO\u2082 captured""", width=WWIDTH)
note_TEA = Paragraph(text="""** Specific CO\u2082 Emissions are described per unit product for industrial cases and per unit
electricity for power plants""", width=int(2.5*WWIDTH))

## Get the initial plot data
plot_data = get_dataset(defaults[0], defaults[1], defaults[2], defaults[13])

controls1 = column(region_select, source_select, utility_select, process_select, xlayer_select, xlabel_select, ylayer_select,
                   ylabel_select, zlayer_select, zlabel_select)
controls2 = column(xlog_select, ylog_select, zlog_select, material_select, xref_input, yref_input)

## Dynamic changes to the layout
region_select.on_change('value', update_source)
for widget in [region_select, source_select]:
    widget.on_change('value', update_utility)
xlayer_select.on_change('value', update_xaxis)
ylayer_select.on_change('value', update_yaxis)
zlayer_select.on_change('value', update_zaxis)

# Chnages to plot
for w in [region_select, source_select, utility_select, process_select, xlayer_select, xlabel_select, ylayer_select,
          ylabel_select, zlayer_select, zlabel_select, xlog_select, ylog_select, zlog_select, material_select, xref_input,
          yref_input]:
    w.on_change('value', update_plot)

## Generate the page
layout = column(row(controls1, column(make_plot(plot_data, labels[defaults[6]], labels[defaults[7]], labels[defaults[8]],
                                                df_keys, defaults[9], defaults[10], defaults[11], defaults[12], "", ""),
                                                note_LCA, note_TEA), controls2))
curdoc().add_root(layout)
curdoc().title = "KPI-3D"