import os
import sys
import json
import pandas as pd
from sqlalchemy import create_engine

def get_engine():
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "retail")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "summary"
    engine = get_engine()

    query = """
        SELECT invoice_date, quantity, unit_price, country, customer_id, description
        FROM online_retail
        WHERE invoice_date IS NOT NULL
          AND quantity IS NOT NULL
          AND unit_price IS NOT NULL
    """
    df = pd.read_sql(query, engine)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["revenue"] = df["quantity"] * df["unit_price"]

    if task == "summary":
        result = {
            "task": "summary",
            "n_rows": int(df.shape[0]),
            "n_cols": int(df.shape[1]),
            "columns": list(df.columns),
            "date_min": str(df["invoice_date"].min()),
            "date_max": str(df["invoice_date"].max()),
            "total_revenue": float(df["revenue"].sum()),
            "n_countries": int(df["country"].nunique()),
            "n_customers": int(df["customer_id"].nunique())
        }

    elif task == "top_countries":
        top = (
            df.groupby("country", as_index=False)["revenue"]
            .sum()
            .sort_values("revenue", ascending=False)
            .head(10)
        )
        result = {
            "task": "top_countries",
            "top_countries": top.to_dict(orient="records")
        }

    elif task == "monthly_revenue":
        monthly = (
            df.groupby(df["invoice_date"].dt.to_period("M"))["revenue"]
            .sum()
            .reset_index()
        )
        monthly["invoice_date"] = monthly["invoice_date"].astype(str)
        result = {
            "task": "monthly_revenue",
            "monthly_revenue": monthly.to_dict(orient="records")
        }

    else:
        result = {
            "task": task,
            "error": f"Unsupported task: {task}"
        }

    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
