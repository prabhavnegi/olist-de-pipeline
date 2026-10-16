with recursive date_spine as(
    select cast('2016-01-01' as date) as full_date
    union all
    select cast(full_date + interval '1 day' as date)
    from date_spine
    where full_date < '2018-12-31'
)
select
    cast(to_char(full_date, 'YYYYMMDD') as int) as date_key,
    full_date,
    extract(quarter from full_date) as quarter,
    extract(year from full_date) as year,
    extract(month from full_date) as month,
    extract(day from full_date) as day,
    extract(isodow from full_date) as day_of_week,
    to_char(full_date, 'Day') as day_name,
    extract(isodow from full_date) in (6, 7) as is_weekend
from date_spine