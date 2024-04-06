from django.test import TestCase
from unittest.mock import MagicMock
from expenses_tracker.filter_func import expenses_query_filter_func


class ExpensesQueryFilterFuncTestCase(TestCase):
    def setUp(self):
        # Mock the queryset
        self.mock_queryset = MagicMock()

    def test_expenses_query_filter_func_ascending(self):
        # Call the function with ascending sort order
        result = expenses_query_filter_func(
            sort_order='ascending',
            sort_pop=None,
            order_by='amount',
            query_db=self.mock_queryset,
            filter_category='food'
        )

        # Ensure the filter and ordering are applied correctly
        self.mock_queryset.filter.assert_called_once_with(category='food')

        self.mock_queryset.filter().order_by.assert_called_once_with('amount')

        # Ensure the result is returned
        self.assertEqual(result, self.mock_queryset.filter().order_by())

    def test_expenses_query_filter_func_descending(self):
        # Call the function with descending sort order
        result = expenses_query_filter_func(
            sort_order='descending',
            sort_pop=None,
            order_by='date',
            query_db=self.mock_queryset,
            filter_category='transport'
        )

        # Ensure the filter and ordering are applied correctly
        self.mock_queryset.filter.assert_called_once_with(category='transport')
        self.mock_queryset.filter().order_by.assert_called_once_with('-date')

        # Ensure the result is returned
        self.assertEqual(result, self.mock_queryset.filter().order_by())

