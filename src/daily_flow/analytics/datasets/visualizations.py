import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.inspection import permutation_importance
from sklearn.model_selection import learning_curve


def get_ccf_heatmap_settings(ccf_df, conf_level, with_noise=True):
    """
    Returns the parameters for displaying the heatmap to unify the appearance
    across different laptops.
    """
    mask = np.abs(ccf_df) < conf_level if not with_noise else None

    return {
        "mask": mask,
        "cmap": "RdBu_r",
        "center": 0,
        "annot": True,
        "fmt": ".2f",
        "linewidths": 0.5,
        "cbar_kws": {"label": "Correlation Coeff"},
        "alpha": 0.9 if with_noise else 1.0,
    }


def plot_temporal_heatmap(ccf_df, conf_level, with_noise=True, title="Temporal Dynamics"):
    plt.figure(figsize=(14, 10))

    settings = get_ccf_heatmap_settings(ccf_df, conf_level, with_noise)

    sns.heatmap(ccf_df, **settings)

    plt.title(f"{title}\n(Significance threshold: ±{conf_level:.2f})", fontsize=14)
    plt.xlabel("Lag (days ago)")
    plt.ylabel("Features")
    plt.tight_layout()
    plt.show()


def plot_learning_curve(estimator, X, y, cv, model_name="Best Model"):
    train_sizes, train_scores, test_scores = learning_curve(
        estimator,
        X,
        y,
        cv=cv,
        n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 15),
        scoring="neg_mean_absolute_error",
    )

    train_mae = -train_scores
    test_mae = -test_scores
    train_mean, train_std = np.mean(train_mae, axis=1), np.std(train_mae, axis=1)
    test_mean, test_std = np.mean(test_mae, axis=1), np.std(test_mae, axis=1)

    final_train = train_mean[-1]
    final_test = test_mean[-1]
    final_gap = final_test - final_train

    if final_gap > 0.3:
        diagnosis, diag_color = "[WARN] Retraining (large gap train/val)", "#ffaa00"
    elif final_train > 0.7 and final_test > 0.7:
        diagnosis, diag_color = "[LOW] Understudy (both curves are high)", "#ff6666"
    elif final_gap > 0.15:
        diagnosis, diag_color = "[MID] Moderate overfitting — more regularization needed", "#ffcc44"
    else:
        diagnosis, diag_color = "[OK] Balance is normal", "#88ff88"

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1e1e26")
    ax.set_facecolor("#1e1e26")
    ax.plot(train_sizes, train_mean, "o-", color="#ff3333", label="Training error", linewidth=2)
    ax.plot(train_sizes, test_mean, "o-", color="#88ff88", label="Validation error", linewidth=2)
    ax.fill_between(
        train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color="#ff3333"
    )
    ax.fill_between(
        train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color="#88ff88"
    )

    ax.text(
        0.02,
        0.12,
        diagnosis,
        transform=ax.transAxes,
        color=diag_color,
        fontsize=11,
        bbox=dict(boxstyle="round", facecolor="#2e2e3e", alpha=0.8),
    )
    ax.text(
        0.02,
        0.05,
        f"Train MAE: {final_train:.3f} | Val MAE: {final_test:.3f} | Gap: {final_gap:.3f}",
        transform=ax.transAxes,
        color="#aaaaaa",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="#2e2e3e", alpha=0.6),
    )

    ax.set_title(f"Learning Curve — {model_name}", color="white", fontsize=14)
    ax.set_xlabel("Training examples", color="white")
    ax.set_ylabel("MAE (Lower is better)", color="white")
    ax.legend(loc="upper right", facecolor="#2e2e3e", labelcolor="white")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")
    plt.tight_layout()
    plt.show()


def plot_permutation_importance(best_pipe, X_test_sel, y_test):
    result = permutation_importance(
        best_pipe,
        X_test_sel,
        y_test,
        n_repeats=10,
        random_state=42,
        n_jobs=-1,
    )
    importance_df = pd.DataFrame(
        {
            "feature": X_test_sel.columns,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    ).sort_values(by="importance_mean", ascending=False)

    plt.figure(figsize=(10, 6), facecolor="#1e1e26")
    plt.barh(
        importance_df["feature"],
        importance_df["importance_mean"],
        xerr=importance_df["importance_std"],
        color="#88ff88",
    )
    plt.gca().invert_yaxis()
    plt.title("Permutation Importance", color="white")
    plt.xlabel("Reduction R²", color="white")
    plt.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tick_params(colors="white")
    plt.tight_layout()
    plt.show()
    return importance_df
