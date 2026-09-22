from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import logging
from db import create_schema, get_engine

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__) 

file_directory = Path(__file__).parent.parent / "data" / "raw"

string_columns = ["customer_zip_code_prefix", "geolocation_zip_code_prefix", "seller_zip_code_prefix"]

file_table_mapping = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_name_translation"
}

def read_data(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    data = pd.read_csv(file_path, dtype={col: str for col in string_columns})
    return data

def load_to_raw(data, table_name, engine):
    data.to_sql(table_name, con=engine, schema="raw", if_exists="replace", index=False)

if __name__ == "__main__":
    engine = get_engine()
    create_schema(engine, "raw")
    for file_name, table_name in file_table_mapping.items():
        file_path = file_directory / file_name
        try:
            data = read_data(file_path)
            load_to_raw(data, table_name, engine)
            logger.info(f"Data loaded successfully into table {table_name} from file {file_name}")
        except Exception as e:
            logger.error(f"Error processing file {file_name}: {e}")
            continue