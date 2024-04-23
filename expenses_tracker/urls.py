from django.urls import path
from . import views

# app_name = 'expenses_tracker'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),

    path('login/', views.login_user, name='login_page'),

    path('logout/', views.logout_user, name='logout'),

    path('register-signup/', views.RegisterView.as_view(), name='register_page'),

    path('overview/', views.overview, name='overview_page'),

    path('all_transactions/', views.AllTransactionsView.as_view(), name='all_transactions_page'),

    path('add_transactions/', views.AddTransactionView.as_view(), name='add_transactions_page'),

    path('categories/', views.CategoryView.as_view(), name='categories_page'),

    path('recurring-transactions/', views.RecurringTransactions.as_view(), name='recurring_transactions_page'),

    path('recurring-incomes/', views.RecurringIncomes.as_view(), name='recurring_income_page'),

    path('budget-overview/', views.BudgetOverviewView.as_view(), name='budget-overview_page'),

    path('add-budget/', views.AddBudgetView.as_view(), name='add_budget_page'),

    path('expenses-report/', views.expenses_report, name='expenses_report_page'),

    path('income-data/', views.IncomeData.as_view(), name='income_data_page'),

    path('add-income/', views.IncomeFormView.as_view(), name='add_income_page'),

    path('income-category/', views.IncomeCategoryView.as_view(), name='income_category_page'),

    path('expense-reports-form/', views.expense_income_report_form, name='expense_reports_form_page'),

    path('profile-details/', views.profile_details, name='profile_page'),

    path('notifications/', views.notification, name='notification_page'),

    path('account-settings/', views.AccountSettingsView.as_view(), name='account_settings_page'),

    path('privacy-policy/', views.privacy_policy, name='privacy_policy_page'),

    path('terms_of_service/', views.terms_of_service, name='terms_of_service_page'),

    path('contact-us/', views.contact_us, name='contact_us_page'),

    path('linechart/', views.line_chart, name='line_chart_page'),

    path('barchart/', views.bar_chart, name='bar_chart_page'),

    path('exchange-rate/', views.exchange_rate, name='exchange_rate_page')

]
