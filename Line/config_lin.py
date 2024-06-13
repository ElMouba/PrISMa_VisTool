import pandas as pd
import math
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

# KPI keys
list_keys = [kpis_yml[i]["kpi"] for i in range(len(kpis_yml))]
label_keys = [kpis_yml[i]["label"] for i in range(len(kpis_yml))]
unit_keys = [kpis_yml[i]["unit"] for i in range(len(kpis_yml))]
order_keys = [kpis_yml[i]["order"] for i in range(len(kpis_yml))]
df_keys = pd.DataFrame({"KPI": list_keys, "Label": label_keys, "Unit": unit_keys, "Order": order_keys})
KPI_count = [5, 13, 23]

# Default input (region, source, process, xlayer, ylayer, zlayer, xlabel, ylabel, zlabel, xlog, ylog, zlog, material)
defaults = ['United Kingdom', 'Cement', 'Temperature Swing Adsorption', ['Henry Selectivity'], ['Purity', 'Productivity'],
            ['nCAC'], ['Climate Change', 'Material Resources: Metals/Minerals'], [], 'None', 'w/ Heat Extraction']
kpis = ["None"] + defaults[3] + defaults[4] + defaults[5] + defaults[6]
TOP = 10

# Non-KPIs to drop from the excel file
to_drop = ['Unnamed: 0', 'product_out', 'n_out_vac', 'rho_b', 'time_steps', 'vac_decay', 'selectivity', 'spec_heat_tot',
           'spec_cool_tot','spec_power_tot', 'productivity_tea', 'CO2_captured', 'var_OPEX', 'CAPEX_bd', 'OPEX_bd', 'CAC_bd',
           'power_output_ccs', 'CAC_approx_neg', 'SPECCA_approx_neg']

# Plot Variables
HEIGHT = 600
WIDTH = 800
FONT_SIZE_AXIS = "10pt"
LABEL_OR = math.pi/4
DATA_SIZE = 1

# Widget width
WWIDTH = 300

HELPS = {'Henry Selectivity': 'https://www.youtube.com/watch?v=CCbrVYcvac8',
        'Purity':"https://www.youtube.com/watch?v=qWwJyzBy7Lc",
        'Productivity': "https://www.youtube.com/watch?v=qWwJyzBy7Lc", 
        'nCAC': 'https://www.youtube.com/watch?v=U33Vyb4WJNU', 
        'Climate Change': 'https://www.youtube.com/watch?v=bPx_LMAdIgA', 
        'Material Resources: Metals/Minerals': "https://www.youtube.com/watch?v=bPx_LMAdIgA",
        }

HELPS_EXTRA = {'CaseStudies': 'https://www.youtube.com/watch?v=hoTej9Ls4S8', 
               'TVSA' : 'https://www.youtube.com/watch?v=l_o4tgXxmuw', 
               'KPIs_material': 'https://www.youtube.com/watch?v=CCbrVYcvac8',
               'KPIs_process': 'https://www.youtube.com/watch?v=qWwJyzBy7Lc',
               'KPIs_TEA': 'https://www.youtube.com/watch?v=U33Vyb4WJNU',
               'KPIs_LCA': 'https://www.youtube.com/watch?v=bPx_LMAdIgA'
               }

JSMOL_SCRIPT ="""
set antialiasDisplay ON; background white; set displayCellParameters FALSE; set disablePopupMenu FALSE;
load data "cifstring"
{}
end "cifstring"
    """

CURRENT_STRUCTURES = []