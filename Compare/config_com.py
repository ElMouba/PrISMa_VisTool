import pandas as pd
import yaml

with open('data/data_read.yml') as f:
    case_yml = yaml.load(f, Loader=yaml.SafeLoader)

with open('data/KPIs.yml') as f:
    kpis_yml = yaml.load(f, Loader=yaml.SafeLoader)

# Material KPIs
df_mat = pd.read_csv("data/Material_KPIs.csv")

# Case study input
regions = list(case_yml["Region"].keys())
sources = list(case_yml["Source"].keys())
utilities = list(case_yml["Utility"].keys())
processes = list(case_yml["Process"].keys())

# Platform layers
layers = ['Material', 'Process', 'Techno-Economics', 'Life Cycle Assessment']

# x-, y- and z-axes keys 
list_keys = [kpis_yml[i]["kpi"] for i in range(len(kpis_yml))]
label_keys = [kpis_yml[i]["label"] for i in range(len(kpis_yml))]
unit_keys = [kpis_yml[i]["unit"] for i in range(len(kpis_yml))]
df_keys = pd.DataFrame({"KPI": list_keys, "Label": label_keys, "Unit": unit_keys})
KPI_count = [5, 13, 23]

# Default input (region1, source1, process1, utility1, region2, source2, process2, utility2, layer, label, log, material)
defaults = ['United Kingdom', 'Cement', 'Temperature Swing Adsorption', 'w/ Heat Extraction', 'United Kingdom', 'Cement',
            'Temperature Swing Adsorption', 'w/ Heat Extraction', 'Techno-Economics', 'nCAC', 'log', 'None']

# Non-KPIs to drop from the excel file
to_drop = ['Unnamed: 0', 'product_out', 'n_out_vac', 'rho_b', 'time_steps', 'vac_decay', 'selectivity', 'spec_heat_tot',
           'spec_cool_tot','spec_power_tot', 'productivity_tea', 'CO2_captured', 'var_OPEX', 'CAPEX_bd', 'OPEX_bd', 'CAC_bd',
           'power_output_ccs', 'CAC_approx_neg', 'SPECCA_approx_neg']

# Plot Variables
HEIGHT = 600
WIDTH = 800
FONT_SIZE_LABEL = "13pt"
FONT_SIZE_AXIS = "10pt"
DATA_SIZE = 15

# Widget width
WWIDTH = 300