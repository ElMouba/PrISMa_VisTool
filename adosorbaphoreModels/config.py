import os

ALLOWED_MODEL_NAMES = ['WaterResistance',
                       'nCAC']

MODEL_CACHE = dict()

PHIMAGE_CACHE = dict()

ALL_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'all_data.pkl')
FEATURE_NAMES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'feature_names.pkl')

DUMMY_PHIMAGE = os.path.join(os.path.dirname(__file__), 'data', 'Nency_139-1_dummy_clean_PHImage.csv')

FROM_PICKLE = True
WATER_MODEL_PICKLE = './water_resistance/water_model.pkl'
NCAC_MODEL_PICKLE= './ncac/nCAC_model.pkl'