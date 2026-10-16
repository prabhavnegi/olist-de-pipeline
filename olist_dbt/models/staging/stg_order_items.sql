select
    order_id,
    order_item_id,
    seller_id,
    product_id,
    shipping_limit_date,
    price,
    freight_value
from {{ source('raw', 'order_items') }}