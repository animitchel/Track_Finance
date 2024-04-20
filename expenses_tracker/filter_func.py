def expenses_query_filter_func(sort_order, sort_pop, order_by, query_db, filter_category=None):
    """
    Filter the queryset based on the given parameters.

    Args:
        sort_order (str): Specifies the sorting order ('ascending' or 'descending').
        sort_pop (str): Specifies the sorting preference for the queryset.
        order_by (str): The field by which the queryset is ordered.
        query_db (QuerySet): The queryset to be filtered.
        filter_category (str, optional): The category by which the queryset is filtered.

    Returns:
        QuerySet: The filtered queryset based on the specified parameters.
    """
    if sort_order == 'ascending':
        # Sort the queryset in ascending order based on the specified field
        return query_db.filter(category=filter_category).order_by(f"{order_by}")

    elif sort_order == 'descending':
        # Sort the queryset in descending order based on the specified field
        return query_db.filter(category=filter_category).order_by(f"-{order_by}")


