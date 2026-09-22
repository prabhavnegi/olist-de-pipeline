from db import get_engine, create_schema
import pandas as pd
from sqlalchemy import text

def truncate_table(engine, table_name, schema_name):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"TRUNCATE TABLE {schema_name}.{table_name} RESTART IDENTITY CASCADE;"))

def transform_customer(engine):
    df = pd.read_sql("SELECT * FROM raw.customers", engine)
    df = df.drop_duplicates(subset="customer_id")
    truncate_table(engine, "dim_customers", "mart")
    df.to_sql("dim_customers", engine, schema="mart", if_exists="append", index=False)

def transform_sellers(engine):
    df = pd.read_sql("SELECT * FROM raw.sellers", engine)
    df = df.drop_duplicates(subset="seller_id")
    truncate_table(engine, "dim_sellers", "mart")
    df.to_sql("dim_sellers", engine, schema="mart", if_exists="append", index=False)

def transform_products(engine):
    df = pd.read_sql("SELECT * FROM raw.products", engine)
    df_2 =  pd.read_sql("SELECT * FROM raw.product_category_name_translation", engine)
    df = df.drop_duplicates(subset="product_id")
    merged_df = df.merge(df_2, on="product_category_name", how="left")
    columns = [
        "product_id",
        "product_category_name",
        "product_category_name_english",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "product_photos_qty",
    ]
    merged_df = merged_df[columns]
    truncate_table(engine, "dim_products", "mart")
    merged_df.to_sql("dim_products", engine, schema="mart", if_exists="append", index=False)

def build_date_table(engine):
    df = pd.read_sql(
            """SELECT MIN(d) AS min_date, MAX(d) AS max_date
            FROM (
            SELECT order_purchase_timestamp AS d FROM raw.orders
            UNION ALL
            SELECT order_delivered_customer_date FROM raw.orders
            UNION ALL
            SELECT order_estimated_delivery_date FROM raw.orders
        ) AS all_dates;""", engine)
    min_date = pd.to_datetime(df["min_date"].iloc[0])
    max_date = pd.to_datetime(df["max_date"].iloc[0])
    start_date = pd.Timestamp(year=min_date.year, month=1, day=1)
    end_date = pd.Timestamp(year=max_date.year, month=12, day=31)
    date_range = pd.date_range(start=start_date, end=end_date)
    date_df = pd.DataFrame({"base_date": date_range})
    date_df['date_key'] = date_df["base_date"].dt.strftime('%Y%m%d').astype(int)
    date_df['full_date'] = date_df["base_date"].dt.date
    date_df["year"] = date_df["base_date"].dt.year
    date_df["month"] = date_df["base_date"].dt.month
    date_df["day"] = date_df["base_date"].dt.day
    date_df["quarter"] = date_df["base_date"].dt.quarter
    date_df["day_of_week"] = date_df["base_date"].dt.dayofweek + 1
    date_df["day_name"] = date_df["base_date"].dt.day_name()
    date_df["is_weekend"] = date_df["day_of_week"].isin([6,7])
    final_cols = ['date_key', 'full_date', 'quarter', 'year', 'month', 'day', 'day_of_week', 'day_name', 'is_weekend']
    date_df = date_df[final_cols]
    truncate_table(engine, "dim_dates", "mart")
    date_df.to_sql("dim_dates", engine, schema="mart", if_exists="append", index=False)

def to_date_int(series):
    return pd.to_datetime(series).dt.strftime('%Y%m%d').astype("Int64")

def transform_orders(engine):
    df = pd.read_sql("SELECT * FROM raw.order_items", engine)
    df_orders = pd.read_sql("SELECT * FROM raw.orders", engine)
    merged_df = df.merge(df_orders, on="order_id", how="left" )
    df_payments = pd.read_sql("SELECT * FROM raw.order_payments", engine)
    total_payment_value = df_payments.groupby("order_id").agg(payment_value=("payment_value", "sum")).reset_index()
    idx = df_payments.groupby("order_id")["payment_value"].idxmax()
    primary_payment = df_payments.loc[idx, ["order_id", "payment_type", "payment_installments"]]
    payments_agg = primary_payment.merge(total_payment_value, on="order_id", how="left")
    df_reviews = pd.read_sql("SELECT * FROM raw.order_reviews", engine)
    reviews_dedup = df_reviews.sort_values("review_answer_timestamp").drop_duplicates(subset="order_id", keep="last")
    merged_df_2 = merged_df.merge(payments_agg, on="order_id", how="left" )
    merged_df_3 = merged_df_2.merge(reviews_dedup, on="order_id", how="left" )
    dim_customers = pd.read_sql("SELECT customer_id, customer_key FROM mart.dim_customers", engine)
    dim_sellers = pd.read_sql("SELECT seller_id, seller_key FROM mart.dim_sellers", engine)
    dim_products = pd.read_sql("SELECT product_id, product_key FROM mart.dim_products", engine)
    merged_df_4 = merged_df_3.merge(dim_customers, on="customer_id", how="left")
    merged_df_5 = merged_df_4.merge(dim_sellers, on="seller_id", how="left")
    merged_df_6 = merged_df_5.merge(dim_products, on="product_id", how="left")
    merged_df_6["purchase_date_key"] = to_date_int(merged_df_6["order_purchase_timestamp"])
    merged_df_6["delivered_customer_date_key"] = to_date_int(merged_df_6["order_delivered_customer_date"])
    merged_df_6["estimated_delivery_date_key"] = to_date_int(merged_df_6["order_estimated_delivery_date"])
    final_cols = ["order_id", "order_item_id", "customer_key", "seller_key", "product_key", "purchase_date_key", "delivered_customer_date_key", "estimated_delivery_date_key", "order_status", "price", "freight_value", "payment_value", "payment_type", "review_score", "payment_installments"]
    final_df = merged_df_6[final_cols]
    truncate_table(engine, "fact_orders", "mart")
    final_df.to_sql("fact_orders", engine, schema="mart", if_exists="append", index=False)

if __name__ == "__main__":
    engine = get_engine()
    transform_customer(engine)
    transform_sellers(engine)
    transform_products(engine)
    build_date_table(engine)
    transform_orders(engine)