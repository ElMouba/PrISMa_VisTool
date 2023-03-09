import math
import yaml

# Region
list_regions = ['China', 'United Kingdoms', 'Switzerland', 'United States']

# Source
list_sources = ['Cement', 'Coal Fired Power Plant', 'Natural Gas Power Plant']

# Process
list_processes = ['Temperature Swing Adsorption', 'Temperature/Vacuum Swing Adsorption (0.6)',
                  'Temperature/Vacuum Swing Adsorption (0.2)']

# KPI keys
with open('Line/data/KPIs.yml') as f:
    kpis_yaml = yaml.load(f, Loader=yaml.SafeLoader)
list_keys = [kpis_yaml[i]["kpi"] for i in range(len(kpis_yaml))]
label_keys = [kpis_yaml[i]["label"] for i in range(len(kpis_yaml))]
unit_keys = [kpis_yaml[i]["unit"] for i in range(len(kpis_yaml))]
order_keys = [kpis_yaml[i]["order"] for i in range(len(kpis_yaml))]

# Plot Variables
HEIGHT = 600
WIDTH = 800
FONT_SIZE_AXIS = "10pt"
LABEL_OR = math.pi/4
DATA_SIZE = 1

# Widget width
WWIDTH = 300