''' Case Study 3D Plots '''

import bokeh.models as bmd
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import OpenURL, TapTool, Select, Paragraph, Spacer
from bokeh.plotting import figure
from config_com import *
from os.path import dirname, join

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
    dataset = pd.merge(df_mat, df_wrc, df_kpi, on="MOF")

    return dataset

# A standard script for bokeh plotting
def make_plot(dataset1, dataset2, label, df_keys, log, material):
    # This is to avoid negative data in the case of nCAC and some other TEA KPIs 
    dataset1_pos = dataset1[dataset1[label] >= 0]
    dataset2_pos = dataset2[dataset2[label] >= 0]

    # Need to form a dataset with three entries: common_MOFs, label_1 and label_2 values
    MOFs_1 = list(dataset1_pos["MOF"])
    MOFs_2 = list(dataset2_pos["MOF"])
    MOFs = list(set(MOFs_1).intersection(MOFs_2))

    label_1 = []
    label_2 = []
    for i in MOFs:
        label_1.append(dataset1_pos[label][dataset1_pos["MOF"] == i].iloc[0])
        label_2.append(dataset2_pos[label][dataset2_pos["MOF"] == i].iloc[0])

    dataset_pos = pd.DataFrame({"MOF":MOFs, "label1":label_1, "label2":label_2})
    material_select.options = ["None"] + MOFs
    
    source = bmd.ColumnDataSource(data=dataset_pos)
    hover = bmd.HoverTool(tooltips= [("MOF", "@MOF")])

    p = figure(height=HEIGHT, width=WIDTH, toolbar_location='above', x_axis_type=log, y_axis_type=log,
               tools=['pan', 'wheel_zoom', 'box_zoom', 'save', 'reset', 'tap', hover], active_drag='box_zoom')

    xax = df_keys["Label"][df_keys["KPI"]==label].iloc[0] + " (" + df_keys["Unit"][df_keys["KPI"]==label].iloc[0] + ")"
    yax = df_keys["Label"][df_keys["KPI"]==label].iloc[0] + " (" + df_keys["Unit"][df_keys["KPI"]==label].iloc[0] + ")"
    p.xaxis.axis_label = xax + " - Case Study 1"
    p.yaxis.axis_label = yax + " - Case Study 2"
    p.xaxis.axis_label_text_font_size = FONT_SIZE_LABEL
    p.yaxis.axis_label_text_font_size = FONT_SIZE_LABEL
    p.xaxis.major_label_text_font_size = FONT_SIZE_AXIS
    p.yaxis.major_label_text_font_size = FONT_SIZE_AXIS

    # Update the plot when you have a structure of interest
    if material == "None":
        p.circle("label1", "label2", size=DATA_SIZE, source=source, alpha=0.5, fill_color="blue")
    else:
        dataset_pos_1 = dataset_pos[dataset_pos["MOF"]==material]
        source2 = bmd.ColumnDataSource(data=dataset_pos_1)
        p.circle("label1", "label2", size=DATA_SIZE, source=source, alpha=0.1, fill_color="blue")
        p.diamond("label1", "label2", size=DATA_SIZE, source=source2, alpha=1.0, line_color="black", fill_color="red")
   
    # Link the data points to the table
    url = "https://prisma.matcloud.xyz/Table?name=@MOF"
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url=url)
    
    return p

# Update the layout given the different options 
def update_source1(attr, old, new):
    region = region1_select.value
    source = source1_select.value

    if region == "Switzerland":
        source1_select.options = [sources[0], sources[2]]
        if source != "Cement":
            source1_select.value = source1_select.options[0]
    elif region == "United Kingdom 2022":
        source1_select.options = [sources[0], sources[2]]
        source1_select.value = source1_select.options[0]
    else:
        source1_select.options = sources

def update_source2(attr, old, new):
    region = region2_select.value
    source = source2_select.value

    if region == "Switzerland":
        source2_select.options = [sources[0], sources[2]]
        if source != "Cement":
            source2_select.value = source2_select.options[0]
    elif region == "United Kingdom 2022":
        source2_select.options = [sources[0], sources[2]]
        source2_select.value = source2_select.options[0]
    else:
        source2_select.options = sources

def update_utility1(attr, old, new):
    region = region1_select.value
    source = source1_select.value

    if region == "Switzerland":
        utility1_select.visible = True
        if source == "Cement":
            utility1_select.options = utilities[:2]
            utility1_select.value = utility1_select.options[0]
        elif source == "Natural Gas Power Plant":
            utility1_select.options = utilities[:4]
            utility1_select.value = utility1_select.options[0]

    elif region == "United Kingdom":
        if source != "Cement":
            utility1_select.visible = True
            utility1_select.options = utilities[4:6]
            utility1_select.value = utility1_select.options[0]
        else:
            utility1_select.visible = False
            utility1_select.value = "w/ Heat Extraction"

    else:
        utility1_select.visible = False
        utility1_select.value = "w/ Heat Extraction"

def update_utility2(attr, old, new):
    region = region2_select.value
    source = source2_select.value

    if region == "Switzerland":
        utility2_select.visible = True
        if source == "Cement":
            utility2_select.options = utilities[:2]
            utility2_select.value = utility2_select.options[0]
        elif source == "Natural Gas Power Plant":
            utility2_select.options = utilities[:4]
            utility2_select.value = utility2_select.options[0]

    elif region == "United Kingdom":
        if source != "Cement":
            utility2_select.visible = True
            utility2_select.options = utilities[4:6]
            utility2_select.value = utility2_select.options[0]
        else:
            utility2_select.visible = False
            utility2_select.value = "w/ Heat Extraction"

    else:
        utility2_select.visible = False
        utility2_select.value = "w/ Heat Extraction"

def update_axis(attr, old, new):
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
    region1val = region1_select.value
    source1val = source1_select.value
    utility1val = utility1_select.value
    process1val = process1_select.value

    region2val = region2_select.value
    source2val = source2_select.value
    utility2val = utility2_select.value
    process2val = process2_select.value

    label = label_select.value
    log = log_select.value
    material = material_select.value
    labelval = labels[label]
    
    src1 = get_dataset(region1val, source1val, process1val, utility1val)
    src2 = get_dataset(region2val, source2val, process2val, utility2val)
    plot_data1.update(src1)
    plot_data2.update(src2)
    layout.children[0].children[1] = column(make_plot(plot_data1, plot_data2, labelval, df_keys, log, material), note_LCA, note_TEA)
    
## Initialize the dictionaries
labels = {label_keys[i]:list_keys[i] for i in range(len(list_keys))}
materials = list(get_dataset(defaults[0], defaults[1], defaults[2], defaults[3])["MOF"])

## Initialize the widgets
# Case study 1
region1_select = Select(title='Region 1', options=regions, value=defaults[0], width=WWIDTH)
source1_select = Select(title='Source 1', options=sources, value=defaults[1], width=WWIDTH)
utility1_select = Select(title='Utility 1', visible=False, value=defaults[3], width=WWIDTH)
process1_select = Select(title='Process Type 1', options=processes, value=defaults[2], width=WWIDTH)
# Case study 2
region2_select = Select(title='Region 2', options=regions, value=defaults[4], width=WWIDTH)
source2_select = Select(title='Source 2', options=sources, value=defaults[5], width=WWIDTH)
utility2_select = Select(title='Utility 2', visible=False, value=defaults[7], width=WWIDTH)
process2_select = Select(title='Process Type 2', options=processes, value=defaults[6], width=WWIDTH)

# Choose 1 single layer and 1 single KPI
layer_select = Select(title='Platform Layer', options=layers, value=defaults[8], width=WWIDTH)
label_select = Select(title="Label", options=list(labels.keys())[KPI_count[1]:KPI_count[2]], value=defaults[9], width=WWIDTH)
log_select = Select(title="Scale", options=["linear", "log"], value=defaults[10], width=WWIDTH)

material_select = Select(title="Material of Interest", options=["None"] + materials, value=defaults[11], width=WWIDTH)
note_LCA = Paragraph(text="""* LCA KPIs are per 1 kg of CO\u2082 captured""", width=WWIDTH)
note_TEA = Paragraph(text="""** Specific CO\u2082 Emissions are described per unit product for industrial cases and per unit
electricity for power plants""", width=int(2.5*WWIDTH))

## Get the initial plot data
plot_data1 = get_dataset(defaults[0], defaults[1], defaults[2], defaults[3])
plot_data2 = get_dataset(defaults[4], defaults[5], defaults[6], defaults[7])

controls1 = column(region1_select, source1_select, utility1_select, process1_select, Spacer(margin=(0, 0, 30, 0)),
                   region2_select, source2_select, utility2_select, process2_select)
controls2 = column(layer_select, label_select, log_select, material_select)

## Dynamic changes to the layout
region1_select.on_change('value', update_source1)
region2_select.on_change('value', update_source2)
for widget in [region1_select, source1_select]:
    widget.on_change('value', update_utility1)
for widget in [region2_select, source2_select]:
    widget.on_change('value', update_utility2)
layer_select.on_change('value', update_axis)

# Changes to plot
for w in [region1_select, source1_select, utility1_select, process1_select, region2_select, source2_select, utility2_select,
          process2_select, layer_select, label_select, log_select, material_select]:
    w.on_change('value', update_plot)

## Generate the page
layout = column(row(controls1, column(make_plot(plot_data1, plot_data2, labels[defaults[9]], df_keys, defaults[10],
                                                defaults[11]), note_LCA, note_TEA), controls2))
curdoc().add_root(layout)
curdoc().title = "Compare"