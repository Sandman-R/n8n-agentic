import os
import sys
import json
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression

def get_engine():
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "retail")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

def main():
    horizon = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    freq = sys.argv[2] if len(sys.argv) > 2 else "D"   # D or M

    engine = get_engine()

    query = """
        SELECT invoice_date, quantity, unit_price
        FROM online_retail
        WHERE invoice_date IS NOT NULL
          AND quantity IS NOT NULL
          AND unit_price IS NOT NULL
    """
    df = pd.read_sql(query, engine)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["revenue"] = df["quantity"] * df["unit_price"]

    if freq == "M":
        ts = (
            df.groupby(df["invoice_date"].dt.to_period("M"))["revenue"]
            .sum()
            .reset_index()
        )
        ts["period"] = ts["invoice_date"].astype(str)
    else:
        ts = (
            df.groupby(df["invoice_date"].dt.date)["revenue"]
            .sum()
            .reset_index()
        )
        ts["period"] = ts["invoice_date"].astype(str)

    ts["t"] = np.arange(len(ts))
    X = ts[["t"]]
    y = ts["revenue"]

    model = LinearRegression()
    model.fit(X, y)

    future_idx = np.arange(len(ts), len(ts) + horizon).reshape(-1, 1)
    preds = model.predict(future_idx)

    result = {
        "task": "forecast",
        "freq": freq,
        "history_points": int(len(ts)),
        "predictions": [float(x) for x in preds]
    }

    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
