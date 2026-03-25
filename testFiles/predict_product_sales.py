import json
import os
import sys
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def load_best_params(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def croston_sba_forecast(values: np.ndarray, alpha: float = 0.1) -> float:
    series = np.asarray(values, dtype=float)
    if series.size == 0:
        return 0.0

    series = np.clip(series, 0.0, None)
    non_zero_idx = np.flatnonzero(series > 0)
    if len(non_zero_idx) == 0:
        return 0.0

    demand = series[non_zero_idx[0]]
    interval = non_zero_idx[0] + 1
    last = non_zero_idx[0]

    for idx in non_zero_idx[1:]:
        demand = demand + alpha * (series[idx] - demand)
        interval = interval + alpha * ((idx - last) - interval)
        last = idx

    croston = demand / interval if interval > 0 else 0.0
    return float(max(0.0, (1.0 - alpha / 2.0) * croston))


def build_lag_training(series: np.ndarray, lags: List[int]):
    values = np.asarray(series, dtype=float)
    max_lag = max(lags)
    if len(values) <= max_lag:
        return None, None

    x_rows, y_rows = [], []
    for index in range(max_lag, len(values)):
        row = [values[index - lag] for lag in lags]
        x_rows.append(row)
        y_rows.append(values[index])

    return np.asarray(x_rows, dtype=float), np.asarray(y_rows, dtype=float)


def one_step_by_rf(series: np.ndarray, params: Dict, lags: List[int]) -> float:
    x_train, y_train = build_lag_training(series, lags)
    if x_train is None or len(x_train) == 0:
        return float(np.mean(series[-4:])) if len(series) else 0.0

    model = RandomForestRegressor(**params)
    model.fit(x_train, y_train)

    future_x = np.asarray([[series[-lag] for lag in lags]], dtype=float)
    pred = float(model.predict(future_x)[0])
    return float(max(0.0, pred))


def one_step_by_lgbm_or_rf(series: np.ndarray, params: Dict, lags: List[int], fallback_rf_params: Dict) -> float:
    x_train, y_train = build_lag_training(series, lags)
    if x_train is None or len(x_train) == 0:
        return float(np.mean(series[-4:])) if len(series) else 0.0

    future_x = np.asarray([[series[-lag] for lag in lags]], dtype=float)

    try:
        import lightgbm as lgb

        model = lgb.LGBMRegressor(**params)
        model.fit(x_train, y_train)
        pred = float(model.predict(future_x)[0])
        return float(max(0.0, pred))
    except Exception:
        model = RandomForestRegressor(**fallback_rf_params)
        model.fit(x_train, y_train)
        pred = float(model.predict(future_x)[0])
        return float(max(0.0, pred))


def parse_inputs(argv: List[str], default_param_path: str):
    product_id = None
    horizon = 12
    param_path = default_param_path

    if len(argv) >= 2:
        product_id = str(argv[1]).strip()

    if len(argv) >= 3:
        arg2 = str(argv[2]).strip()
        if arg2.lower().endswith(".json"):
            param_path = arg2
        else:
            horizon = int(arg2)

    if len(argv) >= 4:
        param_path = str(argv[3]).strip()

    if not product_id:
        product_id = input("Enter product id (StockCode): ").strip()

    if horizon <= 0:
        raise ValueError("horizon must be > 0")

    return product_id, horizon, param_path


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_param_path = os.path.join(base_dir, "outputs", "final_report_20260325", "model_artifacts", "best_model_params.json")

    product_id, horizon, param_path = parse_inputs(sys.argv, default_param_path)

    if not product_id:
        print(json.dumps({"error": "Empty product id"}, ensure_ascii=False))
        sys.exit(1)

    params_bundle = load_best_params(param_path)

    sales_path = os.path.join(base_dir, params_bundle.get("sales_file", "online retail/total_retail_cleaned.csv"))
    cluster_path = os.path.join(base_dir, params_bundle.get("cluster_feature_file", "clustering data/product_features_clustered.csv"))

    retail = pd.read_csv(sales_path)
    clusters = pd.read_csv(cluster_path)

    if "InvoiceDate" in retail.columns:
        retail["InvoiceDate"] = pd.to_datetime(retail["InvoiceDate"], errors="coerce")

    retail["StockCode"] = retail["StockCode"].astype(str)
    clusters["StockCode"] = clusters["StockCode"].astype(str)

    qty_col = "Quantity" if "Quantity" in retail.columns else "quantity"
    price_col = "Price" if "Price" in retail.columns else "unit_price"
    invoice_col = "Invoice" if "Invoice" in retail.columns else "invoice"

    retail = retail[retail[qty_col].notna() & retail[price_col].notna()].copy()
    retail = retail[retail[price_col] > 0].copy()

    if invoice_col in retail.columns:
        retail = retail[~retail[invoice_col].astype(str).str.startswith("C")].copy()

    retail["sales"] = retail[qty_col].astype(float) * retail[price_col].astype(float)
    retail["week"] = retail["InvoiceDate"].dt.to_period("W")

    product_sales = retail[retail["StockCode"] == product_id].copy()
    if product_sales.empty:
        print(json.dumps({"product_id": product_id, "error": "Product not found in sales file"}, ensure_ascii=False))
        sys.exit(1)

    weekly = (
        product_sales.groupby("week", as_index=False)["sales"]
        .sum()
        .sort_values("week")
    )

    all_weeks = pd.period_range(start=weekly["week"].min(), end=weekly["week"].max(), freq="W")
    weekly = weekly.set_index("week").reindex(all_weeks, fill_value=0.0).reset_index()
    weekly.columns = ["week", "sales"]

    cluster_row = clusters[clusters["StockCode"] == product_id]
    if cluster_row.empty:
        cluster_id = None
        cluster_label = None
    else:
        cluster_id = float(cluster_row.iloc[0]["cluster"])
        cluster_label = str(cluster_row.iloc[0].get("cluster_label", ""))

    selected_model = "RF_Default"
    selected_params = params_bundle["defaults"].get("BASELINE_RF_PARAMS", {"n_estimators": 300, "random_state": 42, "n_jobs": -1})

    if cluster_id is not None:
        matched = [cfg for cfg in params_bundle.get("cluster_configs", []) if float(cfg.get("cluster")) == cluster_id]
        if matched:
            selected_model = matched[0].get("selected_model", selected_model)
            selected_params = matched[0].get("params", selected_params)

    lag_features = params_bundle.get("defaults", {}).get("lag_features", [1, 2, 4, 8, 13])
    values = weekly["sales"].values.astype(float)

    history = values.copy()
    forecast_values = []
    future_weeks = [weekly["week"].max() + offset for offset in range(1, horizon + 1)]

    for _ in range(horizon):
        if selected_model == "CrostonSBA":
            alpha = float(selected_params.get("alpha", params_bundle.get("defaults", {}).get("CROSTON_ALPHA", 0.1)))
            step_pred = croston_sba_forecast(history, alpha=alpha)
        elif selected_model in {"RF_Default", "RF_C2_BEST"}:
            step_pred = one_step_by_rf(history, selected_params, lag_features)
        elif selected_model in {"LGBM_Default", "LGBM_Tuned"}:
            fallback_rf = params_bundle.get("defaults", {}).get("BASELINE_RF_PARAMS", {"n_estimators": 300, "random_state": 42, "n_jobs": -1})
            step_pred = one_step_by_lgbm_or_rf(history, selected_params, lag_features, fallback_rf)
        else:
            fallback_rf = params_bundle.get("defaults", {}).get("BASELINE_RF_PARAMS", {"n_estimators": 300, "random_state": 42, "n_jobs": -1})
            step_pred = one_step_by_rf(history, fallback_rf, lag_features)

        forecast_values.append(float(step_pred))
        history = np.append(history, step_pred)

    predictions = [
        {"week": str(period), "predicted_sales": round(float(value), 4)}
        for period, value in zip(future_weeks, forecast_values)
    ]

    result = {
        "product_id": product_id,
        "cluster": cluster_id,
        "cluster_label": cluster_label,
        "selected_model": selected_model,
        "horizon_weeks": int(horizon),
        "predictions": predictions,
        "history_weeks": int(len(weekly)),
        "recent_8_weeks_total_sales": round(float(np.sum(values[-8:])), 4),
        "recent_8_weeks_sales": [round(float(x), 4) for x in values[-8:].tolist()],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
