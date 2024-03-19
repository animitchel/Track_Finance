
def expenses_query_filter_func(sort_order, sort_pop, order_by, query_db, filter_category=None):
    if not filter_category:
        if sort_order == 'ascending':
            return query_db.order_by(f"{order_by}")
        elif sort_order == 'descending':
            return query_db.order_by(f"-{order_by}")

    if sort_order == 'ascending':

        return query_db.filter(category=filter_category).order_by(f"{order_by}")

    elif sort_order == 'descending':

        return query_db.filter(category=filter_category).order_by(f"-{order_by}")
