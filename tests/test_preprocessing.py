import pandas as pd

from preprocessing.clean_data import parse_datetime_column, preprocess_power_data


def test_parse_datetime_column_handles_uci_format():
    df = pd.DataFrame(
        {
            "Date": ["01/12/2006", "02/12/2006"],
            "Time": ["00:00:00", "00:01:00"],
            "Global_active_power": [1.2, 2.1],
        }
    )
    result = parse_datetime_column(df)

    assert "timestamp" in result.columns
    assert str(result["timestamp"].dtype).startswith("datetime64")
    assert result.iloc[0]["timestamp"] == pd.Timestamp("2006-12-01 00:00:00")


def test_preprocess_power_data_handles_missing_and_duplicates():
    df = pd.DataFrame(
        {
            "Date": ["01/12/2006", "01/12/2006", "01/12/2006", "01/12/2006"],
            "Time": ["00:00:00", "00:00:00", "00:01:00", "00:02:00"],
            "Global_active_power": [1.0, 1.0, None, 3.0],
        }
    )

    result = preprocess_power_data(df)

    assert "timestamp" in result.columns
    assert "active_power_kw" in result.columns
    assert result["active_power_kw"].notna().all()
    assert result["timestamp"].is_monotonic_increasing
    assert result["active_power_kw"].dtype.kind in {"f", "i"}
