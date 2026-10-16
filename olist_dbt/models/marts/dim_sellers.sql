select
    row_number() over (order by seller_id) as seller_key,
    seller_id,
    seller_zip_code_prefix,
    seller_city,    
    seller_state
from {{ ref('stg_sellers') }}