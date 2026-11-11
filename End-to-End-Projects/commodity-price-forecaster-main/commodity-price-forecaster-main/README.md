# Commodity Price Forecaster

An interactive **Streamlit dashboard for commodity-market analysis and time-series forecasting** across energy, metals, and agricultural futures. This end-to-end project combines market-data retrieval, exploratory analysis, forecasting, model validation, backtesting, and interactive visualisation.

> **Disclaimer:** This project is for educational and analytical purposes only. Forecasts and risk indicators are not investment, trading, or hedging advice.

## Project Overview

The application helps users explore historical commodity prices, compare forecasting methods, assess forecast errors, and investigate market context through an interactive dashboard.

### Dashboard Features

| Section | Description |
|---|---|
| Market Overview | Historical prices, weekly returns, annualised volatility, and recent highs/lows. |
| Forecast | Forecast paths using Auto-ARIMA, Prophet, LSTM, or an ARIMA–Prophet average. |
| Forecast Validation | Rolling one-step comparisons against naive, drift, and seasonal-naive baselines. |
| Weather Context | Open-Meteo historical weather data aligned with weekly commodity returns. |
| Decomposition | STL trend, seasonal, and residual components. |
| Risk Dashboard | Volatility, drawdown, and trend indicators. |
| Backtest | Walk-forward ARIMA evaluation with configurable horizon and step. |
| Correlations | Correlations between selected commodities' weekly returns. |

## Commodities

The reproducible benchmark covers nine futures contracts:

| Category | Commodity | Yahoo Finance ticker |
|---|---|---|
| Energy | WTI Crude Oil | `CL=F` |
| Energy | Brent Crude | `BZ=F` |
| Energy | Natural Gas | `NG=F` |
| Metals | Gold | `GC=F` |
| Metals | Silver | `SI=F` |
| Metals | Copper | `HG=F` |
| Agriculture | Corn | `ZC=F` |
| Agriculture | Wheat | `ZW=F` |
| Agriculture | Soybeans | `ZS=F` |

The dashboard also supports soft commodities, including coffee, cocoa, sugar, and cotton.

## Forecasting Models

- **Naive:** Uses the latest observed value as the forecast.
- **Drift:** Extends the average historical change.
- **Seasonal Naive:** Repeats the value from the previous seasonal cycle.
- **ARIMA(1,1,1):** Statistical time-series model used in the reproducible benchmark.
- **Auto-ARIMA:** Selects an ARIMA specification when `pmdarima` is installed.
- **Prophet:** Models trend and seasonal patterns.
- **LSTM:** Neural-network approach for time-series forecasting.
- **ARIMA–Prophet average:** Averages the two model forecast paths when both are available.

A more complex model is not automatically more accurate. The benchmark below compares advanced approaches with simple baselines.

## Data Sources

- **Commodity prices:** Yahoo Finance futures data accessed through `yfinance`.
- **Weather:** Historical observations from the [Open-Meteo API](https://open-meteo.com/).
- **Agricultural yields:** USDA NASS Quick Stats data for an optional grains experiment.

The benchmark uses a committed historical price snapshot to make the reported comparison reproducible.

## Benchmark Results

The committed leaderboard evaluates **52 weekly one-step-ahead forecasts**, from **5 October 2025 to 27 September 2026**, across nine futures contracts. The training history begins on 10 January 2016.

| Rank | Model | Average MASE | Average sMAPE |
|---:|---|---:|---:|
| 1 | **Drift** | **2.204** | **4.00%** |
| 2 | Naive | 2.207 | 4.01% |
| 3 | ARIMA(1,1,1) | 2.255 | 4.05% |
| 4 | Prophet | 8.037 | 14.58% |
| 5 | Seasonal Naive | 16.414 | 25.38% |

*Lower error values indicate better performance. Results are from the committed evaluation snapshot.*

**Interpretation:** Drift has the lowest average MASE, but its lead over the naive baseline is very small (0.003 MASE). ARIMA and Prophet did not outperform the simple baselines on average for this one-week forecast task. Seasonal naive performed poorly in this evaluation window.

The repository also includes per-commodity metrics, forecast-versus-actual charts, ARIMA prediction-interval calibration, and an experimental USDA yield-regressor comparison for corn, wheat, and soybeans.

### Prediction-Interval Calibration

Across the same 52 forecast origins, pooled ARIMA interval coverage was **67.1% for nominal 80% intervals** and **79.5% for nominal 95% intervals**. Coverage varies considerably by commodity; the nominal 95% interval covered gold prices only 44.2% of the time. Treat these intervals cautiously rather than as calibrated risk ranges.

### USDA Yield Feature Experiment

A grains-only experiment tests whether lagged USDA national yield information improves one-week forecasts. Average MASE changes from 0.844 for ARIMA to 0.841 for ARIMA plus the yield feature. This is a small change and does not establish a meaningful general improvement; the experiment is kept separate from the main leaderboard.

## Evaluation Methodology

Daily futures closes are converted into weekly observations. At each rolling forecast origin, each model is trained only on data available before the forecast week and predicts the next weekly close.

Evaluation metrics include:
- **MAE:** Mean Absolute Error.
- **RMSE:** Root Mean Squared Error.
- **MAPE / sMAPE:** Percentage-based forecast errors.
- **MASE:** Mean Absolute Scaled Error relative to a naive in-sample error scale.
- **Directional accuracy:** How often the forecast correctly predicts the direction of the next price movement.

See [FORECASTING_METHODOLOGY.md](FORECASTING_METHODOLOGY.md) for the detailed evaluation design, metric definitions, and limitations.

## Technology Stack

| Area | Tools |
|---|---|
| Programming | Python |
| Data processing | pandas, NumPy |
| Forecasting and statistics | statsmodels, pmdarima, Prophet, SciPy |
| Deep learning | PyTorch |
| Visualisation | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Data access | yfinance, requests, Open-Meteo API |
| Testing | pytest |
| Version control | Git, GitHub |

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sarath0034/Data-Analyst-Projects.git
cd Data-Analyst-Projects/End-to-End-Projects/commodity-price-forecaster-main/commodity-price-forecaster-main
```

### 2. Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies and run

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
streamlit run app.py
```

Open the local URL printed by Streamlit in your browser.

## Run Tests

```bash
python -m pytest -q
```

## Reproduce the Benchmark

Run these commands from the project root:

```bash
python scripts/run_leaderboard.py
python scripts/run_calibration.py
python scripts/run_usda_variant.py
```

Prophet results are included when Prophet is installed. Refreshing the USDA cache requires a USDA NASS API key; the committed cache is sufficient for the existing benchmark workflow.

## Project Structure

```text
commodity-price-forecaster/
├── app.py
├── src/                 # Data, forecasting, validation, and chart modules
├── scripts/             # Benchmark and data-refresh scripts
├── data/                # Market-price snapshot and USDA cache
├── results/             # Metrics, benchmark outputs, and charts
├── assets/              # Supporting images and screenshots
├── site/                # Static companion demo
├── tests/               # Automated tests
├── notebooks/           # Model-development notebook
├── FORECASTING_METHODOLOGY.md
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Limitations

- Yahoo Finance continuous futures series can be affected by contract rolls and are not identical to spot prices.
- Historical relationships may not persist under different market conditions.
- Prediction-interval coverage is uneven across commodities; see the calibration results.
- Weather analysis is contextual and does not establish causation.
- Scenario controls are illustrative adjustments, not probability-weighted forecasts.
- External data services may be delayed, revised, incomplete, or unavailable.
- Backtest performance does not guarantee future forecast accuracy.

## What This Project Demonstrates

This project demonstrates an end-to-end analytics workflow: data acquisition, data preparation, exploratory analysis, time-series forecasting, rolling-origin validation, backtesting, performance measurement, and interactive dashboard development.

**Repository:** [Sarath0034/Data-Analyst-Projects](https://github.com/Sarath0034/Data-Analyst-Projects)
