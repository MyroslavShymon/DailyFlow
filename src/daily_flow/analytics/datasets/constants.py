from enum import Enum

import numpy as np
from catboost import CatBoostRegressor
from sklearn.ensemble import ExtraTreesRegressor, VotingRegressor
from sklearn.linear_model import BayesianRidge, ElasticNet, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR


class AnalysisProfiles(Enum):
    HISTORICAL = "Historical (Common)"
    SYNTHETIC_BRIDGE = "Synthetic Bridge"
    MODERN_FULL = "Modern (Full)"


class DatasetPeriod(Enum):
    COMMON_ONLY = "common_only"
    MOODS_ONLY = "moods_only"
    FULL = "full"


FINAL_DATASET_PERIODS = {
    DatasetPeriod.COMMON_ONLY: ("2025-01-03", "2025-05-04"),
    DatasetPeriod.MOODS_ONLY: ("2025-10-06", "2025-12-31"),
    DatasetPeriod.FULL: ("2026-01-01", "2026-03-19"),
}


LINEAR_MODELS = [
    "Ridge",
    "BayesianRidge",
    "SVR_linear",
    "SVR",
    "HuberSVR",
    "Lasso",
    "ElasticNet",
    "ElasticNet_Ensemble",
]

MODELS_CONFIG = {
    "ExtraTrees": {
        "model": ExtraTreesRegressor(random_state=42, bootstrap=True),
        "params": {
            "model__n_estimators": [50, 100, 200],
            "model__max_depth": [2, 3, 4],
            "model__min_samples_leaf": [2, 4, 5, 8, 12],
            "model__max_features": ["sqrt", "log2", 1.0],
        },
    },
    "BayesianRidge": {
        "model": BayesianRidge(),
        "params": {
            "model__alpha_1": [1e-6, 1e-4, 1e-2],
            "model__alpha_2": [1e-6, 1e-4, 1e-2],
            "model__lambda_1": [1e-6, 1e-4, 1e-2],
            "model__lambda_2": [1e-6, 1e-4, 1e-2],
        },
    },
    "SVR_linear": {
        "model": SVR(kernel="linear"),
        "params": {
            "model__C": np.logspace(-2, 2, 10).tolist(),
            "model__epsilon": [0.05, 0.1, 0.3],
        },
    },
    "KNN": {
        "model": KNeighborsRegressor(),
        "params": {
            "model__n_neighbors": [3, 5, 7, 10],
            "model__weights": ["uniform", "distance"],
            "model__p": [1, 2],
        },
    },
    "ElasticNet_Ensemble": {
        "model": VotingRegressor(
            estimators=[
                ("en1", ElasticNet(l1_ratio=0.2, max_iter=20000)),
                ("en2", ElasticNet(l1_ratio=0.5, max_iter=20000)),
                ("en3", ElasticNet(l1_ratio=0.8, max_iter=20000)),
            ]
        ),
        "params": {
            "model__en1__alpha": np.logspace(-3, 1, 6),
            "model__en2__alpha": np.logspace(-3, 1, 6),
            "model__en3__alpha": np.logspace(-3, 1, 6),
        },
    },
    "Voting_Cat_SVR": {
        "model": VotingRegressor(
            estimators=[
                (
                    "catboost",
                    CatBoostRegressor(
                        iterations=200,
                        learning_rate=0.05,
                        depth=4,
                        l2_leaf_reg=5,
                        random_seed=42,
                        verbose=0,
                        allow_writing_files=False,
                    ),
                ),
                ("svr", SVR(kernel="rbf")),
            ]
        ),
        "params": {
            "model__catboost__depth": [3, 4, 5],
            "model__catboost__l2_leaf_reg": [3, 5, 7],
            "model__svr__C": [1, 10, 100],
            "model__svr__epsilon": [0.05, 0.1],
        },
    },
    "Voting_Cat_SVR_Ridge": {
        "model": VotingRegressor(
            estimators=[
                (
                    "catboost",
                    CatBoostRegressor(
                        iterations=150,
                        depth=3,
                        verbose=0,
                        allow_writing_files=False,
                    ),
                ),
                ("svr", SVR(C=10)),
                ("ridge", Ridge(alpha=1.0)),
            ]
        ),
        "params": {
            "model__catboost__depth": [3, 4],
            "model__svr__C": [1, 10],
        },
    },
    "CatBoost": {
        "model": CatBoostRegressor(
            iterations=200,
            learning_rate=0.05,
            depth=4,
            l2_leaf_reg=5,
            random_seed=42,
            verbose=0,
            allow_writing_files=False,
        ),
        "params": {
            "model__depth": [1, 2, 3, 4, 5],
            "model__l2_leaf_reg": [3, 5, 7],
            "model__iterations": [200, 500, 800],
            "model__min_data_in_leaf": [3, 5, 8],
        },
    },
    "Ridge": {
        "model": Ridge(),
        "params": {"model__alpha": np.logspace(-2, 3, 15)},
    },
    "SVR": {
        "model": SVR(kernel="rbf"),
        "params": {
            "model__C": [1, 10, 100],
            "model__epsilon": [0.05, 0.1, 0.3],
            "model__gamma": ["scale", 0.01],
        },
    },
    "HuberSVR": {
        "model": SVR(kernel="rbf", epsilon=0.5),
        "params": {
            "model__C": np.logspace(-1, 2, 15).tolist(),
            "model__epsilon": [0.3, 0.5, 0.7, 1.0],
            "model__gamma": ["scale", "auto", 0.01, 0.05],
        },
    },
}

FINETUNE_PARAMS = {
    "Ridge": {
        "model__alpha": [0.1, 1.0, 10.0, 50.0, 100.0],
    },
    "SVR": {
        "model__C": [0.1, 1.0, 5.0, 10.0, 50.0],
        "model__epsilon": [0.1, 0.2, 0.5],
        "model__gamma": ["scale", 0.01, 0.1],
        "model__kernel": ["linear", "rbf"],
    },
    "HuberSVR": {
        "model__C": [0.1, 1.0, 10.0],
        "model__epsilon": [0.5, 0.8, 1.2],
        "model__gamma": ["scale", "auto"],
    },
    "BayesianRidge": {
        "model__alpha_1": [1e-6, 1e-4, 1e-2],
        "model__lambda_1": [1e-6, 1e-4, 1e-2],
    },
    "ExtraTrees": {
        "model__n_estimators": [50, 100],
        "model__max_depth": [2, 3],
        "model__min_samples_leaf": [5, 10, 15],
    },
    "KNN": {
        "model__n_neighbors": [5, 7, 10, 15, 20],
        "model__weights": ["uniform", "distance"],
        "model__p": [1, 2],
    },
    "Voting_Cat_SVR": {
        "model__catboost__depth": [2, 3],
        "model__svr__C": [1, 5, 10],
        "model__svr__epsilon": [0.1, 0.2],
    },
    "Voting_Cat_SVR_Ridge": {
        "model__catboost__depth": [1, 2, 3, 4],
        "model__svr__C": [1, 3, 5, 7, 10, 15],
        "model__ridge__alpha": [1.0, 5.0, 10.0, 50.0, 100.0],
    },
    "Lasso": {
        "model__alpha": np.logspace(-5, 2, 30),
    },
    "ElasticNet": {
        "model__alpha": np.logspace(-4, 2, 15),
        "model__l1_ratio": [0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9],
    },
    "ElasticNet_Ensemble": {
        "model__en1__alpha": np.logspace(-4, 2, 8),
        "model__en2__alpha": np.logspace(-4, 2, 8),
        "model__en3__alpha": np.logspace(-4, 2, 8),
    },
    "SVR_linear": {
        "model__C": [0.01, 0.1, 1.0, 5.0, 10.0],
        "model__epsilon": [0.1, 0.2, 0.5],
    },
    "CatBoost": {
        "model__depth": [1, 2, 3, 4],
        "model__random_strength": [1, 5, 10],
        "model__l2_leaf_reg": [1, 3, 5, 7, 10, 15, 20, 30, 50],
        "model__learning_rate": [0.01, 0.02, 0.03, 0.05, 0.1],
        "model__iterations": [100, 200, 300, 400, 500],
        "model__bootstrap_type": ["Bernoulli"],
        "model__min_data_in_leaf": [2, 5, 10],
        "model__subsample": [0.6, 0.8],
    },
}

# FINETUNE_PARAMS_DEFAULT = {
#     'model__ridge__alpha': np.logspace(-2, 3, 10).tolist(),
# }
