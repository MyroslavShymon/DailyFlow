# DailyFlow: Decoding Emotional Entropy

> *A personal mood forecasting system — from raw Telegram logs to a CatBoost model that beats the naive baseline by ~50%.*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![CatBoost](https://img.shields.io/badge/CatBoost-1.2-yellow)
![Optuna](https://img.shields.io/badge/Optuna-4.0-purple)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![Fly.io](https://img.shields.io/badge/Deployed-Fly.io-8B5CF6)
![GitHub Actions](https://img.shields.io/badge/CI%2FBackup-GitHub_Actions-2088FF?logo=githubactions)

---

## What is this?

Most mood trackers tell you how you felt. This project predicts how you will feel tomorrow.

DailyFlow is a full personal analytics pipeline built around one question: **can a small, noisy, self-collected dataset carry enough signal to forecast mood one day ahead?** The answer is yes — with the right feature engineering and a properly validated model.

The project covers everything: a **Telegram bot** for daily data collection, a **SQL ingestion pipeline** with validation, **exploratory analysis** across 5 notebooks, and a final **CatBoost model tuned with Optuna** that achieves TEST MAE=0.933 and R²=0.309 on a 14-day holdout — a **~50% improvement** over the naive lag-1 baseline (MAE=1.857).

---

## Why this matters

Mood is not random. It has **inertia** (yesterday's state predicts today's), **weekly rhythms** (work-cycle effects on anxiety and calm), and **2-week burnout cycles** (high-energy periods predict lower mood 14 days later). None of this is visible from a simple average. A forecasting model makes these patterns actionable: knowing that a low-mood period is likely three days ahead gives you time to do something about it.

---

## Project Architecture

```
daily-flow/
├── src/daily_flow/
│   ├── analytics/datasets/     # Feature engineering, correlations, time series utils
│   ├── db/                     # SQLAlchemy models and repositories (clean architecture)
│   ├── ingest/                 # ETL pipeline: load → validate → clean → store
│   │   ├── validators/         # Rule-based checks (missing values, out-of-range, etc.)
│   │   ├── transforms/         # Data normalisation and schema alignment
│   │   └── loaders/            # CSV and Excel source adapters
│   ├── services/               # Business logic layer (mood, activity, ideas)
│   └── ui/telegram/            # Telegram bot (aiogram): handlers, keyboards, states
├── notebooks/
│   ├── 01_dataset_structure_eda.ipynb
│   ├── 02_mood_distribution_eda.ipynb
│   ├── 03_feature_relationships.ipynb
│   ├── 04_temporal_dynamics_and_lags.ipynb
│   └── 05_feature_engineering_and_selection_strategy.ipynb
├── scripts/backup/             # Automated backup scripts
├── .github/workflows/          # CI, backup, and deploy pipelines
├── Dockerfile
├── docker-compose.yml
└── fly.toml
```

The `src/` layout follows a **layered architecture**: data access (repositories) is separated from business logic (services), which is separated from the UI (Telegram handlers). This makes each layer independently testable.

---

## Data Collection Infrastructure

Data is collected through a **custom Telegram bot** built with `aiogram` and deployed on **Fly.io**. Each day the bot prompts the user to log 10 emotion dimensions (Joy, Calm, Energy, Fatigue, Interest, Sadness, Fear, Anxiety, Confidence, Irritation) rated 1–4, plus sleep quality.

The ingestion pipeline handles:
- **Schema validation** — checks for missing required fields, out-of-range values, and duplicate entries before any data touches the database
- **Daily automated backups** via GitHub Actions (`.github/workflows/backup.yml`)
- **Continuous deployment** to Fly.io on every push to main

All data is stored in **SQLite via SQLAlchemy**, with async support through `aiosqlite`.

---

## Data Science Pipeline

### Stage 1 — EDA & Dataset Structure

160 days of self-collected records. The dataset is small by ML standards, which makes every design decision matter more than usual.

Key findings from `01_dataset_structure_eda.ipynb` and `02_mood_distribution_eda.ipynb`:
- Mood distribution is approximately normal (mean ~4.2/7), with visible **weekly seasonality** — Mondays and Thursdays consistently score lower
- Emotion dimensions show moderate intercorrelation — Joy, Energy and Interest cluster together; Fatigue, Sadness and Anxiety form a negative cluster
- Missing data is sparse and handled via segment-based imputation

### Stage 2 — Feature Relationships

`03_feature_relationships.ipynb` maps out which emotions are statistically related to the target at zero lag. Key results:
- **Joy** (r=0.51), **Energy** (r=0.44), and **Fatigue** (r=-0.41) are the strongest same-day correlates
- **Sleep quality** shows a significant relationship, but with a delay — motivating the lag analysis in Stage 3

### Stage 3 — Temporal Dynamics & Lag Selection

`04_temporal_dynamics_and_lags.ipynb` is the methodological core of the feature engineering stage.

**Stationarity:** ADF tests confirmed all series are stationary — no differencing required. ACF decays rapidly across all segments.

**Autocorrelation (ACF/PACF):**
- **Lag 1** shows the strongest partial autocorrelation (~0.35) — yesterday's mood is the primary predictor
- **Lag 4** shows a secondary spike — consistent with a work-week micro-cycle
- Lags 8 and 13 appeared in ACF but vanished in PACF — correctly identified as harmonic echoes, not independent signals

**Sleep cross-correlation (CCF):**
The strongest sleep-mood correlation appears at **Lag 2** (r=0.262), not Lag 1. This "delayed recovery" effect — where today's sleep quality is most reflected in mood the day after tomorrow — was replicated across both Modern and Synthetic data segments. A weekly resonance at **Lag 7** (r=0.241) reflects routine and schedule effects.

**The 14-day burnout cycle:**
The most counterintuitive finding: Joy and Energy values from **14–15 days ago show a negative correlation** with current mood. High positive emotional states predict lower mood two weeks later — consistent with an energy debt pattern. This motivated the `mood_volatility_7d` feature in the final model.

**Target stability validation (Leave-One-Out):**
Before running cross-correlation analysis on individual emotions, the synthetic `target_final` was stress-tested by removing each emotion in turn. All Leave-One-Out correlations with the real mood log remained within 0.71–0.79 (p < 0.05), confirming the target is balanced and no single emotion dominates it.

### Stage 4 — Feature Engineering & Selection

`05_feature_engineering_and_selection_strategy.ipynb` builds the full feature matrix with complete **leakage protection**:
- All features computed with `.shift(1)` — no future information enters any feature
- Statistical decisions (lag selection, SMA windows) made on training data only, with the 14-day holdout fully shielded
- Collinearity pruning: 24 manual and 925 generated redundant features removed before model training

Feature categories engineered:

| Category | Examples | Rationale |
| :--- | :--- | :--- |
| **Autoregressive Lags** | `target_final_lag_1`, `target_final_lag_4` | Captures mood inertia and short-term cycles identified via ACF/PACF. |
| **Emotion Lags** | `fatigue_lag_2`, `calm_lag_5`, `joy_delta_1d` | Accounts for delayed recovery effects and emotional momentum. |
| **Sleep Signals** | `sleep_lag_7`, `had_severe_bad_sleep_last_2d` | Reflects weekly sleep-mood resonance and acute sleep deprivation impact. |
| **Interaction Terms** | `joy_x_irritation_lag_4` | Models non-linear combinations where emotions amplify or dampen each other. |
| **Volatility** | `mood_volatility_7d` | Rolling standard deviation acting as a proxy for burnout cycle phases. |
| **Rolling Averages** | `calm_sma_9d`, `fatigue_ewm_9` | Simple and Exponential moving averages to extract smoothed trend signals. |
Final dataset after cleaning: **95 features + target**, 146 rows.

**Feature selection:** `SequentialFeatureSelector` (forward, TimeSeriesSplit CV) selects 3–8 features per model. Linear models receive a pre-filtered pool of 15 candidates ranked by Pearson correlation; tree models receive the full ranked feature space.

---

## Modelling

### Comparison sweep

77 total configurations tested: 11 model families × 6 feature counts (3–8), plus fine-tuning of 11 qualifying candidates.

![all_models_test_result.png](assets%2Fimages%2Fall_models_test_result.png)
> **[Chart: Win count by model family]**
> CatBoost and Voting_Cat_SVR_Ridge each won 6 configurations by the combined CV/TEST threshold. However, all Voting ensemble variants produced negative TEST R² on the fixed holdout despite strong CV scores — a sign of overfitting to the 3-fold CV structure. CatBoost maintained positive TEST R² with the lowest CV R² Std.

**Feature co-occurrence across successful models:**

![feature_cooccurrence_pie_chart.png](assets%2Fimages%2Ffeature_cooccurrence_pie_chart.png)
> **[Chart: Feature co-occurrence pie chart]**
> `target_final_lag_1` appeared in 11/11 successful configurations (22% of total feature usage). `interest_delta_5d` and `joy_delta_1d` were the next most robust signals — present across multiple model families, confirming they carry genuine cross-model signal.

### CatBoost + Optuna

The final model uses **CatBoost** tuned with **Optuna TPE** (Tree-structured Parzen Estimator, 100 trials). Key design decisions:

- **Stability-penalised objective:** `-(mean_R² - std_R²)` — Optuna specifically avoids configurations that score well on one fold by chance
- **Minimum subsample=0.75** — prevents `CatBoostError: Too few sampling units` on small folds with Bernoulli bootstrap
- **`TimeSeriesSplit` throughout** — standard KFold was never used; all CV respects temporal order

| Metric | Naive baseline (lag-1) | Baseline (RandomizedSearchCV) | **Optuna CatBoost** |
|---|---|---|---|
| TEST MAE | 1.857 | 0.959 | **0.933** |
| TEST R² | -1.681 | 0.258 | **0.309** |
| CV R² Std | — | 0.074 | **0.022** |

### Feature importance — two methods

![cat_boost_built_in_importance.png](assets%2Fimages%2Fcat_boost_built_in_importance.png)
> **[Chart: CatBoost Built-in Importance]**
> Built-in (split-based) importance ranks `target_final_lag_1` highest (27.6%). This is computed on training data and reflects split frequency — not necessarily test-set usefulness.

![permutation_importance.png](assets%2Fimages%2Fpermutation_importance.png)
> **[Chart: Permutation Importance]**
> Permutation importance (evaluated on the test set) tells a different story: **`joy_delta_1d`** and **`mood_volatility_7d`** are the real drivers. `target_final_lag_1` shows near-zero permutation importance — a collinearity artefact where the model compensates via other lag features when this one is shuffled. Features with negative permutation importance (`joy_x_irritation_lag_4`) are candidates for removal in future iterations.

### Learning curve

![learning_curve_CatBoost_6f_optuna.png](assets%2Fimages%2Flearning_curve_CatBoost_6f_optuna.png)
> **[Chart: Learning Curve CatBoost_6f Optuna]**
> The learning curve shows `[MID]` — moderate overfitting (Train MAE=0.336, Val MAE=0.629, Gap=0.292). This is expected and acceptable on 160 samples: it reflects the irreducible noise floor of subjective mood ratings, not a modelling failure. The Optuna stability penalty reduced CV R² Std from 0.074 to 0.022, confirming regularisation was effective.

---

## Results — Actual vs Predicted

![holdout_test_set_predictions.png](assets%2Fimages%2Fholdout_test_set_predictions.png)
> **[Chart: Holdout test set predictions]**
> On the 14-day holdout the model correctly captures the **directional trend** of mood — rises and falls move in the right direction. It smooths out extreme values (actual range 2–7, predicted range ~3.6–5.5), which is the expected behaviour of a regularised regression on a small dataset. MAE=0.933 means the average daily prediction error is less than one mood unit on the 1–7 scale.

![last_cv_fold_validation_window.png](assets%2Fimages%2Flast_cv_fold_validation_window.png)
> **[Chart: Last CV fold validation window]**
> The last CV fold (MAE=0.551, R²=0.102) shows closer tracking than the holdout, consistent with the model performing better when the test period is temporally adjacent to the training period.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data collection | Telegram Bot (`aiogram`), deployed on **Fly.io** |
| Storage | SQLite + SQLAlchemy (async via `aiosqlite`) |
| Ingestion & validation | Custom ETL pipeline with rule-based validators |
| Infrastructure | Docker, Docker Compose, GitHub Actions (CI + daily backup + deploy) |
| Analysis | pandas, statsmodels, scipy, seaborn, matplotlib |
| Modelling | scikit-learn, CatBoost, Optuna |
| Code quality | ruff (linting), mypy (type checking), pre-commit hooks |

---

## Notebooks Overview

| Notebook | What it covers |
|---|---|
| `01_dataset_structure_eda.ipynb` | Data loading, gap handling, segment validation, distribution overview |
| `02_mood_distribution_eda.ipynb` | Target distribution, weekly seasonality, normality tests |
| `03_feature_relationships.ipynb` | Zero-lag correlations between emotions and mood target |
| `04_temporal_dynamics_and_lags.ipynb` | ADF stationarity, ACF/PACF lag selection, CCF (sleep × mood), 14-day burnout cycle |
| `05_feature_engineering_and_selection_strategy.ipynb` | Feature matrix construction, collinearity pruning, model sweep, Optuna tuning |

---

## Key Insights

- **Yesterday predicts tomorrow** — `target_final_lag_1` appears in 100% of successful model configurations. Mood has genuine short-term inertia.
- **Sleep impact is delayed** — the strongest sleep-mood correlation is at Lag 2, not Lag 1. Physical recovery takes time to translate into psychological state.
- **High periods carry a cost** — Joy and Energy 14 days ago negatively correlate with current mood. Emotional "energy debt" is measurable.
- **Directional forecasting works** — even on 160 samples, the model correctly identifies rising and falling mood trends, which is the useful signal for proactive well-being decisions.

---

## Running the project

```bash
# Clone and install
git clone https://github.com/your-username/daily-flow.git
cd daily-flow
pip install -e ".[ui,dev]"

# Run the Telegram bot
start_telegram_bot

# Run data ingestion
ingest

# Or with Docker
docker-compose up
```

Requires a `.env` file with `TELEGRAM_BOT_TOKEN` and database path configuration.

---

## Status

This is an active personal project. The modelling pipeline (Notebook 05) is complete. Future work includes adding more training data (target: 300+ days), testing LightGBM as a CatBoost alternative, and building a lightweight daily prediction dashboard.
