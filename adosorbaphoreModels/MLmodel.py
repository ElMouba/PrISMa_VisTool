import os

from fastcore.xtras import load_pickle
import optuna
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import xgboost as xgb

class XGBoostOptunaClassifier(xgb.XGBClassifier):
        def __init__(self, n_trials=100, **kwargs):
            super().__init__(**kwargs)
            self.n_trials = n_trials

        def fit(self, X, y, seed, *args, **kwargs):
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=seed)

            def objective(trial):
                params = {
                "learning_rate": trial.suggest_float("learning_rate", 1e-2, 0.25, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 100.0, log=True),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 100.0, log=True),
                "subsample": trial.suggest_float("subsample", 0.1, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.1, 1.0),
                "max_depth": trial.suggest_int("max_depth", 1, 9),
                "n_estimators": trial.suggest_categorical("n_estimators", [7000, 15000, 20000]),
                }

                model = xgb.XGBClassifier(**params)
                model.fit(X_train, y_train, early_stopping_rounds=10, eval_set=[(X_val, y_val)], verbose=False)

                y_pred = model.predict(X_val)
                accuracy = accuracy_score(y_val, y_pred)
                return 1.0 - accuracy

            study = optuna.create_study(direction='minimize')
            study.optimize(objective, n_trials=self.n_trials)

            self.best_params_ = study.best_params
            super().set_params(**self.best_params_)

            return super().fit(X, y, *args, **kwargs)