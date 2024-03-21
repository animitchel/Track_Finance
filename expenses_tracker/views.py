import logging
import os

from functools import wraps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.db.models import Count, Sum, Avg

from .form_models import ProfileForm, TransactionForm, BudgetForm, IncomeForm
from django.views import View
from datetime import datetime, timedelta
from .models import Transaction, Budget, Profile, Income
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.template.loader import render_to_string, get_template
from django.utils import timezone

from .filter_func import expenses_query_filter_func


class IndexView(TemplateView):
    template_name = 'expenses_tracker/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        return context


@login_required
def overview(request):
    transactions = Transaction.objects.all().filter(user_id=request.user.id)

    category_transactions = transactions.order_by('-date')[:3]
    transactions_sum_total = transactions.aggregate(amount=Sum('amount'))

    category = {field.category: transactions.filter(category=field.category).aggregate(
        sum=Sum('amount')).get('sum') for field in category_transactions}

    recent_transactions = category_transactions
    recurring_transaction = transactions.filter(recurring_transaction=True).order_by('next_occurrence')[:3]

    budget = Budget.objects.all().filter(user_id=request.user.id)
    budget_sum_total = budget.aggregate(budget=Sum('budget'))
    budget_remaining_total = budget.aggregate(amount=Sum('amount'))

    all_budget = budget.order_by('expiration_date')[:3]

    date_now = timezone.now()

    # print(request.session.get('current_user'))
    user_currency = request.session.get('user_currency')

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
                 'user_currency': user_currency
                 }
    )


def budget_calculation(budget_objs, transaction_obj):
    for field in budget_objs.all():
        if field.budget > field.amount:
            field.amount += transaction_obj.amount
            field.spent -= transaction_obj.amount
            field.save()


class AllTransactionsView(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/all_transactions.html'
    model = Transaction
    context_object_name = 'transactions'

    def get_queryset(self):

        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')

        query = super(AllTransactionsView, self).get_queryset().filter(user_id=self.request.user.id).order_by('-date')

        if filter_category:
            return expenses_query_filter_func(sort_order=sort_order,
                                              filter_category=self.request.session.pop('filter_category'),
                                              order_by=self.request.session.pop('order_by'), query_db=query,
                                              sort_pop=self.request.session.pop('sort_order'))

        return query

    def get_context_data(self, **kwargs):
        context = super(AllTransactionsView, self).get_context_data(**kwargs)
        context['date_now'] = timezone.now()
        context['user_currency'] = self.request.session.get('user_currency')
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        return context

    def post(self, request, *args, **kwargs):
        transaction_id = request.POST.get('all_transaction_id')
        if transaction_id:
            transaction_obj = Transaction.objects.get(id=transaction_id)

            budget_objects = Budget.objects.all().filter(user_id=self.request.user.id)
            budget_objects_categories = budget_objects.filter(category=transaction_obj.category).filter(
                date__lte=transaction_obj.date)

            all_transactions_budget = budget_objects.filter(category="All Transactions").filter(
                date__lte=transaction_obj.date)

            budget_calculation(budget_objs=budget_objects_categories, transaction_obj=transaction_obj)

            budget_calculation(budget_objs=all_transactions_budget, transaction_obj=transaction_obj)

            transaction_obj.delete()

        request.session['filter_category'] = request.POST.get('filter_category')
        request.session['order_by'] = request.POST.get('order_by')
        request.session['sort_order'] = request.POST.get('sort_order')

        return HttpResponseRedirect('/all_transactions')


def budget_calc(field, form_instance):
    field.amount -= form_instance.amount
    field.spent = field.budget - field.amount
    field.save()


class AddTransactionView(LoginRequiredMixin, CreateView):
    template_name = 'expenses_tracker/add_transaction.html'
    model = Transaction
    form_class = TransactionForm
    success_url = "/all_transactions"
    context_object_name = 'transactions'

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        for field in Budget.objects.all().filter(user_id=self.request.user.id):
            if field.category == 'All Transactions':
                budget_calc(field=field, form_instance=form.instance)

            elif field.category == form.instance.category:
                budget_calc(field=field, form_instance=form.instance)
        return super(AddTransactionView, self).form_valid(form)


class CategoryView(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/categories.html'
    model = Transaction
    context_object_name = 'categories'

    def get_queryset(self):
        db = super(CategoryView, self).get_queryset().filter(user_id=self.request.user.id)

        return {field.category: db.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in db.order_by("-date")}

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        return context

    def post(self, request, *args, **kwargs):
        request.session['order_by'] = request.POST.get('order_by')
        request.session['sort_order'] = request.POST.get('sort_order')

        return HttpResponseRedirect('/categories')


class RecurringTransactions(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/recurring-transactions.html'
    model = Transaction
    context_object_name = 'recurring_transactions'

    def get_queryset(self):
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')

        data = (super(RecurringTransactions, self).get_queryset().filter(
            user_id=self.request.user.id).filter(recurring_transaction=True))

        for recurring_transaction in data.all():
            if timezone.now() > recurring_transaction.next_occurrence:
                recurring_transaction.date = timezone.now()
                recurring_transaction.save()

        if filter_category:
            return expenses_query_filter_func(sort_order=sort_order,
                                              filter_category=self.request.session.pop('filter_category'),
                                              order_by=self.request.session.pop('order_by'), query_db=data,
                                              sort_pop=self.request.session.pop('sort_order'))
        return data.order_by('next_occurrence')

    def get_context_data(self, **kwargs):
        context = super(RecurringTransactions, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        return context

    def post(self, request, *args, **kwargs):
        transaction_id = request.POST.get('recurring_transaction_id')
        if transaction_id:
            transaction_obj = Transaction.objects.get(id=transaction_id)
            transaction_obj.recurring_transaction = False
            transaction_obj.frequency = None
            transaction_obj.transaction_title = None
            transaction_obj.next_occurrence = None
            transaction_obj.save()
        else:
            request.session['filter_category'] = request.POST.get('filter_category')
            request.session['order_by'] = request.POST.get('order_by')
            request.session['sort_order'] = request.POST.get('sort_order')
        return HttpResponseRedirect('/recurring-transactions')


class BudgetOverviewView(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/budget-overview.html'
    model = Budget
    context_object_name = 'budget'

    def get_queryset(self):
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')
        order_by = self.request.session.get('order_by')

        db = super(BudgetOverviewView, self).get_queryset().filter(user_id=self.request.user.id)
        for field in db:
            if field.spent >= field.budget or timezone.now() > field.expiration_date:
                field.delete()

        if filter_category:
            return expenses_query_filter_func(sort_order=sort_order,
                                              filter_category=self.request.session.pop('filter_category'),
                                              order_by=self.request.session.pop('order_by'), query_db=db,
                                              sort_pop=self.request.session.pop('sort_order'))

        return db.order_by('expiration_date')

    def get_context_data(self, **kwargs):
        context = super(BudgetOverviewView, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        return context

    def post(self, request, *args, **kwargs):
        budget_id = request.POST.get('budget_overview_id')

        if budget_id:
            Budget.objects.get(id=budget_id).delete()

        request.session['filter_category'] = request.POST.get('filter_category')
        request.session['order_by'] = request.POST.get('order_by')
        request.session['sort_order'] = request.POST.get('sort_order')
        return HttpResponseRedirect('/budget-overview')


class AddBudgetView(LoginRequiredMixin, CreateView):
    template_name = 'expenses_tracker/add_budget.html'
    model = Budget
    form_class = BudgetForm
    success_url = '/budget-overview'

    def form_valid(self, form):
        form.instance.budget = float(form.cleaned_data.get('amount'))
        form.instance.user_id = self.request.user.id
        return super(AddBudgetView, self).form_valid(form)


def expenses_report_decorator(func):
    @wraps(func)
    def decorated_function(request, *args, **kwargs):
        if not request.session.get('start_date'):
            return HttpResponseRedirect('/expense-reports-form')

        # If the condition is met, proceed to the wrapped function
        return func(request, *args, **kwargs)

    return decorated_function


@expenses_report_decorator
@login_required
def expenses_report(request):
    from .pdf import convert_html_to_pdf
    user = User.objects.get(id=request.user.id)
    user_currency = user.profile.currency

    start_date = request.session.pop('start_date')
    end_date = request.session.pop('end_date')
    purpose = request.session.pop('purpose')
    note = request.session.pop('note')

    reports_transaction = Transaction.objects.filter(
        user_id=user.id).filter(date__date__gte=start_date, date__date__lte=end_date)

    transactions_sum_total = reports_transaction.aggregate(amount=Sum('amount'))

    category = {field.category: reports_transaction.filter(category=field.category).aggregate(
        sum=Sum('amount')).get('sum') for field in reports_transaction}

    context = {
        'first_name': user.profile.first_name,
        'last_name': user.profile.last_name,
        'occupation': user.profile.occupation,
        'email': user.email,
        'start_date': start_date,
        'end_date': end_date,
        'user_status': request.user.is_authenticated,
        'transactions': reports_transaction,
        'purpose': purpose,
        'note': note,
        'user_currency': user_currency,
        'category': category,
        'transactions_sum_total': transactions_sum_total['amount']
    }

    html_content = render_to_string('expenses_tracker/expenses-report.html', context)

    pdf_response = convert_html_to_pdf(html_content)
    return pdf_response


@login_required
def income_report(request):
    return render(
        request,
        'expenses_tracker/income-report.html',
        status=200,
        context={'user_status': request.user.is_authenticated}
    )


@login_required
def expense_report_form(request):
    from expenses_tracker.form_models import ExpenseReportForm
    error = None
    if request.method == 'POST':
        form = ExpenseReportForm(request.POST or None)

        if form.is_valid():
            for key, value in form.cleaned_data.items():

                if key != 'csrfmiddlewaretoken':
                    if key == 'start_date' or key == 'end_date':
                        # Convert a date object to string
                        serialized_date = value.isoformat()
                        request.session[key] = serialized_date
                    else:
                        request.session[key] = value
            return HttpResponseRedirect('/expenses-report')
        else:
            error = form.errors

    return render(
        request,
        template_name='expenses_tracker/expenses_report_form.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'errors': error}
    )


class IncomeData(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'expenses_tracker/income_data.html'
    context_object_name = 'income_data'

    def get_context_data(self, **kwargs):
        context = super(IncomeData, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        # context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        return context


class IncomeFormView(LoginRequiredMixin, CreateView):
    model = Income
    template_name = 'expenses_tracker/add_income.html'
    form_class = IncomeForm
    success_url = '/income-data'

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super(IncomeFormView, self).form_valid(form)


@login_required
def profile_details(request):
    profile = Profile.objects.get(user=request.user)
    return render(
        request,
        template_name='expenses_tracker/profile.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'profile': profile}
    )


@login_required
def notification(request):
    return render(
        request,
        template_name='expenses_tracker/notification.html',
        status=200,
        context={'user_status': request.user.is_authenticated}
    )


class AccountSettingsView(LoginRequiredMixin, View):
    template_name = 'expenses_tracker/account_settings.html'

    def get(self, request, *args, **kwargs):

        try:
            profile_updated = request.session.pop('message')
        except KeyError:
            profile_updated = None

        profile = Profile.objects.get(user_id=request.user.id)

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

        return render(
            request, self.template_name,
            context={'form': profile_form,
                     'user_status': request.user.is_authenticated,
                     'profile_updated': profile_updated}
        )

    def post(self, request, *args, **kwargs):

        profile = Profile.objects.get(user_id=request.user.id)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            self.request.session['user_currency'] = profile_form.instance.currency

            profile_form.save()

            request.session['message'] = 'Profile updated successfully'

            return HttpResponseRedirect('/account-settings')

        return render(
            request, self.template_name,
            context={'user_status': request.user.is_authenticated,
                     'form': profile_form}
        )


class RegisterView(View):

    def get(self, request):
        password_not_confirm = None
        form = ProfileForm()
        fields_to_display = ['Currency']

        return render(
            request, template_name='expenses_tracker/signup.html',
            context={
                "form": form,
                "password_not_confirm": password_not_confirm,
                "fields_to_display": fields_to_display,
                'user_status': request.user.is_authenticated,
            }
        )

    def post(self, request):
        password_not_confirm = None
        error_message = None
        continue_to_form = True

        fields_to_display = ['Currency']

        form = ProfileForm(request.POST or None)

        for key, value in form.data.items():
            if not value:
                # print(key, value)
                continue_to_form = False

        if form.is_valid() and continue_to_form:
            if form.data.get("confirm-password") == form.data.get("password"):
                try:
                    user = User.objects.create_user(username=form.data.get('username'),
                                                    password=form.data.get('password'),
                                                    email=form.data.get('email'))
                except IntegrityError:
                    # messages.error()
                    error_message = "Username is already taken. Please try another"

                else:
                    user.save()

                    form.instance.user = user
                    # adding the default blank image
                    form.instance.image = 'images/c0749b7cc401421662ae901ec8f9f660.jpg'

                    self.request.session['user_currency'] = form.instance.currency

                    form.save()

                    # current_user = User.objects.get(username=form.cleaned_data["username"])
                    request.session["current_user"] = user.id

                    login(request, user)

                    return HttpResponseRedirect('/')
            else:
                password_not_confirm = "Password must be the same on both fields"
        else:
            error_message = "Please fill out all the required fields"

        return render(request, template_name="expenses_tracker/signup.html",
                      context={"form": form, "password_not_confirm": password_not_confirm,
                               'error_message': error_message,
                               'fields_to_display': fields_to_display,
                               'user_status': request.user.is_authenticated
                               }
                      )


def login_user(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            logging.info(msg='Authentication successful')
            request.session["current_user"] = user.id

            request.session['user_currency'] = user.profile.currency

            login(request, user)
            return HttpResponseRedirect('/')
        else:
            logging.info(msg='Authentication failed')
            error_message = "Username or password incorrect"

    return render(
        request,
        template_name='expenses_tracker/login.html',
        status=200,
        context={
            "error_message": error_message,
            'user_status': request.user.is_authenticated
        }
    )


def logout_user(request):
    request.session.delete()
    logout(request)
    return HttpResponseRedirect('/login')


def privacy_policy(request):
    return render(
        request,
        template_name='expenses_tracker/privacy_policy.html',
        status=200,
        context={'user_status': request.user.is_authenticated}
    )


def terms_of_service(request):
    return render(
        request,
        template_name='expenses_tracker/terms_of_service.html',
        status=200,
        context={'user_status': request.user.is_authenticated}
    )


def contact_us(request):
    return render(
        request,
        template_name='expenses_tracker/contact_us.html',
        status=200,
        context={'user_status': request.user.is_authenticated}
    )
