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

from .form_models import ProfileForm, TransactionForm, BudgetForm, IncomeForm, ContactForm, UserForm
from django.views import View
from datetime import datetime, timedelta
from .models import Transaction, Budget, Profile, Income
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.template.loader import render_to_string, get_template
from django.utils import timezone

from .filter_func import expenses_query_filter_func
from expenses_tracker.form_models import ExpenseIncomeReportForm
from expenses_tracker.email_client import send_message
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class IndexView(TemplateView):
    template_name = 'expenses_tracker/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
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

    income_data = Income.objects.all().filter(user_id=request.user.id)
    total_income = income_data.aggregate(amount=Sum('amount'))

    recent_income_data = income_data.order_by('-date')[:3]

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
                 'user_currency': user_currency,
                 'user_status': request.user.is_authenticated,
                 'total_income': total_income['amount'],
                 'income_data': recent_income_data,
                 'current_year': date_now.year
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
            filtered_query = expenses_query_filter_func(sort_order=sort_order,
                                                        filter_category=self.request.session.pop('filter_category'),
                                                        order_by=self.request.session.pop('order_by'), query_db=query,
                                                        sort_pop=self.request.session.pop('sort_order'))
            return filtered_query

        return query

    def get_context_data(self, **kwargs):
        context = super(AllTransactionsView, self).get_context_data(**kwargs)
        context['thirty_days_earlier'] = timezone.now() - timedelta(days=30)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
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

    def get_context_data(self, **kwargs):
        context = super(AddTransactionView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        return context


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
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        return context


class RecurringTransactions(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/recurring-transactions.html'
    model = Transaction
    context_object_name = 'recurring_transactions_incomes'

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
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
        context['thirty_days_later'] = timezone.now() + timedelta(days=30)
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
        context['thirty_days_later'] = timezone.now() + timedelta(days=30)
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
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

    def get_context_data(self, **kwargs):
        context = super(AddBudgetView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        return context


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
def expenses_report(request, *args, **kwargs):
    from .pdf import convert_html_to_pdf
    is_expense_report = True
    user = User.objects.get(id=request.user.id)
    user_currency = request.session.get('user_currency')

    start_date = request.session.pop('start_date')
    end_date = request.session.pop('end_date')
    purpose = request.session.pop('purpose')
    note = request.session.pop('note')

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
    request_from_income_report = request.session.pop("request_from_income_report", default=None)

    if request_from_income_report:

        income_data = Income.objects.filter(user_id=user.id).filter(date__date__gte=start_date,
                                                                    date__date__lte=end_date).order_by('date')
        income_data_sum_total = income_data.aggregate(amount=Sum('amount'))

        source = {field.category: income_data.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in income_data}

        context["source"] = source
        context["income_data_sum_total"] = income_data_sum_total['amount']
        context["income_data"] = income_data

        html_content = render_to_string('expenses_tracker/income-report.html', context)
        is_expense_report = False

    else:

        reports_transaction = Transaction.objects.filter(
            user_id=user.id).filter(date__date__gte=start_date, date__date__lte=end_date).order_by('date')

        transactions_sum_total = reports_transaction.aggregate(amount=Sum('amount'))

        category = {field.category: reports_transaction.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in reports_transaction}

        context["category"] = category
        context["transactions_sum_total"] = transactions_sum_total['amount']
        context["transactions"] = reports_transaction

        html_content = render_to_string('expenses_tracker/expenses-report.html', context)

    pdf_response = convert_html_to_pdf(source_html=html_content, is_expense_report=is_expense_report)
    return pdf_response


@login_required
def expense_income_report_form(request):
    error = None
    if request.method == 'POST':
        form = ExpenseIncomeReportForm(request.POST or None)

        if form.is_valid():
            for key, value in form.cleaned_data.items():

                if key != 'csrfmiddlewaretoken':
                    if key == 'start_date' or key == 'end_date':
                        # Convert a date object to string
                        serialized_date = value.isoformat()
                        request.session[key] = serialized_date
                    else:
                        request.session[key] = value
            request.session["request_from_income_report"] = request.POST.get('income_data')
            return HttpResponseRedirect('/expenses-report')
        else:
            error = form.errors

    return render(
        request,
        template_name='expenses_tracker/expenses_incomes_report_form.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'errors': error,
                 'current_year': datetime.now().year}
    )


class IncomeData(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'expenses_tracker/income_data.html'
    context_object_name = 'income_data'

    def get_context_data(self, **kwargs):
        context = super(IncomeData, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Source"
        context['thirty_days_earlier'] = timezone.now() - timedelta(days=30)
        return context

    def get_queryset(self):
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')
        order_by = self.request.session.get('order_by')
        data = (super(IncomeData, self).get_queryset().filter(user_id=self.request.user.id))

        if filter_category:
            return expenses_query_filter_func(sort_order=sort_order,
                                              filter_category=self.request.session.pop('filter_category'),
                                              order_by=self.request.session.pop('order_by'), query_db=data,
                                              sort_pop=self.request.session.pop('sort_order'))
        return data.order_by('-date')

    def post(self, request, *args, **kwargs):
        income_data_id = request.POST.get('income_data_id')

        if income_data_id:
            Income.objects.get(id=income_data_id).delete()

        request.session['filter_category'] = request.POST.get('filter_category')
        request.session['order_by'] = request.POST.get('order_by')
        request.session['sort_order'] = request.POST.get('sort_order')
        return HttpResponseRedirect('/income-data')


class IncomeFormView(LoginRequiredMixin, CreateView):
    model = Income
    template_name = 'expenses_tracker/add_income.html'
    form_class = IncomeForm
    success_url = '/income-data'

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super(IncomeFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(IncomeFormView, self).get_context_data(**kwargs)
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        return context


class IncomeCategoryView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'expenses_tracker/categories.html'
    context_object_name = 'categories'

    def get_queryset(self):
        db = super(IncomeCategoryView, self).get_queryset().filter(user_id=self.request.user.id)

        return {field.category: db.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in db.order_by("-date")}

    def get_context_data(self, **kwargs):
        context = super(IncomeCategoryView, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['current_year'] = datetime.now().year
        return context


class RecurringIncomes(LoginRequiredMixin, ListView):
    template_name = 'expenses_tracker/income-recur.html'
    model = Income
    context_object_name = 'recurring_transactions_incomes'

    def get_queryset(self):
        filter_category = self.request.session.get('filter_category')
        sort_order = self.request.session.get('sort_order')

        data = (super(RecurringIncomes, self).get_queryset().filter(
            user_id=self.request.user.id).filter(recurring_transaction=True))

        for recurring_income in data.all():
            if timezone.now() > recurring_income.next_occurrence:
                recurring_income.date = timezone.now()
                recurring_income.save()

        if filter_category:
            return expenses_query_filter_func(sort_order=sort_order,
                                              filter_category=self.request.session.pop('filter_category'),
                                              order_by=self.request.session.pop('order_by'), query_db=data,
                                              sort_pop=self.request.session.pop('sort_order'))
        return data.order_by('next_occurrence')

    def get_context_data(self, **kwargs):
        context = super(RecurringIncomes, self).get_context_data(**kwargs)
        context['user_currency'] = self.request.session.get('user_currency')
        context['user_status'] = self.request.user.is_authenticated
        context['transaction_category'] = {cate_.category: None for cate_ in self.object_list}
        context['current_year'] = datetime.now().year
        context["category_source"] = "Category"
        context['thirty_days_later'] = timezone.now() + timedelta(days=30)
        return context

    def post(self, request, *args, **kwargs):
        income_id = request.POST.get('recurring_transaction_id')
        if income_id:
            transaction_obj = Income.objects.get(id=income_id)
            transaction_obj.recurring_transaction = False
            transaction_obj.frequency = None
            transaction_obj.transaction_title = None
            transaction_obj.next_occurrence = None
            transaction_obj.save()
        else:
            request.session['filter_category'] = request.POST.get('filter_category')
            request.session['order_by'] = request.POST.get('order_by')
            request.session['sort_order'] = request.POST.get('sort_order')
        return HttpResponseRedirect('/recurring-incomes')


@login_required
def profile_details(request):
    profile = Profile.objects.get(user=request.user)
    if not profile.image:
        profile.image = 'images/c0749b7cc401421662ae901ec8f9f660.jpg'
        profile.save()
    return render(
        request,
        template_name='expenses_tracker/profile.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'profile': profile,
                 'current_year': datetime.now().year}
    )


@login_required
def notification(request):
    return render(
        request,
        template_name='expenses_tracker/notification.html',
        status=200,
        context={'user_status': request.user.is_authenticated,
                 'current_year': datetime.now().year}
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
                     'profile_updated': profile_updated,
                     'current_year': datetime.now().year}
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
                     'form': profile_form,
                     'current_year': datetime.now().year}
        )


class RegisterView(View):

    def get(self, request):
        password_not_confirm = None
        form = ProfileForm()
        user_form = UserForm(request.POST or None)
        fields_to_display = ['Currency']

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
        user_form = UserForm(request.POST or None)

        fields_to_display = ['Currency']

        form = ProfileForm(request.POST or None)

        if form.is_valid() and user_form.is_valid():

            user_form.save(commit=False)

            user_form.instance.set_password(user_form.cleaned_data['password'])

            form.instance.user = user_form.instance

            # adding the default blank image
            form.instance.image = 'images/c0749b7cc401421662ae901ec8f9f660.jpg'

            self.request.session['user_currency'] = form.instance.currency

            user_form.save()
            form.save()

            user = User.objects.get(username=user_form.instance.username)

            request.session["current_user"] = user.id

            login(request, user)

            return HttpResponseRedirect('/')

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
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            request.session["current_user"] = user.id

            request.session['user_currency'] = user.profile.currency

            login(request, user)
            return HttpResponseRedirect('/')
        else:
            error_message = "Username or password incorrect"

    return render(
        request,
        template_name='expenses_tracker/login.html',
        status=200,
        context={
            "error_message": error_message,
            'user_status': request.user.is_authenticated,
            'current_year': datetime.now().year
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
        context={'user_status': request.user.is_authenticated,
                 'current_year': datetime.now().year}
    )


def terms_of_service(request):
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

    is_message_sent = request.session.pop('is_message_sent', False)
    validation_error = None

    form = ContactForm(request.POST or None)

    if form.is_valid():
        try:
            ContactForm.clean_your_field(form)
        except ValidationError:
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
            # Render the template with the flag
            return HttpResponseRedirect('/contact-us')
            # return render_template("contact.html", msg_sent=sent)

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
