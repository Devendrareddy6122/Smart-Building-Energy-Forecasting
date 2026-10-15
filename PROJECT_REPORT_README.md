# Smart Building Energy Forecasting — Project Report

This document describes the project as it is implemented in this repository. It can be used as a report draft or as a guide for presenting the project. The forecasting target is a household's hourly electricity demand; the project uses that public household dataset as a stand-in for a single smart building meter.

## 1. Project summary

The project converts one-minute electricity readings into hourly average active power, compares forecasting models, predicts the next 24 hourly values, and presents the history and forecast in an interactive Streamlit dashboard.

The current workflow is local and batch oriented:

1. Read the raw household power dataset.
2. Clean timestamps and readings, then aggregate valid readings by hour.
3. Save the hourly series as a processed CSV.
4. Fit forecasting candidates and select a model using a chronological holdout.
5. Write forecast and comparison CSV files and show results in the dashboard.

Kafka and HDFS components are included as optional integration scaffolding. The current dashboard and batch pipeline read and write local CSV files; they do not automatically send the dataset through Kafka or HDFS.

## 2. The W questions

### What is the project?

A small end-to-end time-series forecasting prototype for hourly electricity demand. It demonstrates data preparation, model fitting, evaluation, result storage, and a dashboard in one Python project.

### Why was it built?

Electricity demand varies throughout the day. A short-term forecast can help a building operator anticipate high-demand periods and plan usage. This prototype explores how historical meter readings can be turned into a next-day forecast and how candidate models compare on recent unseen data.

### Who is it for?

- **Primary user:** a building or facilities operator reviewing recent demand and near-term peaks.
- **Technical user:** a student, analyst, or developer learning an end-to-end forecasting workflow.
- **Not yet intended for:** utility dispatch, billing, safety-critical controls, or production energy management. The source is one household meter, rather than a representative portfolio of commercial buildings.

### Where does the data come from and where is it stored?

The source is the UCI Individual Household Electric Power Consumption dataset. A copy is expected at `data/raw/household_power_consumption.txt`. The download script uses the dataset URL configured in `config/settings.py` if the raw file needs to be downloaded.

The prepared series and model outputs are stored under `data/processed/`. The evaluation report is written to `reports/model_evaluation.md`. HDFS can be configured in the storage helper, but it is not used by the active dashboard path.

### When does it run?

The preprocessing and evaluation scripts run when invoked by a user. The dashboard runs while the Streamlit process is active. Changing its start or end date filters the historical data used for the dashboard forecast; the dashboard then writes updated forecast and holdout-comparison CSVs on rerun. This is not an always-on streaming or scheduled retraining service.

### Which data and models are used?

- **Input measure:** `Global_active_power`, in kilowatts, recorded approximately once per minute.
- **Forecast target:** hourly mean active power in kW. This value is average power, not hourly energy in kWh.
- **Baseline:** repeat the prior day's 24-hour profile.
- **ARIMA:** autoregressive integrated moving average, default order `(2, 1, 2)`.
- **Prophet:** trend and seasonal model with daily and weekly seasonality enabled and yearly seasonality disabled.
- **Selection criterion in the dashboard forecasting path:** lowest mean absolute error (MAE) on the latest 24 observations of the selected date range, when there is enough history for a holdout.

### How does it work?

The raw text file is semicolon-delimited and contains `Date`, `Time`, and power columns. Preprocessing combines date and time into a timestamp, converts the target reading to a number, drops invalid timestamps and missing readings, sorts readings, and removes duplicate timestamps (keeping the last duplicate). It resamples valid readings into hourly means and writes `timestamp,active_power_kw` rows.

For model selection, the forecasting module holds back the final 24 hourly records from the selected history, fits the available candidates to earlier records, and measures each candidate's MAE on the held-out day. It then fits the candidates using the complete selected history and forecasts the following 24 hours. Negative forecasts are clipped to zero. A candidate that fails to fit is skipped; the best available candidate is selected.

The dashboard shows the selected date range, historical demand, a forecast chart, model validation MAE, and an alert threshold. It writes `next_24h_forecast.csv` and `forecast_comparison.csv` in `data/processed/` using the range currently being forecast. The standalone evaluation script instead evaluates ARIMA and Prophet against the last 24 readings in the full processed dataset, writes the same two CSV files, and creates `reports/model_evaluation.md`.

## 3. Dataset and preparation details

The raw UCI file is minute-level household data spanning December 2006 through November 2010. The processed file currently contains 34,168 hourly records. Hours without a valid power reading are omitted after resampling; therefore the hourly timeline may have gaps. The preprocessing code does not interpolate or fill those missing hours.

Only `Global_active_power` is used for the forecast in the current pipeline. Other household measurements in the source file are not included in the model. The resulting series represents one household, not a collection of buildings or an aggregate grid load.

## 4. Architecture and repository map

```text
data/raw/household_power_consumption.txt
                 |
                 v
scripts/run_pipeline.py --> preprocessing/clean_data.py
                 |                  |
                 |                  v
                 +------> data/processed/hourly_consumption.csv
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
                 forecasting/train.py     scripts/evaluate_models.py
                         |                         |
                         +------------+------------+
                                      v
                   forecast CSVs + Streamlit dashboard
```

Key files:

| Path | Purpose |
| --- | --- |
| `app.py` | Streamlit dashboard, date controls, forecast invocation, and output CSV refresh. |
| `preprocessing/clean_data.py` | Timestamp parsing, numeric cleanup, deduplication, and hourly aggregation. |
| `forecasting/train.py` | Candidate generation, chronological holdout selection, and next-24-hour forecast. |
| `forecasting/baseline.py` | Previous-day same-hour profile baseline. |
| `forecasting/arima_model.py` | ARIMA fitting and forecasting. |
| `forecasting/prophet_model.py` | Prophet fitting and forecasting. |
| `forecasting/evaluate.py` | MAE, RMSE, and MAPE calculations. |
| `scripts/run_pipeline.py` | Regenerates `hourly_consumption.csv` from the raw dataset. |
| `scripts/evaluate_models.py` | Evaluates ARIMA and Prophet on the last 24 hours of all processed data; writes forecasts and a report. |
| `data/processed/hourly_consumption.csv` | Hourly input series consumed by the dashboard and evaluation script. |
| `data/processed/forecast_comparison.csv` | Holdout actual values and candidate predictions. In the dashboard this reflects the selected date range. |
| `data/processed/next_24h_forecast.csv` | Next 24 hourly predictions. In the dashboard this reflects the selected date range. |
| `reports/model_evaluation.md` | Summary created by the standalone evaluation script. |
| `kafka/`, `kafka_ingestion/` | Producer, consumer, and topic helpers for optional Kafka use. |
| `storage/hdfs_client.py` | HDFS helper with a local fallback. |

## 5. Installation and running

Use Python 3.10 or newer where possible, create an isolated environment, and install the pinned project dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Regenerate the hourly dataset from the raw text file:

```bash
PYTHONPATH=. python scripts/run_pipeline.py
```

Run the standalone model evaluation and produce its report and CSV outputs:

```bash
PYTHONPATH=. python scripts/evaluate_models.py
```

Start the interactive dashboard from the project root:

```bash
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Choose a start and end date in the sidebar to change the historical window and recompute the dashboard forecast. The current controls choose a date range; there is no file-upload widget for selecting a different raw dataset.

To download the source dataset when it is absent, run:

```bash
PYTHONPATH=. python scripts/download_dataset.py
```

## 6. Results from the current standalone evaluation

The latest saved `reports/model_evaluation.md` reports the following scores for a single chronological 24-hour holdout from the end of the complete processed series:

| Model | MAE (kW) | RMSE (kW) | MAPE |
| --- | ---: | ---: | ---: |
| ARIMA | 0.495419 | 0.625868 | 86.687705% |
| Prophet | 0.471866 | 0.616828 | 39.608031% |

On this holdout, Prophet has lower MAE and RMSE than ARIMA. This result does not prove that Prophet will be better on other dates or buildings. It is one test day and the dashboard independently chooses the best available model for its selected date range. If the dashboard is open, it may overwrite the CSV outputs with its current selected-range results; rerunning the standalone evaluation script restores the full-series batch evaluation outputs and report.

### What the metrics mean

- **MAE** is the average absolute prediction error, in kW. Lower is better and is easy to read in the target's units.
- **RMSE** is the square root of the average squared error, in kW. It penalizes larger misses more heavily than MAE.
- **MAPE** is the average absolute percentage error. The implementation substitutes a denominator of 1 for actual values close to zero, so this figure should be interpreted cautiously for low household loads.

## 7. Dashboard outputs and interpretation

- The historical chart displays hourly average demand for the selected dates.
- The forecast chart overlays the selected forecasting model's next-24-hour estimate on the selected history.
- The model comparison table displays validation MAE values available for that selected range.
- The threshold control is in kW and is used to show a high-demand alert.
- The CSV outputs are useful for inspecting the actual holdout predictions and future forecast outside the dashboard.

Interpret overview values with care: the overview helper currently labels the maximum of the last 48 historical points as “Predicted Peak”; it is a historical peak calculation, not the future forecast peak. Also, the alert condition currently checks the ARIMA forecast column even when another model is selected for the forecast chart. These are known differences between the displayed labels/selection and the underlying alert/overview calculations.

## 8. Scope, assumptions, and limitations

1. The dataset describes one household, so results do not establish performance on a commercial building or a population of meters.
2. The model assumes historical hourly demand contains useful signal for the next 24 hours. Weather, occupancy, tariffs, holidays, and operational schedules are not model inputs.
3. Model selection uses one chronological holdout, not rolling-origin cross-validation. Scores can vary substantially with the chosen date range.
4. Missing minute values are dropped. Missing hourly buckets are omitted rather than imputed, so a long gap can make the series irregular even though the models expect regular hourly steps.
5. The baseline implementation repeats the previous 24 observed values in their order; it does not verify that timestamps are contiguous for the prior day.
6. Forecast candidate exceptions are skipped, which can leave fewer models in the dashboard comparison than expected.
7. Kafka and HDFS are optional helpers, not part of the active forecasting run. No live smart meter data is ingested by the dashboard.
8. The dashboard currently forecasts only the range selected by its date controls. It does not accept a new uploaded dataset.
9. Results are forecasts for analysis and demonstration, not guaranteed demand values or automated control instructions.

## 9. Testing

The repository includes tests for preprocessing, forecasting, metrics, and Kafka message handling. Run them from the project root with:

```bash
PYTHONPATH=. pytest -q
```

## 10. Suggested presentation summary

“This project takes minute-level household electricity readings, cleans and aggregates them into hourly active-power values, and compares a previous-day baseline, ARIMA, and Prophet. It selects among the available models using a recent chronological 24-hour holdout, forecasts the following day, and displays the results in Streamlit. In the current full-series evaluation, Prophet achieved MAE 0.4719 kW compared with ARIMA's 0.4954 kW. The implementation demonstrates the forecasting workflow, while its main limitations are the single-household dataset, one-day evaluation window, and lack of live ingestion or external explanatory variables.”
