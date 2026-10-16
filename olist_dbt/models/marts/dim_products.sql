select
    row_number() over (order by product_id) as product_key,
    p.product_id,
    t.product_category_name_english,
    p.product_category_name,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    p.product_photos_qty
from {{ ref('stg_products') }} p left outer join {{ ref('stg_product_category_translation') }} t
    on p.product_category_name = t.product_category_name