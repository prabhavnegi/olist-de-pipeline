select
    f.order_id,
    f.fact_total,
    r.raw_total
from (
    select order_id, sum(payment_value) as fact_total
    from {{ ref('fact_orders') }}
    group by order_id
) f
join (
    select order_id, sum(payment_value) as raw_total
    from {{ ref('stg_order_payments') }}
    group by order_id
) r on f.order_id = r.order_id
where abs(f.fact_total - r.raw_total) > 0.01