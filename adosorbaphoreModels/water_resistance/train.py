import os

from fastcore.xtras import load_pickle, save_pickle
import optuna
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import xgboost as xgb

from config import ALL_DATA_FILE, FEATURE_NAMES_FILE
from MLmodel import XGBoostOptunaClassifier

def train_water_resistance_model():
    all_data = pd.read_pickle(ALL_DATA_FILE)
    subset = all_data[all_data['below_benchmark'] == True]
    feature_names = load_pickle(FEATURE_NAMES_FILE)
    feature_names = [f for f in all_data.columns if 'phimage' in f]
                
    subset['below_water_benchmark'] = subset['water_resistance'] < .7
    subset['above_water_benchmark'] = subset['water_resistance'] > .7


    model = XGBoostOptunaClassifier(n_trials=100)
    model.fit(subset[feature_names].values, subset['below_water_benchmark'].astype(int), seed=42)

    save_pickle('water_model.pkl', model)
    return model