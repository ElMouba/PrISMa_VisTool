import pandas as pd

DATA_FILE = "data/adsorption_data.csv"
df = pd.read_csv(DATA_FILE)

# Structures
STRUCTURES = sorted(list(set(df["structure"])))

# Widget width
WWIDTH = 300

JSMOL_SCRIPT ="""
set antialiasDisplay ON; background white; set displayCellParameters FALSE; set disablePopupMenu FALSE;
load data "cifstring"
{}
end "cifstring"
    """