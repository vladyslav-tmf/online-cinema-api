movie_schema_example = {}

order_schema_example = {
    "id": 5,
    "user_id": 3,
    "created_at": "2025-01-01",
    "status": "pending",
    "movies": [movie_schema_example],
    "total_amount": 19,
}

order_item_schema_example = {
    "id": 2,
    "order_id": 4,
    "movie_id": 2,
    "price_at_order": 9.5,
}
