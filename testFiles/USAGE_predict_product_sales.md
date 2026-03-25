# Product Sales Prediction - Quick Usage Guide

## Overview
This script predicts future weekly sales for a single product ID (StockCode) using the best model selected per cluster.

- Default forecast horizon: **12 weeks**

- Script: `testFiles/predict_product_sales.py`
- Model params file: `outputs/final_report_20260325/model_artifacts/best_model_params.json`

## Requirements
Use a Python environment with these packages installed:

- pandas
- numpy
- scikit-learn
- lightgbm (optional; script falls back to RandomForest if unavailable)

Recommended interpreter in this project:

- /opt/homebrew/anaconda3/bin/python

## Run the Script
### Option 1: Pass product ID in command line

```bash
/opt/homebrew/anaconda3/bin/python testFiles/predict_product_sales.py 85123A
```

### Option 1b: Pass product ID and custom horizon

```bash
/opt/homebrew/anaconda3/bin/python testFiles/predict_product_sales.py 85123A 12
```

### Option 2: Interactive input

```bash
/opt/homebrew/anaconda3/bin/python testFiles/predict_product_sales.py
```
Then enter the product ID when prompted.

### Option 3: Specify custom params file

```bash
/opt/homebrew/anaconda3/bin/python testFiles/predict_product_sales.py 85123A outputs/final_report_20260325/model_artifacts/best_model_params.json
```

### Option 4: Product ID + horizon + custom params file

```bash
/opt/homebrew/anaconda3/bin/python testFiles/predict_product_sales.py 85123A 12 outputs/final_report_20260325/model_artifacts/best_model_params.json
```

## Output Format
The script prints JSON with:

- product_id
- cluster
- cluster_label
- selected_model
- horizon_weeks
- predictions (array of future weeks)
- history_weeks
- recent_8_weeks_total_sales
- recent_8_weeks_sales

Example:

```json
{
  "product_id": "85123A",
  "cluster": 2.0,
  "cluster_label": "Steady regulars",
  "selected_model": "RF_C2_BEST",
  "horizon_weeks": 12,
  "predictions": [
    {"week": "2011-12-12/2011-12-18", "predicted_sales": 1791.347},
    {"week": "2011-12-19/2011-12-25", "predicted_sales": 1688.925}
  ],
  "history_weeks": 106,
  "recent_8_weeks_total_sales": 18681.03,
  "recent_8_weeks_sales": [670.05, 1251.44, 5240.94, 1579.61, 3784.42, 2432.75, 1952.39, 1769.43]
}
```

## Notes
- If the product is not found, the script returns an error JSON.
- If LightGBM is not available, LGBM routes automatically fall back to RandomForest.
- The forecast is recursive multi-step ahead (default 12 weeks).
