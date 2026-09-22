# olist-de-pipeline

An end-to-end ELT pipeline for the [Olist Brazilian E-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce):
raw CSVs → Postgres raw layer → a Kimball-style star schema for analytics.

## Architecture

```
9 CSVs  --ingest.py-->  raw.* tables (Postgres)  --transform.py-->  mart.* star schema
```

**Extract + Load (`raw` schema):** `scripts/ingest.py` reads all 9 source CSVs and loads
each into its own table under `raw.*`, close to as-is (mostly text-typed, no constraints).
This is the landing zone — disposable and fully rebuildable from the CSVs at any time.

**Transform (`mart` schema):** `scripts/transform.py` reads from `raw.*`, deduplicates,
joins, and aggregates, then writes into a star schema:

- `dim_customers`, `dim_products` (joined with English category translations),
  `dim_sellers`, `dim_dates` — descriptive dimensions with surrogate keys
- `fact_orders` — one row per order line item, with foreign keys into every dimension,
  plus price, freight, aggregated payment info, and review score

Grain of `fact_orders`: **one row per order line item** (one product within one order).

## Setup

```bash
git clone <this repo>
cd olist-de-pipeline
python -m venv venv && source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt

# Download the 9 CSVs from Kaggle and place them in data/raw/
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

cp .env.example .env      # edit with your local Postgres credentials
docker compose up -d      # starts Postgres
```

## Run

```bash
# 1. Create the mart (star schema) tables
docker exec -i olist-postgres psql -U postgres -d olist < sql/02_create_star_schema.sql

# 2. Load raw CSVs into Postgres (also creates the raw schema/tables)
cd scripts && python -m ingest

# 3. Build the star schema from the raw layer
python -m transform
```

## Schema notes / design decisions

- **Surrogate keys** (`customer_key`, `product_key`, etc.) are auto-incrementing integers
  generated in the warehouse, separate from the natural keys (`customer_id`, etc.) used
  by the source system — standard Kimball dimensional modeling practice.
- **`dim_dates`** is a generated calendar dimension (one row per day) rather than storing
  raw timestamps in the fact table — lets queries `GROUP BY` on year/quarter/weekend
  without repeating date-math logic in every query.
- **Split payments**: an order can have multiple payment rows (e.g. part voucher, part
  credit card). `payment_value` is summed across all of an order's payments;
  `payment_type`/`payment_installments` are taken from the single largest payment row
  (via `idxmax()`) so the two values stay consistent with each other rather than being
  aggregated independently.
- **Multiple reviews per order**: some orders have more than one review submitted at
  different times. The most recent review (by answer timestamp) is kept.
- **Undelivered/cancelled orders** have a `NULL` `delivered_customer_date_key` — left
  null rather than backfilled with a placeholder, since no delivery genuinely happened.

## Status / roadmap

- [x] Raw ingestion (9 CSVs → Postgres)
- [x] Star schema transform (pandas)
- [ ] dbt models (staging + mart, with tests) — replacing the pandas transform
- [ ] Airflow DAG to orchestrate ingest → transform on a schedule
- [ ] Docker Compose for the full stack (Postgres + Airflow + pipeline)
- [ ] Raw file backup to GCS

## Why this project

Built to demonstrate core data engineering skills — dimensional modeling, ELT from
messy multi-table source data into an analytics-ready star schema, and handling
real-world data quality issues (split payments, duplicate reviews, missing delivery
dates) — using a realistic e-commerce dataset.
