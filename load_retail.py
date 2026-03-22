import pandas as pd
from sqlalchemy import create_engine

# 1. 读 xlsx（注意文件名）
df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")

# 2. 统一列名（强烈推荐，后面 SQL / Agent 都省心）
df = df.rename(columns={
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "Customer ID": "customer_id",
    "Country": "country"
})

# 3. 基本清洗
df = df.dropna(subset=["description", "customer_id"])

df["invoice_date"] = pd.to_datetime(df["invoice_date"])
df["revenue"] = df["quantity"] * df["unit_price"]

# 4. 连本地 Postgres（docker-compose 那套）
engine = create_engine(
    "postgresql://postgres:postgres@localhost:5432/retail"
)

# 5. 写入数据库
df.to_sql(
    "online_retail",
    engine,
    if_exists="replace",
    index=False
)

print("✅ online_retail 表已成功写入 Postgres")