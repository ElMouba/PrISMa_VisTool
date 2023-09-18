import pandas as pd
from pymatgen.core.structure import Structure

from config import MODEL_CACHE, PHIMAGE_CACHE, DUMMY_PHIMAGE, WATER_MODEL_PICKLE, NCAC_MODEL_PICKLE, FROM_PICKLE
from MLmodel import XGBoostOptunaClassifier
from models import ModelResult
from water_resistance.train import train_water_resistance_model
from ncac.train import train_nCAC_model
from fastcore.xtras import load_pickle

from mofdscribe.featurizers.topology.ph_image import PHImage

def _featurize_mof_from_content(content, fmt = 'cif', outdir= None):
    featurizer = PHImage(
    atom_types=(
        "C-H-N-O",
        "C-",
        "F-Cl-Br-I",
        "Cu-Mn-Ni-Mo-Fe-Pt-Zn-Ca-Er-Au-Cd-Co-Gd-Na-Sm-Eu-Tb-V"
        "-Ag-Nd-U-Ba-Ce-K-Ga-Cr-Al-Li-Sc-Ru-In-Mg-Zr-Dy-W-Yb-Y-"
        "Ho-Re-Be-Rb-La-Sn-Cs-Pb-Pr-Bi-Tm-Sr-Ti-Hf-Ir-Nb-Pd-Hg-"
        "Th-Np-Lu-Rh-Pu",
    ),
    spread=0.15,
    min_size=100,
    max_fit_tolerence=0.2,
)
    # featurizer.max_b = [0.0, 34.716224670410156, 33.68175430297852, 0.0]
    # featurizer.max_p = [34.71620407104492, 5.384189414978027, 7.482088851928711, 0.0]
    featurizer.max_b = [0.0, 11.85585823059082, 11.856735992431641, 0.0]
    featurizer.max_p = [8.401015663146973, 8.07491397857666, 4.6178689956665036, 0.0]


    structure = Structure.from_str(content, fmt)

    feats = featurizer.featurize(structure)
    features = featurizer.feature_labels()
    df = pd.DataFrame([dict(zip(features, feats))])
    return df

def get_phImage(content, extension = 'cif', dummy=False):
    if dummy:
        return pd.read_csv(DUMMY_PHIMAGE)
    if content not in PHIMAGE_CACHE:
        print('Calculating PH image...')
        PHIMAGE_CACHE[content] = _featurize_mof_from_content(content, fmt=extension)

    return PHIMAGE_CACHE[content]

def get_water_resistance_model(model_name, from_pickle = True):
    if from_pickle:
        print('Loaded from pickle')
        return load_pickle(WATER_MODEL_PICKLE)
    if model_name not in MODEL_CACHE:
        MODEL_CACHE[model_name] = train_water_resistance_model()
    return MODEL_CACHE[model_name]

def get_nCAC_resistance_model(model_name, from_pickle = True):
    if from_pickle:
        print('Loaded from pickle')
        return load_pickle(NCAC_MODEL_PICKLE)
    if model_name not in MODEL_CACHE:
        MODEL_CACHE[model_name] = train_nCAC_model()
    return MODEL_CACHE[model_name]

def predict_water_resistance(df:pd.DataFrame, model:XGBoostOptunaClassifier):
    print('predicting water resistance')
    feats = df.loc[:, df.columns != 'Unnamed: 0']
        
    prediction = model.predict(feats)
    return prediction[0]

def predict_nCAC(df:pd.DataFrame, model:XGBoostOptunaClassifier):
    print('predicting nCAC')
    feats = df.loc[:, df.columns != 'Unnamed: 0']
        
    prediction = model.predict(feats)
    return prediction[0]


def get_water_resistance_predictions(fileContent, extension = 'cif', model_name = 'nCAC'):
    ph_image = get_phImage(fileContent, extension = extension)
    ph_image_dict = ph_image.to_dict(orient='list')

    model = get_water_resistance_model(model_name, from_pickle=FROM_PICKLE)
    prediction = predict_water_resistance(ph_image, model)

    return ModelResult(model_name = model_name,
                       model_input_type = 'PHImage',
                       model_input_value = ph_image_dict,
                       prediction = prediction,
                       prediction_explanation = 'whether a material can maintain its CO2 adsorption capacity in wet flue gasses')

def get_nCAC_predictions(fileContent, extension = 'cif', model_name = 'nCAC', dummy = False):
    ph_image = get_phImage(fileContent, extension = extension, dummy = dummy)
    ph_image_dict = ph_image.to_dict(orient='list')

    model = get_nCAC_resistance_model(model_name, from_pickle=FROM_PICKLE)
    prediction = predict_nCAC(ph_image, model)

    return ModelResult(model_name = model_name,
                       model_input_type = 'PHImage',
                       model_input_value = ph_image_dict,
                       prediction = prediction,
                       prediction_explanation = 'whether a material has a lower nCAC than the MEA-based benchmark'
                       )
