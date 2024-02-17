from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import CreateView, TemplateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.db.models import Count, Sum, Avg

from .form_models import UserForm, TransactionForm, BudgetForm
from django.views import View
from datetime import datetime, timedelta
from .models import Transaction, Budget, User

from django.utils import timezone


# Create your views here.


class IndexView(TemplateView):
    template_name = 'expenses_tracker/index.html'


def overview(request):
    transactions = Transaction.objects.all()
    category_transactions = transactions.order_by('-date')[:3]
    transactions1 = transactions.aggregate(amount=Sum('amount'))

    category = {field.category: transactions.filter(category=field.category).aggregate(
        sum=Sum('amount')).get('sum') for field in category_transactions}

    recent_transactions = category_transactions
    recurring_transaction = transactions.filter(recurring_transaction=True).order_by('next_occurrence')[:3]

    budget = Budget.objects.all()
    budget1 = budget.aggregate(amount=Sum('amount'))
    budget2 = budget.order_by('expiration_date')[:3]

    date_now = timezone.now()

    return render(
        request,
        'expenses_tracker/overview.html',
        context={'transactions': transactions1['amount'],
                 'category': category,
                 'recent_transactions': recent_transactions,
                 'budget': budget2,
                 'total_budget': budget1['amount'],
                 'recur_transaction': recurring_transaction,
                 'date_now': date_now
                 }
    )


def budget_calculation(budget_objs, transaction_obj):
    for field in budget_objs.all():
        if field.budget > field.amount:
            field.amount += transaction_obj.amount
            field.spent -= transaction_obj.amount
            field.save()


class AllTransactionsView(ListView):
    template_name = 'expenses_tracker/all_transactions.html'
    model = Transaction
    context_object_name = 'transactions'

    def get_queryset(self):
        return super(AllTransactionsView, self).get_queryset().order_by('-date')

    def get_context_data(self, **kwargs):
        context = super(AllTransactionsView, self).get_context_data(**kwargs)
        context['date_now'] = timezone.now()
        return context

    def post(self, request, *args, **kwargs):
        transaction_id = request.POST.get('all_transaction_id')
        transaction_obj = Transaction.objects.get(id=transaction_id)
        budget_objects = Budget.objects.all()
        budget_objects_categories = budget_objects.filter(category=transaction_obj.category)
        all_transactions_budget = budget_objects.filter(category="All Transactions")

        budget_calculation(budget_objs=budget_objects_categories, transaction_obj=transaction_obj)
        budget_calculation(budget_objs=all_transactions_budget, transaction_obj=transaction_obj)
        transaction_obj.delete()
        return HttpResponseRedirect('/all_transactions')


def budget_calc(field, form_instance):
    field.amount -= form_instance.amount
    field.spent = field.budget - field.amount
    field.save()


class AddTransactionView(CreateView):
    template_name = 'expenses_tracker/add_transaction.html'
    model = Transaction
    form_class = TransactionForm
    success_url = "/all_transactions"
    context_object_name = 'transactions'

    def form_valid(self, form):
        for field in Budget.objects.all():
            if field.category == 'All Transactions':
                budget_calc(field=field, form_instance=form.instance)

            elif field.category == form.instance.category:
                budget_calc(field=field, form_instance=form.instance)
        return super(AddTransactionView, self).form_valid(form)


class CategoryView(ListView):
    template_name = 'expenses_tracker/categories.html'
    model = Transaction
    context_object_name = 'categories'

    def get_queryset(self):
        db = super(CategoryView, self).get_queryset()
        return {field.category: db.filter(category=field.category).aggregate(
            sum=Sum('amount')).get('sum') for field in db.order_by("-date")}


class RecurringTransactions(ListView):
    template_name = 'expenses_tracker/recurring-transactions.html'
    model = Transaction
    context_object_name = 'recurring_transactions'

    def get_queryset(self):
        data = super(RecurringTransactions, self).get_queryset().filter(recurring_transaction=True)
        for recurring_transaction in data.all():
            if timezone.now() > recurring_transaction.next_occurrence:
                recurring_transaction.date = timezone.now()
                recurring_transaction.save()
        return data.order_by('next_occurrence')

    def post(self, request, *args, **kwargs):
        transaction_id = request.POST.get('recurring_transaction_id')
        transaction_obj = Transaction.objects.get(id=transaction_id)
        transaction_obj.recurring_transaction = False
        transaction_obj.frequency = None
        transaction_obj.transaction_title = None
        transaction_obj.next_occurrence = None
        transaction_obj.save()
        return HttpResponseRedirect('/recurring-transactions')


class BudgetOverviewView(ListView):
    template_name = 'expenses_tracker/budget-overview.html'
    model = Budget
    context_object_name = 'budget'

    def get_queryset(self):
        db = super(BudgetOverviewView, self).get_queryset()
        for field in db:
            if field.spent >= field.budget or timezone.now() > field.expiration_date:
                field.delete()
        return db.order_by('expiration_date')

    def post(self, request, *args, **kwargs):
        budget_id = request.POST.get('budget_overview_id')
        Budget.objects.get(id=budget_id).delete()
        return HttpResponseRedirect('/budget-overview')


class AddBudgetView(CreateView):
    template_name = 'expenses_tracker/add_budget.html'
    model = Budget
    form_class = BudgetForm
    success_url = '/budget-overview'

    def form_valid(self, form):
        form.instance.budget = float(form.cleaned_data.get('amount'))
        return super(AddBudgetView, self).form_valid(form)


def expenses_report(request):
    return render(
        request,
        'expenses_tracker/expenses-report.html',
        status=200
    )


def income_report(request):
    return render(
        request,
        'expenses_tracker/income-report.html',
        status=200
    )


def custom_report(request):
    return render(
        request,
        template_name='expenses_tracker/custom-report.html',
        status=200
    )


def profile_details(request):
    return render(
        request,
        template_name='expenses_tracker/profile.html',
        status=200
    )


def notification(request):
    return render(
        request,
        template_name='expenses_tracker/notification.html',
        status=200
    )


def account_settings(request):
    return render(
        request,
        template_name='expenses_tracker/account_settings.html',
        status=200
    )


class RegisterView(View):

    def get(self, request):

        password_not_confirm = None
        form = UserForm()

        return render(
            request, template_name='expenses_tracker/signup.html',
            context={
                "form": form,
                "password_not_confirm": password_not_confirm
            }
        )

    def post(self, request):
        password_not_confirm = None

        form = UserForm(request.POST or None)
        if form.is_valid():

            if form.data.get("confirm-password") == form.cleaned_data["password"]:
                form.save()
                return HttpResponseRedirect('/overview')
            else:
                password_not_confirm = "Password must be the same on both fields"

        return render(request, template_name="expenses_tracker/signup.html",
                      context={"form": form, "password_not_confirm": password_not_confirm})


def login(request):
    return render(
        request,
        template_name='expenses_tracker/login.html',
        status=200
    )


def logout(request):
    pass


def privacy_policy(request):
    return render(
        request,
        template_name='expenses_tracker/privacy_policy.html',
        status=200
    )


def terms_of_service(request):
    return render(
        request,
        template_name='expenses_tracker/terms_of_service.html',
        status=200
    )


def contact_us(request):
    return render(
        request,
        template_name='expenses_tracker/contact_us.html',
        status=200
    )


class DeleteItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pass
