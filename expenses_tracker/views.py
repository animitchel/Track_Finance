from functools import wraps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.db.models import Count, Sum, Avg

from .form_models import (
    ProfileForm, TransactionForm, BudgetForm, IncomeForm, ContactForm, UserForm, LoginForm
)
from django.views import View
from datetime import datetime, timedelta
from .models import Transaction, Budget, Profile, Income
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.template.loader import render_to_string, get_template
from django.utils import timezone

from .filter_func import expenses_query_filter_func
from expenses_tracker.form_models import ExpenseIncomeReportForm, DateForm
from expenses_tracker.email_client import send_message
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from expenses_tracker.graphical_insights import linechart, barchart
from expenses_tracker.redirect_endpoints import url_has_allowed_host_and_scheme_func
from django.conf import settings

from django.core.cache import cache
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator


@method_decorator(cache_page(30), name='dispatch')
class IndexView(TemplateView):
    template_name = 'expenses_tracker/index.html'  # Define the template name for this view

    def get_context_data(self, **kwargs):
        # Call the parent class method to get the context data
        context = super(IndexView, self).get_context_data(**kwargs)

        # Add the user authentication status to the context
        context['user_status'] = self.request.user.is_authenticated

        # Add the current year to the context
        context['current_year'] = datetime.now().year

        # Return the updated context
        return context


@cache_page(60 * 3)
@login_required
def overview(request):
    # Get all transactions associated with the logged-in user
    transactions = Transaction.objects.all().filter(user_id=request.user.id)

    # Retrieve the 3 most recent transactions
    category_transactions = transactions.order_by('-date')[:3]

    # Calculate the total sum of all transactions
    transactions_sum_total = transactions.aggregate(amount=Sum('amount'))

    # Group transactions by category and calculate the sum of each category
    category = {field.category: transactions.filter(category=field.category).aggregate(
        sum=Sum('amount')).get('sum') for field in category_transactions}

    # Assign the 3 most recent transactions to recent_transactions
    recent_transactions = category_transactions

    # Get the 3 most recent recurring transactions
    recurring_transaction = transactions.filter(recurring_transaction=True).order_by('next_occurrence')[:3]

    # Retrieve all budgets associated with the logged-in user
    budget = Budget.objects.all().filter(user_id=request.user.id)

    # Calculate the total sum of all budgets
    budget_sum_total = budget.aggregate(budget=Sum('budget'))

    # Calculate the remaining total amount of all budgets
    budget_remaining_total = budget.aggregate(amount=Sum('amount'))

    # Get the 3 budgets with the closest expiration dates
    all_budget = budget.order_by('expiration_date')[:3]

    # Get the current date and time
    date_now = timezone.now()

    # Retrieve all income data associated with the logged-in user
    income_data = Income.objects.all().filter(user_id=request.user.id)

    # Calculate the total sum of all income
    total_income = income_data.aggregate(amount=Sum('amount'))

    # Get the 3 most recent income entries
    recent_income_data = income_data.order_by('-date')[:3]

    # Get the user's preferred currency from the session
    user_currency = request.session.get('user_currency')

    # Render the overview template with the calculated context data
    return render(
        request,
        'expenses_tracker/overview.html',
        context={'transactions': transactions_sum_total['amount'],
                 'category': category,
                 'recent_transactions': recent_transactions,
                 'budget': all_budget,
                 'total_budget': budget_sum_total['budget'],
                 'budget_remaining_total': budget_remaining_total['amount'],
                 'recur_transaction': recurring_transaction,
                 'date_now': date_now,
                 'user_currency': user_currency,
                 'user_status': request.user.is_authenticated,
                 'total_income': total_income['amount'],
                 'income_data': recent_income_data,
                 'current_year': date_now.year
                 }
    )


class AllTransactionsView(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/all_transactions.html'
    model = Transaction
    context_object_name = 'transactions'
    paginate_by = 50

    def get_paginate_by(self, queryset):
        search_query = self.request.session.get('search_query')
        if search_query:
            return None   # Disable pagination
        return self.paginate_by  # Use default pagination

    # Method to get the queryset of transactions
    def get_queryset(self):
        # Get session data for filter category, sort order, and search query
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')
        search_query = self.request.session.get('search_query')

        # Get the initial queryset of all transactions for the logged-in user
        query = super(AllTransactionsView, self).get_queryset().filter(user_id=self.request.user.id)

        if filter_category:
            # Apply filtering based on category if filter category is provided
            filtered_query = expenses_query_filter_func(
                sort_order=sort_order,
                filter_category=self.request.session.pop('filter_category'),
                order_by=self.request.session.pop('order_by'),
                query_db=query,
                sort_pop=self.request.session.pop('sort_order')
            )

            # Calculate the total amount of filtered transactions
            total_trans_queried_amount = filtered_query.aggregate(amount=Sum('amount'))
            self.request.session['total_trans_queried_amount'] = total_trans_queried_amount['amount']

            # Return the filtered queryset ordered by date
            return filtered_query

        elif search_query:
            # Apply filtering based on search query if search query is provided
            filtered_query = query.filter(description__icontains=search_query)
            total_trans_queried_amount = filtered_query.aggregate(amount=Sum('amount'))
            self.request.session['total_trans_queried_amount'] = total_trans_queried_amount['amount']

            # Return the filtered queryset ordered by date
            return filtered_query.order_by('date')

        # Return the initial queryset ordered by date (default)
        return query.order_by('-date')

    # Method to get context data for the template
    def get_context_data(self, **kwargs):
        context = super(AllTransactionsView, self).get_context_data(**kwargs)

        # Add additional context data
        context['thirty_days_earlier'] = timezone.now() - timedelta(days=30)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
        context["total_trans_queried_amount"] = self.request.session.pop('total_trans_queried_amount', None)
        context["search_query"] = self.request.session.pop('search_query', None)

        return context

    # Method to handle POST requests
    def post(self, request, *args, **kwargs):
        # Get transaction ID and search query from POST data
        search_query = request.POST.get('search')

        if search_query:
            # If search query is provided, store it in session
            self.request.session['search_query'] = search_query

        else:
            # If filter category, order by, and sort order are provided, store them in session
            request.session['filter_category'] = request.POST.get('filter_category')
            request.session['order_by'] = request.POST.get('order_by')
            request.session['sort_order'] = request.POST.get('sort_order')

        # Redirect to the all_transactions_page
        return HttpResponseRedirect(reverse('all_transactions_page'))


def update_budget(budget_obj, object_obj, form_instance):
    for field in budget_obj:

        if object_obj > form_instance.amount:
            field.amount += object_obj - form_instance.amount
            field.spent -= object_obj - form_instance.amount

        elif object_obj < form_instance.amount:
            field.amount -= form_instance.amount - object_obj
            field.spent += form_instance.amount - object_obj

        field.save()


class AllTransactionUpdateAndDeletePage(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'expenses_tracker/add_transaction.html'
    success_url = "/all_transactions"

    def get_context_data(self, **kwargs):
        context = super(AllTransactionUpdateAndDeletePage, self).get_context_data(**kwargs)
        self.request.session['object_amount'] = float(self.object.amount)
        context['update'] = True
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        context['object'] = self.object.id
        context['header_name'] = 'Update Transaction'
        return context

    def form_valid(self, form):
        budget = Budget.objects.all().filter(user_id=self.request.user.id, date__lte=self.object.date)
        budget_cate = budget.filter(category=self.object.category)
        budget_all = budget.filter(category='All Transactions')
        object_amount = self.request.session.get('object_amount')

        update_budget(budget_obj=budget_cate, object_obj=object_amount, form_instance=form.instance)

        if form.instance.is_all_trans_bud:
            update_budget(budget_obj=budget_all, object_obj=object_amount, form_instance=form.instance)

        if object_amount is not None:
            self.request.session.pop('object_amount')

        if form.instance.recurring_transaction is False:
            form.instance.next_occurrence = None

        return super(AllTransactionUpdateAndDeletePage, self).form_valid(form)


def budget_calculation(budget_objs, transaction_obj):
    # Iterate over each budget object
    for field in budget_objs.all():
        # Check if the current budget amount is greater than the current spent amount
        if field.budget > field.amount:
            # Increment the amount by the transaction amount
            field.amount += transaction_obj.amount

            # Decrement the spent amount by the transaction amount
            field.spent -= transaction_obj.amount

            # Save the changes to the budget object
            field.save()


@login_required
def delete_transaction(request, pk):
    transaction_obj = Transaction.objects.get(id=pk)

    # If transaction ID is provided, delete the transaction and recalculate budgets

    budget_objects = Budget.objects.all().filter(user_id=request.user.id)
    budget_objects_categories = budget_objects.filter(category=transaction_obj.category).filter(
        date__lte=transaction_obj.date)

    all_transactions_budget = budget_objects.filter(
        category="All Transactions").filter(date__lte=transaction_obj.date)

    budget_calculation(budget_objs=budget_objects_categories, transaction_obj=transaction_obj)

    if transaction_obj.is_all_trans_bud:
        budget_calculation(budget_objs=all_transactions_budget, transaction_obj=transaction_obj)

    transaction_obj.delete()
    return HttpResponseRedirect(reverse('all_transactions_page'))


def budget_calc(field, form_instance):
    # Deduct the amount from the budget field
    field.amount -= form_instance.amount

    # Update the spent amount based on the new budget amount
    field.spent = field.budget - field.amount

    # Save the changes to the budget field
    field.save()


# @method_decorator(cache_page(60 * 30), name='dispatch')
class AddTransactionView(LoginRequiredMixin, CreateView):
    template_name = 'expenses_tracker/add_transaction.html'
    model = Transaction
    form_class = TransactionForm
    success_url = "/all_transactions"
    context_object_name = 'transactions'

    def form_valid(self, form):
        # Get the value of 'all_transaction_budget' from the POST data

        # Set the user_id and is_all_trans_bud fields of the form instance
        form.instance.user_id = self.request.user.id

        # Iterate over budget objects
        for field in Budget.objects.all().filter(user_id=self.request.user.id):
            # Check if 'all_transaction_budget' is True
            if form.instance.is_all_trans_bud:
                # If category is 'All Transactions', perform budget calculation
                if field.category == 'All Transactions':
                    budget_calc(field=field, form_instance=form.instance)

            # Check if category matches the form instance category
            if field.category == form.instance.category:
                # Perform budget calculation
                budget_calc(field=field, form_instance=form.instance)

        return super(AddTransactionView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AddTransactionView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        context['header_name'] = 'Add Transaction'
        return context


@method_decorator(cache_page(60 * 10), name='dispatch')
class CategoryView(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/categories.html'
    model = Transaction
    context_object_name = 'categories'

    def get_queryset(self):
        # Get all transactions for the logged-in user
        db = super(CategoryView, self).get_queryset().filter(user_id=self.request.user.id)

        # Aggregate the sum of amounts for each category
        return {field.category: db.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in db.order_by("-date")}

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        context['categories_pace_holder'] = 'transaction categories'
        context['transaction_income_pace_holder'] = 'transaction'
        return context


class RecurringTransactions(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/recurring-transactions.html'
    model = Transaction
    context_object_name = 'recurring_transactions_incomes'

    def get_queryset(self):
        # Get filter category and sort order from session
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')

        # Get all recurring transactions for the logged-in user
        data = (super(RecurringTransactions, self).get_queryset().filter(
            user_id=self.request.user.id).filter(recurring_transaction=True))

        # Update date for recurring transactions if next occurrence has passed
        for recurring_transaction in data.all():
            if timezone.now() > recurring_transaction.next_occurrence:

                # Creat new transaction, with same details if it's in the past

                Transaction.objects.create(
                    category=recurring_transaction.category,
                    amount=recurring_transaction.amount,
                    description=recurring_transaction.description,
                    recurring_transaction=recurring_transaction.recurring_transaction,
                    frequency=recurring_transaction.frequency,
                    transaction_title=recurring_transaction.transaction_title,
                    next_occurrence=recurring_transaction.next_occurrence,
                    is_all_trans_bud=recurring_transaction.is_all_trans_bud,
                    user=recurring_transaction.user,
                )

        if filter_category:
            # Apply filtering based on category if filter category is provided
            return expenses_query_filter_func(
                sort_order=sort_order,
                filter_category=self.request.session.pop('filter_category'),
                order_by=self.request.session.pop('order_by'), query_db=data,
                sort_pop=self.request.session.pop('sort_order')
            )

        # Return recurring transactions ordered by next occurrence date
        return data.order_by('next_occurrence')

    def get_context_data(self, **kwargs):
        context = super(RecurringTransactions, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
        context['thirty_days_later'] = timezone.now() + timedelta(days=30)
        return context

    def post(self, request, *args, **kwargs):
        # Get transaction ID from POST data
        transaction_id = request.POST.get('recurring_transaction_id')
        if transaction_id:
            # If transaction ID is provided, update recurring transaction attributes
            transaction_obj = Transaction.objects.get(id=transaction_id)
            transaction_obj.recurring_transaction = False
            transaction_obj.frequency = None
            transaction_obj.transaction_title = None
            transaction_obj.next_occurrence = None
            transaction_obj.save()
        else:
            # If filter category, order by, and sort order are provided, store them in session
            request.session['filter_category'] = request.POST.get('filter_category')
            request.session['order_by'] = request.POST.get('order_by')
            request.session['sort_order'] = request.POST.get('sort_order')

        return HttpResponseRedirect(reverse('recurring_transactions_page'))


class BudgetOverviewView(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/budget-overview.html'
    model = Budget
    context_object_name = 'budget'

    def get_queryset(self):
        # Get filter category and sort order from session
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')

        # Get all budgets for the logged-in user
        db = super(BudgetOverviewView, self).get_queryset().filter(user_id=self.request.user.id)

        # Delete budgets if spent exceeds budget or expiration date has passed
        for field in db:
            if field.spent >= field.budget or timezone.now() > field.expiration_date:
                field.delete()

        if filter_category:
            # Apply filtering based on category if filter category is provided
            return expenses_query_filter_func(sort_order=sort_order,
                                              filter_category=self.request.session.pop('filter_category'),
                                              order_by=self.request.session.pop('order_by'), query_db=db,
                                              sort_pop=self.request.session.pop('sort_order'))

        # Return budgets ordered by expiration date
        return db.order_by('expiration_date')

    def get_context_data(self, **kwargs):
        context = super(BudgetOverviewView, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['thirty_days_later'] = timezone.now() + timedelta(days=30)
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
        return context

    def post(self, request, *args, **kwargs):
        # Get budget ID from POST data
        budget_id = request.POST.get('budget_overview_id')

        if budget_id:
            # If budget ID is provided, delete the budget
            Budget.objects.get(id=budget_id).delete()
        else:
            # If filter category, order by, and sort order are provided, store them in session
            request.session['filter_category'] = request.POST.get('filter_category')
            request.session['order_by'] = request.POST.get('order_by')
            request.session['sort_order'] = request.POST.get('sort_order')

        # Redirect to the budget-overview_page
        return HttpResponseRedirect(reverse('budget-overview_page'))


@method_decorator(cache_page(60 * 30), name='dispatch')
class AddBudgetView(LoginRequiredMixin, CreateView):
    template_name = 'expenses_tracker/add_budget.html'
    model = Budget
    form_class = BudgetForm
    success_url = '/budget-overview'

    def form_valid(self, form):
        # Set the budget amount and user ID
        form.instance.budget = float(form.cleaned_data.get('amount'))
        form.instance.user_id = self.request.user.id
        return super(AddBudgetView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AddBudgetView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        return context


def expenses_report_decorator(func):
    # Define a decorator function that checks if start_date is set in the session
    @wraps(func)
    def decorated_function(request, *args, **kwargs):
        # Check if start_date is not set in the session
        if not request.session.get('start_date'):
            # If start_date is not set, redirect to '/expense-reports-form'
            return HttpResponseRedirect('/expense-reports-form')

        # If start_date is set, call the original function with its arguments
        return func(request, *args, **kwargs)

    # Return the decorated function
    return decorated_function


@expenses_report_decorator
@login_required
def expenses_report(request, *args, **kwargs):
    from .pdf import convert_html_to_pdf
    is_expense_report = True

    # Get user details and user currency from session
    user = User.objects.get(id=request.user.id)
    user_currency = request.session.get('user_currency')

    # Pop session variables
    start_date = request.session.pop('start_date')
    end_date = request.session.pop('end_date')
    purpose = request.session.pop('purpose')
    note = request.session.pop('note')

    # Prepare context dictionary
    context = {
        'first_name': user.profile.first_name,
        'last_name': user.profile.last_name,
        'occupation': user.profile.occupation,
        'email': user.email,
        'start_date': start_date,
        'end_date': end_date,
        'purpose': purpose,
        'note': note,
        'user_currency': user_currency,
    }

    # Check if request is from income report
    request_from_income_report = request.session.pop("request_from_income_report", default=None)

    if request_from_income_report:
        # If request is from income report

        # Get income data for the specified date range
        income_data = Income.objects.filter(user_id=user.id).filter(date__date__gte=start_date,
                                                                    date__date__lte=end_date).order_by('date')
        # Calculate total income
        income_data_sum_total = income_data.aggregate(amount=Sum('amount'))

        # Calculate income by source category
        source = {field.category: income_data.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in income_data}

        # Update context with income data
        context["source"] = source
        context["income_data_sum_total"] = income_data_sum_total['amount']
        context["income_data"] = income_data

        # Render HTML template for income report
        html_content = render_to_string('expenses_tracker/income-report.html', context)
        is_expense_report = False

    else:
        # If request is from expense report

        # Get transaction data for the specified date range
        reports_transaction = Transaction.objects.filter(
            user_id=user.id).filter(date__date__gte=start_date, date__date__lte=end_date).order_by('date')

        # Calculate total transactions amount
        transactions_sum_total = reports_transaction.aggregate(amount=Sum('amount'))

        # Calculate expenses by category
        category = {field.category: reports_transaction.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in reports_transaction}

        # Update context with expense data
        context["category"] = category
        context["transactions_sum_total"] = transactions_sum_total['amount']
        context["transactions"] = reports_transaction

        # Render HTML template for expenses report
        html_content = render_to_string('expenses_tracker/expenses-report.html', context)

    # Convert HTML content to PDF
    pdf_response = convert_html_to_pdf(source_html=html_content, is_expense_report=is_expense_report)

    # Return the PDF response
    return pdf_response


# @cache_page(60 * 30)
@login_required
def expense_income_report_form(request):
    error = None
    if request.method == 'POST':
        # If the request method is POST, process the form
        form = ExpenseIncomeReportForm(request.POST or None)

        if form.is_valid():
            # If the form is valid, store form data in session
            for key, value in form.cleaned_data.items():
                if key != 'csrfmiddlewaretoken':
                    if key == 'start_date' or key == 'end_date':
                        # Serialize date objects to string
                        serialized_date = value.isoformat()
                        request.session[key] = serialized_date
                    else:
                        request.session[key] = value
            request.session["request_from_income_report"] = request.POST.get('income_data')
            return HttpResponseRedirect(reverse('expenses_report_page'))
        else:
            error = form.errors

    # Render the form template with appropriate context
    return render(
        request,
        template_name='expenses_tracker/expenses_incomes_report_form.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'errors': error,
                 'current_year': datetime.now().year}
    )


class IncomeData(LoginRequiredMixin, ListView):
    # View to display income data
    model = Income
    template_name = 'expenses_tracker/income_data.html'
    context_object_name = 'income_data'
    paginate_by = 50

    def get_paginate_by(self, queryset):
        # paginate = self.request.GET.get('paginate', 'yes')
        search_query = self.request.session.get('search_query')
        if search_query:
            return None   # Disable pagination
        return self.paginate_by  # Use default pagination

    def get_context_data(self, **kwargs):
        # Get context data for rendering the template
        context = super(IncomeData, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Source"
        context['thirty_days_earlier'] = timezone.now() - timedelta(days=30)
        context['total_trans_queried_amount'] = self.request.session.pop('total_trans_queried_amount', None)
        context["search_query"] = self.request.session.pop('search_query', None)
        return context

    def get_queryset(self):
        # Get the queryset based on filtering and search
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')
        search_query = self.request.session.get('search_query')

        data = (super(IncomeData, self).get_queryset().filter(user_id=self.request.user.id))

        if filter_category:
            # Filter the queryset based on category
            filtered_query = expenses_query_filter_func(
                sort_order=sort_order,
                filter_category=self.request.session.pop('filter_category'),
                order_by=self.request.session.pop('order_by'), query_db=data,
                sort_pop=self.request.session.pop('sort_order')
            )

            total_trans_queried_amount = filtered_query.aggregate(amount=Sum('amount'))

            self.request.session['total_trans_queried_amount'] = total_trans_queried_amount['amount']

            return filtered_query

        elif search_query:
            # Filter the queryset based on search query
            filtered_query = data.filter(notes__icontains=search_query)
            total_trans_queried_amount = filtered_query.aggregate(amount=Sum('amount'))
            self.request.session['total_trans_queried_amount'] = total_trans_queried_amount['amount']

            return filtered_query.order_by('date')

        return data.order_by('-date')

    def post(self, request, *args, **kwargs):
        # Handle POST request for deleting or searching income data
        search_query = request.POST.get('search')

        if search_query:
            # If search query is provided, store it in session
            self.request.session['search_query'] = search_query
        else:
            # Otherwise, store filter options in session
            request.session['filter_category'] = request.POST.get('filter_category')
            request.session['order_by'] = request.POST.get('order_by')
            request.session['sort_order'] = request.POST.get('sort_order')

        return HttpResponseRedirect(reverse('income_data_page'))


class AllIncomeUpdateAndDeletePage(LoginRequiredMixin, UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'expenses_tracker/add_income.html'
    success_url = "/income-data"

    def get_context_data(self, **kwargs):
        context = super(AllIncomeUpdateAndDeletePage, self).get_context_data(**kwargs)
        context['update'] = True
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        context['object'] = self.object.id
        context['header_name'] = 'Update Income'
        return context

    def form_valid(self, form):
        if form.instance.recurring_transaction is False:
            form.instance.next_occurrence = None

        return super(AllIncomeUpdateAndDeletePage, self).form_valid(form)


@login_required
def delete_income(request, pk):
    Income.objects.get(id=pk).delete()
    return HttpResponseRedirect(reverse('income_data_page'))


# @method_decorator(cache_page(60 * 30), name='dispatch')
class IncomeFormView(LoginRequiredMixin, CreateView):
    # View for adding income
    model = Income
    template_name = 'expenses_tracker/add_income.html'
    form_class = IncomeForm
    success_url = '/income-data'

    def form_valid(self, form):
        # Ensure user ID is set before saving the form
        form.instance.user_id = self.request.user.id
        return super(IncomeFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Get context data for rendering the template
        context = super(IncomeFormView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        context['header_name'] = 'Add Income'
        return context


@method_decorator(cache_page(60 * 10), name='dispatch')
class IncomeCategoryView(LoginRequiredMixin, ListView):
    # View for displaying income categories
    model = Income
    template_name = 'expenses_tracker/categories.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Get queryset for income categories
        db = super(IncomeCategoryView, self).get_queryset().filter(user_id=self.request.user.id)

        return {field.category: db.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in db.order_by("-date")}

    def get_context_data(self, **kwargs):
        # Get context data for rendering the template
        context = super(IncomeCategoryView, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        context['categories_pace_holder'] = 'income categories'
        context['transaction_income_pace_holder'] = 'income'
        return context


class RecurringIncomes(LoginRequiredMixin, ListView):
    # View for displaying recurring incomes
    template_name = 'expenses_tracker/income-recur.html'
    model = Income
    context_object_name = 'recurring_transactions_incomes'

    def get_queryset(self):
        # Get queryset for recurring incomes
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')

        data = (super(RecurringIncomes, self).get_queryset().filter(
            user_id=self.request.user.id).filter(recurring_transaction=True))

        for recurring_income in data.all():
            if timezone.now() > recurring_income.next_occurrence:
                # Creat new transaction, with same details if it's in the past
                Income.objects.create(
                    category=recurring_income.category,
                    amount=recurring_income.amount,
                    description=recurring_income.description,
                    recurring_transaction=recurring_income.recurring_transaction,
                    frequency=recurring_income.frequency,
                    transaction_title=recurring_income.transaction_title,
                    next_occurrence=recurring_income.next_occurrence,
                    is_all_trans_bud=recurring_income.is_all_trans_bud,
                    user=recurring_income.user,
                )

        if filter_category:
            # Filter queryset based on category
            return expenses_query_filter_func(
                sort_order=sort_order,
                filter_category=self.request.session.pop('filter_category'),
                order_by=self.request.session.pop('order_by'), query_db=data,
                sort_pop=self.request.session.pop('sort_order')
            )

        return data.order_by('next_occurrence')

    def get_context_data(self, **kwargs):
        # Get context data for rendering the template
        context = super(RecurringIncomes, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
        context['thirty_days_later'] = timezone.now() + timedelta(days=30)
        return context

    def post(self, request, *args, **kwargs):
        # Handle POST requests for deleting or filtering recurring incomes
        income_id = request.POST.get('recurring_transaction_id')
        if income_id:
            # If income ID is provided, update the income record
            transaction_obj = Income.objects.get(id=income_id)
            transaction_obj.recurring_transaction = False
            transaction_obj.frequency = None
            transaction_obj.transaction_title = None
            transaction_obj.next_occurrence = None
            transaction_obj.save()
        else:
            # Otherwise, store filter options in session
            request.session['filter_category'] = request.POST.get('filter_category')
            request.session['order_by'] = request.POST.get('order_by')
            request.session['sort_order'] = request.POST.get('sort_order')

        return HttpResponseRedirect(reverse('recurring_income_page'))


@cache_page(60 * 3)
@login_required
def profile_details(request):
    # Get the profile associated with the current user
    profile = Profile.objects.get(user=request.user)

    # If the profile image is missing, set a default image
    if not profile.image:
        profile.image = 'images/c0749b7cc401421662ae901ec8f9f660.jpg'
        profile.save()

    # Render the profile details template with the profile information
    return render(
        request,
        template_name='expenses_tracker/profile.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'profile': profile,
                 'current_year': datetime.now().year}
    )


@cache_page(60 * 30)
@login_required
def notification(request):
    current_datetime = timezone.now()

    # Calculate datetime 24 hours from now
    next_24_hours = current_datetime + timedelta(hours=24)

    # Query your model for instances where the date is within the next 24 hours
    transactions_instances_next_24_hours = Transaction.objects.filter(
        next_occurrence__gt=current_datetime, next_occurrence__lte=next_24_hours
    ).order_by('next_occurrence')

    incomes_instances_next_24_hours = Income.objects.filter(
        next_occurrence__gt=current_datetime, next_occurrence__lte=next_24_hours
    ).order_by('next_occurrence')

    budgets_instances_next_24_hours = Budget.objects.filter(
        expiration_date__gt=current_datetime, expiration_date__lte=next_24_hours
    ).order_by('expiration_date')

    # Render the notification template with instances due in the next 24 hours
    return render(
        request,
        template_name='expenses_tracker/notification.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'current_year': datetime.now().year,
                 'transactions_instances_next_24_hours': transactions_instances_next_24_hours,
                 'user_currency': request.session.get('user_currency'),
                 'incomes_instances_next_24_hours': incomes_instances_next_24_hours,
                 'budgets_instances_next_24_hours': budgets_instances_next_24_hours,
                 }
    )


class AccountSettingsView(LoginRequiredMixin, View):
    template_name = 'expenses_tracker/account_settings.html'

    def get(self, request, *args, **kwargs):
        # Retrieve any profile update messages stored in session
        try:
            profile_updated = request.session.pop('message')
        except KeyError:
            profile_updated = None

        # Retrieve the profile associated with the current user
        profile = Profile.objects.get(user_id=request.user.id)

        # Initialize profile form with current profile data
        profile_form = ProfileForm(
            initial={'currency': profile.currency,
                     'first_name': profile.first_name,
                     'last_name': profile.last_name,
                     'occupation': profile.occupation,
                     'city': profile.city,
                     'country': profile.country,
                     'phone_number': profile.phone_number
                     }
        )

        # Render the account settings page with the profile form and other context data
        return render(
            request, self.template_name,
            context={'form': profile_form,
                     'user_status': request.user.is_authenticated,
                     'profile_updated': profile_updated,
                     'current_year': datetime.now().year}
        )

    def post(self, request, *args, **kwargs):
        # Retrieve the profile associated with the current user
        profile = Profile.objects.get(user_id=request.user.id)

        # Initialize profile form with POST data and current profile instance
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            # Update user currency in session
            self.request.session['user_currency'] = profile_form.instance.currency

            # Save the updated profile
            profile_form.save()

            # Set success message in session
            request.session['message'] = 'Profile updated successfully'

            # Redirect to account settings page
            return HttpResponseRedirect(reverse('account_settings_page'))

        # If form is invalid, render account settings page with form and other context data
        return render(
            request, self.template_name,
            context={'user_status': request.user.is_authenticated,
                     'form': profile_form,
                     'current_year': datetime.now().year,
                     }
        )


class RegisterView(View):

    def get(self, request):
        password_not_confirm = None
        # Initialize user and profile forms
        form = ProfileForm()
        user_form = UserForm(request.POST or None)
        fields_to_display = ['Currency']

        # Render signup page with forms and other context data
        return render(
            request, template_name='expenses_tracker/signup.html',
            context={
                "form": form,
                "password_not_confirm": password_not_confirm,
                "fields_to_display": fields_to_display,
                'user_status': request.user.is_authenticated,
                'user_form': user_form,
            }
        )

    def post(self, request):
        # Initialize user and profile forms with POST data
        user_form = UserForm(request.POST or None)
        form = ProfileForm(request.POST or None)

        fields_to_display = ['Currency']

        if form.is_valid() and user_form.is_valid():
            user_form.save(commit=False)

            # Set password for user
            user_form.instance.set_password(user_form.cleaned_data['password'])

            # Link profile to user and set default image
            form.instance.user = user_form.instance
            form.instance.image = 'images/c0749b7cc401421662ae901ec8f9f660.jpg'

            # Store user currency in session
            self.request.session['user_currency'] = form.instance.currency

            # Save user and profile forms
            user_form.save()
            form.save()

            # Set login message in session
            request.session['login_msg'] = f"Now login as - {user_form.instance.username}"

            return HttpResponseRedirect(reverse('login_page'))

        # If forms are invalid, render signup page with forms and other context data
        return render(request, template_name="expenses_tracker/signup.html",
                      context={"form": form,
                               'fields_to_display': fields_to_display,
                               'user_status': request.user.is_authenticated,
                               'current_year': datetime.now().year,
                               'user_form': user_form,
                               }
                      )


def login_user(request):
    error_message = None
    login_form = LoginForm(request.POST or None)

    redirect_ = request.GET.get('next', '')

    if request.method == 'POST':
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                # Store the current user ID in session
                request.session["current_user"] = user.id

                # Store the user's currency in session
                request.session['user_currency'] = user.profile.currency

                # Log in the user
                login(request, user)

                # Redirect to the next parameter if it exists, otherwise redirect to the default URL
                if redirect_:
                    allow_hosts = settings.ALLOWED_HOSTS
                    redirect_to = url_has_allowed_host_and_scheme_func(redirect=redirect_, allowed_hosts=allow_hosts)

                    if redirect_to:
                        return HttpResponseRedirect(redirect_to)

                return HttpResponseRedirect(reverse('home'))

            else:
                error_message = "Username or password is incorrect"

    return render(
        request,
        template_name='expenses_tracker/login.html',
        status=200,
        context={
            "error_message": error_message,
            'user_status': request.user.is_authenticated,
            'current_year': datetime.now().year,
            'next': redirect_,
            'login_msg': request.session.pop('login_msg', None),
            'login_form': login_form
        }
    )


@login_required
def logout_user(request):
    # Delete the session data and log out the user
    request.session.delete()
    logout(request)
    return HttpResponseRedirect(reverse('login_page'))


@cache_page(60 * 30)
def privacy_policy(request):
    # Render the privacy policy page
    return render(
        request,
        template_name='expenses_tracker/privacy_policy.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'current_year': datetime.now().year}
    )


@cache_page(60 * 30)
def terms_of_service(request):
    # Render the terms of service page
    return render(
        request,
        template_name='expenses_tracker/terms_of_service.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'current_year': datetime.now().year}
    )


def contact_us(request):
    """
    Handle the contact form submission.

    If the request method is POST, extract form data and send a message.
    Display a confirmation message on successful submission.

    Returns:
        str: Rendered HTML template.
    """

    # Check if a message has been sent successfully
    is_message_sent = request.session.pop('is_message_sent', False)
    validation_error = None

    # Create a ContactForm instance
    form = ContactForm(request.POST or None)

    if form.is_valid():
        try:
            # Validate the form data
            ContactForm.clean_your_field(form)
        except ValidationError:
            # Handle validation errors
            validation_error = ("Message or Name: Please refrain from using Non-ASCII characters such as 😁 and "
                                "others. Kindly write your message without emojis or symbols.")
        else:
            # Extract form data
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email")
            phone = form.cleaned_data.get("phone")
            message = form.cleaned_data.get("message")

            # Send the message
            send_message(name, email, phone, message)

            # Set a flag to indicate that the message has been sent
            request.session['is_message_sent'] = True
            # Redirect to the contact us page to avoid form resubmission
            return HttpResponseRedirect(reverse('contact_us_page'))

    # Render the contact form template for GET requests
    return render(
        request,
        template_name='expenses_tracker/contact_us.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'is_message_sent': is_message_sent,
                 'form': form,
                 'error_message': validation_error,
                 'current_year': datetime.now().year}
    )


@cache_page(60 * 30)
@login_required
def line_chart(request):
    timeframe = ""
    timeframe_inc = ""
    seven_days_earlier = timezone.now() - timedelta(days=6)

    transaction_inst = Transaction.objects.all().filter(user=request.user)
    income_inst = Income.objects.all().filter(user=request.user)

    # Create a DateForm instance
    date_form = DateForm(request.POST or None)

    if date_form.is_valid():
        # Extract start and end dates from the form
        start_date = date_form.cleaned_data.get('start')
        end_date = date_form.cleaned_data.get('end')

        # Filter transactions by date range
        transaction = transaction_inst.filter(date__date__gte=start_date,
                                              date__date__lte=end_date)

        # Toggle income visualization based on user input
        if request.POST.get('toggle_state') == 'True':
            income = income_inst.filter(date__date__gte=start_date,
                                        date__date__lte=end_date)
        else:
            income = income_inst
            timeframe_inc = '(All Time)'
    else:
        # If form is not valid, show all transactions and incomes
        transaction = transaction_inst.filter(date__date__gte=seven_days_earlier)
        income = income_inst.filter(date__date__gte=seven_days_earlier)

        timeframe = '(1 Week)'
        timeframe_inc = '(1 Week)'

    # Calculate the total sum of all transactions
    transactions_sum_total = transaction.aggregate(amount=Sum('amount'))
    incomes_sum_total = income.aggregate(amount=Sum('amount'))

    transactions_total = transactions_sum_total['amount']
    incomes_total = incomes_sum_total['amount']

    if transactions_sum_total['amount'] is None:
        transaction = transaction_inst
        transactions_total = transaction.aggregate(amount=Sum('amount'))
        transactions_total = transactions_total['amount']
        timeframe = '(All Time)'

        if transactions_total is None:
            transactions_total = '-- no transaction data --'

    if incomes_sum_total['amount'] is None:
        income = income_inst
        incomes_total = income.aggregate(amount=Sum('amount'))
        incomes_total = incomes_total['amount']
        timeframe_inc = '(All Time)'

        if incomes_total is None:
            incomes_total = '-- no income data --'

    chart = linechart(
        request_obj=request, object_inst=transaction, obj_name='Transaction', timeframe=timeframe,
        total=transactions_total
    )
    chart2 = linechart(
        request_obj=request, object_inst=income, obj_name='Income', timeframe=timeframe_inc,
        total=incomes_total
    )

    # Prepare context data for rendering the template
    context = {'chart': chart,
               'chart2': chart2,
               'form': date_form,
               'user_status': request.user.is_authenticated,
               'chart_name': 'Line Chart',
               'url_name': 'line_chart_page',
               'current_year': datetime.now().year,
               }

    # Render the line chart template
    return render(request, 'expenses_tracker/line_chart.html', context)


def aggregate_calc(instance):
    return {field.category: instance.filter(category=field.category).aggregate(
        sum=Sum('amount')).get('sum') for field in instance}


@cache_page(60 * 30)
@login_required
def bar_chart(request):
    timeframe = ""
    timeframe_inc = ""
    seven_days_earlier = timezone.now() - timedelta(days=6)

    transaction_inst = Transaction.objects.all().filter(user=request.user)
    income_inst = Income.objects.all().filter(user=request.user)

    # Create a DateForm instance
    date_form = DateForm(request.POST or None)

    if date_form.is_valid():
        # Extract start and end dates from the form
        start_date = date_form.cleaned_data.get('start')
        end_date = date_form.cleaned_data.get('end')

        # Filter transactions by date range
        transaction = transaction_inst.filter(date__date__gte=start_date,
                                              date__date__lte=end_date)

        # Toggle income visualization based on user input
        if request.POST.get('toggle_state') == 'True':
            income = income_inst.filter(date__date__gte=start_date,
                                        date__date__lte=end_date)
        else:
            income = income_inst
            timeframe_inc = '(All Time)'
    else:

        # If form is not valid, show all transactions and incomes
        transaction = transaction_inst.filter(date__date__gte=seven_days_earlier)
        income = income_inst.filter(date__date__gte=seven_days_earlier)

        timeframe = '(1 Week)'
        timeframe_inc = '(1 Week)'

    # Calculate the total sum of all transactions
    transactions_sum_total = transaction.aggregate(amount=Sum('amount'))
    incomes_sum_total = income.aggregate(amount=Sum('amount'))

    transactions_total = transactions_sum_total['amount']
    incomes_total = incomes_sum_total['amount']

    if transactions_sum_total['amount'] is None:
        transaction = transaction_inst
        transactions_total = transaction.aggregate(amount=Sum('amount'))
        transactions_total = transactions_total['amount']
        timeframe = '(All Time)'

        if transactions_total is None:
            transactions_total = '-- no transaction data --'

    if incomes_sum_total['amount'] is None:
        income = income_inst
        incomes_total = income.aggregate(amount=Sum('amount'))
        incomes_total = incomes_total['amount']
        timeframe_inc = '(All Time)'

        if incomes_total is None:
            incomes_total = '-- no income data --'

    category_trans = aggregate_calc(transaction)

    category_income = aggregate_calc(income)

    chart = barchart(
        request_obj=request, object_inst=category_trans, obj_name='Transactions Categories', timeframe=timeframe,
        total=transactions_total
    )
    chart2 = barchart(
        request_obj=request, object_inst=category_income, obj_name='Incomes Sources', timeframe=timeframe_inc,
        total=incomes_total
    )

    context = {'chart': chart,
               'chart2': chart2,
               'form': date_form,
               'user_status': request.user.is_authenticated,
               'chart_name': 'Bar Chart',
               'url_name': 'bar_chart_page',
               'current_year': datetime.now().year,
               }

    return render(request, 'expenses_tracker/line_chart.html', context)


@cache_page(60 * 30)
@login_required
def exchange_rate(request):
    return render(
        request,
        template_name='expenses_tracker/exchange_rate.html',
        context={
            'current_year': datetime.now().year,
            'user_status': request.user.is_authenticated,
        },
        status=200
    )
