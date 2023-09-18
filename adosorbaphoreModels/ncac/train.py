import os

from fastcore.xtras import load_pickle, save_pickle
import optuna
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import xgboost as xgb

from config import ALL_DATA_FILE, FEATURE_NAMES_FILE
from MLmodel import XGBoostOptunaClassifier

def train_nCAC_model():
    all_data = pd.read_pickle(ALL_DATA_FILE)
    feature_names = load_pickle(FEATURE_NAMES_FILE)
    feature_names = [f for f in all_data.columns if "phimage" in f]
                

    model = XGBoostOptunaClassifier(n_trials=100)
    model.fit(all_data[feature_names].values, all_data["below_benchmark"].astype(int), seed=42)
    
    save_pickle('nCAC_model.pkl', model)
    
    return model
