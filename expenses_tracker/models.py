from copy import copy

from django.db import models
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from django.utils import timezone


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100, unique=True, null=False)
    email_address = models.EmailField(max_length=150, null=False, unique=True)
    password = models.CharField(max_length=20, null=False, blank=False)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to='images', null=True)
    occupation = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=15,
                                    null=True,
                                    validators=[
                                        RegexValidator(r'^\+?1?\d{9,15}$',
                                                       message="Phone number must be entered in the format: "
                                                               "'+999999999'"
                                                               ". Up to 15 digits allowed.")])


class Transaction(models.Model):
    EXPENSE_CATEGORIES = [
        ('Housing', 'Housing'),
        ('Transportation', 'Transportation'),
        ('Groceries', 'Groceries'),
        ('Utilities', 'Utilities'),
        ('Healthcare', 'Healthcare'),
        ('Debt Repayment', 'Debt Repayment'),
        ('Entertainment', 'Entertainment'),
        ('Personal Care', 'Personal Care'),
        ('Education', 'Education'),
        ('Insurance', 'Insurance'),
        ('Taxes', 'Taxes'),
        ('Savings', 'Savings'),
        ('Miscellaneous', 'Miscellaneous'),
        ('Travel', 'Travel'),
        ('Home Maintenance', 'Home Maintenance'),
        ('Investments', 'Investments'),
        ('Clothing', 'Clothing'),
        ('Dining Out', 'Dining Out'),
        ('Fitness', 'Fitness'),
        ('Food', 'Food')
    ]

    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, null=False)
    amount = models.FloatField()
    description = models.TextField(null=True, max_length=400)
    recurring_transaction = models.BooleanField(default=False)
    frequency = models.CharField(max_length=10, null=True)
    transaction_title = models.CharField(max_length=50, null=True)
    date = models.DateTimeField(default=timezone.now)
    next_occurrence = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction', null=True)

    def save(self, *args, **kwargs):

        _frequency = {
            'weekly': 1,
            'monthly': 4.4286,
            'quarterly': 13.4286,
            'yearly': 54.2857,
            '2 weeks': 2,
            '3 weeks': 3,
            '2 months': 9.0000,
            '4 months': 17.8571,
            '5 months': 22.5714,
            '6 months': 27.0000,
            '7 months': 31.4286,
            '8 months': 36.1429,
            '9 months': 40.5714,
            '10 months': 45.0000,
            '11 months': 49.5714,
        }

        for field in Budget.objects.all():

            if field.category == 'All Transactions':
                field.amount -= self.amount
                field.spent = field.budget - field.amount
                field.save()

            elif field.category == self.category:
                field.amount -= self.amount
                field.spent = field.budget - field.amount
                field.save()

        if self.recurring_transaction:
            frequency = next(_frequency[key] for key in _frequency if key == self.frequency)

            # parsed_datetime = datetime.now() + timedelta(weeks=frequency)
            # desired_timezone = pytz.timezone('UTC')
            # self.next_occurrence = parsed_datetime.replace(tzinfo=pytz.utc).astimezone(desired_timezone)
            self.next_occurrence = timezone.now() + timedelta(weeks=frequency)

            if not self.transaction_title:
                self.transaction_title = self.category

        else:
            self.frequency = None
            self.transaction_title = None

        super(Transaction, self).save(*args, **kwargs)


class Budget(models.Model):
    BUDGET_CATEGORIES = [
        ('All Transactions', 'Budget for All Transactions'),
        ('Housing', 'Housing'),
        ('Transportation', 'Transportation'),
        ('Groceries', 'Groceries'),
        ('Utilities', 'Utilities'),
        ('Healthcare', 'Healthcare'),
        ('Debt Repayment', 'Debt Repayment'),
        ('Entertainment', 'Entertainment'),
        ('Personal Care', 'Personal Care'),
        ('Education', 'Education'),
        ('Insurance', 'Insurance'),
        ('Savings', 'Savings'),
        ('Miscellaneous', 'Miscellaneous'),
        ('Travel', 'Travel'),
        ('Home Maintenance', 'Home Maintenance'),
        ('Investments', 'Investments'),
        ('Taxes', 'Taxes'),
        ('Clothing', 'Clothing'),
        ('Dining Out', 'Dining Out'),
        ('Fitness', 'Fitness'),
        ('Food', 'Food')
    ]

    category = models.CharField(max_length=20, choices=BUDGET_CATEGORIES)
    amount = models.FloatField()
    budget = models.FloatField(null=True)
    spent = models.FloatField(default=0.0)
    description = models.TextField(max_length=500)
    duration = models.CharField(max_length=20, null=True, blank=True)
    # durational = models.BooleanField(default=False)
    expiration_date = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget', null=True)

    def save(self, *args, **kwargs):
        _duration = {
            '1 week': 1,
            '2 weeks': 2,
            '3 weeks': 3,
            '1 month': 4.4286,
            '2 months': 9.0000,
            '3 months': 13.4286,
            '4 months': 17.8571,
            '5 months': 22.5714,
            '6 months': 27.0000,
            '7 months': 31.4286,
            '8 months': 36.1429,
            '9 months': 40.5714,
            '10 months': 45.0000,
            '11 months': 49.5714,
            '1 year': 54.2857,
        }

        if self.spent == 0.0:
            validity_period = next(_duration[key] for key in _duration if key == self.duration)

            # parsed_datetime = datetime.now() + timedelta(weeks=validity_period)
            # desired_timezone = pytz.timezone('UTC')
            # self.expiration_date = parsed_datetime.replace(tzinfo=pytz.utc).astimezone(desired_timezone)
            self.expiration_date = timezone.now() + timedelta(weeks=validity_period)

        super(Budget, self).save(*args, **kwargs)
