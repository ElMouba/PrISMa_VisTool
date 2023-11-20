import pandas as pd

# Adsorption data
DATA_FILE = "data/adsorption_data.csv"
df = pd.read_csv(DATA_FILE)

# Structures
structures = sorted(list(set(df["structure"])))

# Units and Labels
KEYS = ["uptake", "heat"]
LABELS = ["Uptake", "Isosteric Heat of Adsorption"]
UNITS = ["mol/kg", "kJ/mol"]
COLORS = ["blue", "red"]
df_keys = pd.DataFrame({"Property": KEYS, "Label": LABELS, "Unit": UNITS, "Color": COLORS})

# Molecules
MOLECULES = ['CO2', 'N2']

# Default values
defaults = [structures[0], 'CO2', 'Uptake']

# Plot Variables
HEIGHT = 600
WIDTH = 800
FONT_SIZE_LABEL = "13pt"
FONT_SIZE_AXIS = "10pt"
DATA_SIZE = 10

# Widget width
WWIDTH = 300