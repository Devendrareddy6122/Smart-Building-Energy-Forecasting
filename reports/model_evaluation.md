# Model Evaluation Report

## Evaluation horizon
- The most recent 24 hourly observations were held back as a test set.
- All earlier observations were used for model fitting.

## Actual metrics

- ARIMA MAE: 0.495419
- ARIMA RMSE: 0.625868
- ARIMA MAPE: 86.687705%
- Prophet MAE: 0.471866
- Prophet RMSE: 0.616828
- Prophet MAPE: 39.608031%

## Forecast sample

| timestamp | actual_demand | arima_forecast | prophet_forecast |
| --- | ---: | ---: | ---: |
| 2010-11-25 22:00:00 | 1.248 | 1.201 | 1.057 |
| 2010-11-25 23:00:00 | 0.957 | 1.116 | 0.625 |
| 2010-11-26 00:00:00 | 0.294 | 1.076 | 0.343 |
| 2010-11-26 01:00:00 | 0.281 | 1.066 | 0.216 |
| 2010-11-26 02:00:00 | 0.273 | 1.075 | 0.147 |

## Peak-demand summary

- Next-24h ARIMA peak: 1.201 kW
- Next-24h Prophet peak: 1.695 kW