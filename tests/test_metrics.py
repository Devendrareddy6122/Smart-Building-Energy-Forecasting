import numpy as np

from forecasting.evaluate import mae_score, mape_score, rmse_score


def test_metric_functions_return_positive_values():
    actual = np.array([1.0, 2.0, 3.0])
    pred = np.array([1.0, 1.0, 5.0])

    assert mae_score(actual, pred) == 1.0
    assert np.isclose(rmse_score(actual, pred), np.sqrt((0.0**2 + 1.0**2 + 2.0**2) / 3.0))
    assert mape_score(actual, pred) > 0
