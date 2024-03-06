from django.urls import path
from . import views


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

    path('budget-overview/', views.BudgetOverviewView.as_view(), name='budget-overview_page'),

    path('add-budget/', views.AddBudgetView.as_view(), name='add_budget_page'),

    path('expenses-report/', views.expenses_report, name='expenses_report_page'),

    path('income-report/', views.income_report, name='income_report_page'),

    path('custom-report/', views.custom_report, name='custom_report_page'),

    path('profile-details/', views.profile_details, name='profile_page'),

    path('notifications/', views.notification, name='notification_page'),

    path('account-settings/', views.AccountSettingsView.as_view(), name='account_settings_page'),

    path('privacy-policy/', views.privacy_policy, name='privacy_policy_page'),

    path('terms_of_service/', views.terms_of_service, name='terms_of_service_page'),

    path('contact-us/', views.contact_us, name='contact_us_page'),

    # path('delete-item/<int:pk>/', views.BudgetDeleteItemView.as_view(), name='budget_delete_item')
]
