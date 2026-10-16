with order_items as (
    select *,
    sum(price) over (partition by order_id ) as total_item_price
    from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

ranked_payments as (
    select
        order_id,
        payment_type,
        payment_installments,
        payment_value,
        row_number() over (
            partition by order_id
            order by payment_value desc
        ) as payment_rank
    from {{ ref('stg_order_payments') }}
),
primary_payment as (
    select order_id, payment_type, payment_installments
    from ranked_payments
    where payment_rank = 1
),
total_payment as (
    select order_id, sum(payment_value) as payment_value
    from {{ ref('stg_order_payments') }}
    group by order_id
),
item_shares as (
    select
        oi.order_id,
        oi.order_item_id,
        tp.payment_value as order_payment_value,
        count(*) over (partition by oi.order_id) as item_count,
        case
            when oi.total_item_price = 0
                then round((tp.payment_value / count(*) over (partition by oi.order_id))::numeric, 2)
            else round(((oi.price / oi.total_item_price) * tp.payment_value)::numeric, 2)
        end as item_share
    from order_items oi
    left join total_payment tp on oi.order_id = tp.order_id
),
allocated_payments as (
    select
        order_id,
        order_item_id,
        (case
            when order_item_id = item_count
            then order_payment_value - coalesce(
                sum(item_share) over (
                    partition by order_id
                    order by order_item_id
                    rows between unbounded preceding and 1 preceding
                ), 0)
            else item_share
        end)::numeric(10,2) as payment_value
    from item_shares
),
ranked_reviews as (
    select
        order_id,
        review_score,
        row_number() over (
            partition by order_id
            order by review_answer_timestamp desc
        ) as review_rank
    from {{ ref('stg_order_reviews') }}
),
latest_review as (
    select order_id, review_score
    from ranked_reviews
    where review_rank = 1
),

dim_customers as (
    select customer_id, customer_key from {{ ref('dim_customers') }}
),
dim_products as (
    select product_id, product_key from {{ ref('dim_products') }}
),
dim_sellers as (
    select seller_id, seller_key from {{ ref('dim_sellers') }}
)

select
    oi.order_id,
    oi.order_item_id,
    c.customer_key,
    p.product_key,
    s.seller_key,
    cast(to_char(o.order_purchase_timestamp, 'YYYYMMDD') as int) as purchase_date_key,
    cast(to_char(o.order_delivered_customer_date, 'YYYYMMDD') as int) as delivered_customer_date_key,
    cast(to_char(o.order_estimated_delivery_date, 'YYYYMMDD') as int) as estimated_delivery_date_key,
    o.order_status,
    oi.price,
    oi.freight_value,
    ap.payment_value,
    pp.payment_type,
    pp.payment_installments,
    lr.review_score
from order_items oi
left join orders o on oi.order_id = o.order_id
left join primary_payment pp on oi.order_id = pp.order_id
left join allocated_payments ap on oi.order_id = ap.order_id and oi.order_item_id = ap.order_item_id
left join latest_review lr on oi.order_id = lr.order_id
left join dim_customers c on o.customer_id = c.customer_id
left join dim_products p on oi.product_id = p.product_id
left join dim_sellers s on oi.seller_id = s.seller_id