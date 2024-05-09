from copy import copy

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

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


class Profile(models.Model):
    # Choices for currency selection
    CURRENCY_CHOICES = [
        ('$', 'Dollar - USD'),
        ('€', 'Euro - EUR'),
        ('£', 'Pound Sterling - GBP'),
        ('¥', 'Yen - JPY'),
        ('₣', 'Franc - CHF'),
        ('₹', 'Rupee - INR'),
        ('₦', 'Naira - NGN'),
        ('د.ك', 'Dinar - KWD'),
        ('د.إ', 'Dirham - AED'),
        ('﷼‎', 'Riyal - SAR'),
        ('₻', 'Mark - DEM'),
        ('₽', 'Ruouble - RUB'),
        ('₾', 'Lari - GEL'),
        ('₺', 'Lira - TRY'),
        ('₼', 'Manat - AZN'),
        ('₸', 'Tenge - KZT'),
        ('₴', 'Hryvnia - UAH'),
        ('₷', 'Spesmilo - XDR'),
        ('฿', 'Baht - THB'),
        ('원', 'Won - KRW'),
        ('₫', 'Dong - VND'),
        ('₮', 'Tugrik - MNT'),
        ('₯', 'Drachma - GRD'),
        ('₱', 'Peso - PHP'),
        ('₳', 'Austral - AUD'),
        ('₵', 'Cedi - GHS'),
        ('₲', 'Guarani - PYG'),
        ('₪', 'Sheqel - ILS'),
        ('₰', 'Penny - GBP')
    ]

    # Define fields for the Profile model
    currency = models.CharField(max_length=20, null=True, choices=CURRENCY_CHOICES)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=80, null=True)
    image = models.ImageField(upload_to='images', null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)

    # Define phone_number field with validation
    phone_number = models.CharField(max_length=15,
                                    null=True,
                                    validators=[
                                        RegexValidator(r'^\+?1?\d{9,15}$',
                                                       message="Phone number must be entered in the format: "
                                                               "'+999999999'. Up to 15 digits allowed.")
                                    ])

    # Define user field as a OneToOneField to User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)


class Transaction(models.Model):
    # Choices for expense categories
    EXPENSE_CATEGORIES = [
        ('Housing', 'Housing'),
        ('Transportation', 'Transportation'),
        ('Groceries', 'Groceries'),
        ('Utilities', 'Utilities'),
        ('Healthcare', 'Healthcare'),
        ('Accommodation', 'Accommodation'),
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
        ('Food', 'Food'),
        ('Business', 'Business'),
        ('My Girl', 'My Girl'),
        ('Family', 'Family'),
        ('Other', 'Other'),
    ]

    # Define fields for the Transaction model
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, null=False)
    amount = models.FloatField()
    description = models.TextField(null=True, max_length=100)
    recurring_transaction = models.BooleanField(default=False)
    frequency = models.CharField(max_length=10, null=True, blank=True)
    transaction_title = models.CharField(max_length=40, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    next_occurrence = models.DateTimeField(null=True, blank=True)
    is_all_trans_bud = models.BooleanField(default=False, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction', null=True)

    def save(self, *args, **kwargs):
        # If the transaction is recurring, calculate the next occurrence based on the frequency

        if self.recurring_transaction:
            frequency = _frequency.get(self.frequency)
            self.next_occurrence = timezone.now() + timedelta(weeks=frequency)

            self.transaction_title = self.transaction_title or self.category
        else:
            self.frequency = None
            self.transaction_title = None

        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        # Return string representation of the transaction
        return f"{self.category} - {self.amount}"


class Budget(models.Model):
    # Choices for budget categories
    BUDGET_CATEGORIES = [
        ('All Transactions', 'Budget for All Transactions'),
        ('Housing', 'Housing'),
        ('Transportation', 'Transportation'),
        ('Accommodation', 'Accommodation'),
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
        ('Food', 'Food'),
        ('Business', 'Business'),
        ('My Girl', 'My Girl'),
        ('Family', 'Family')
    ]

    # Define fields for the Budget model
    category = models.CharField(max_length=20, choices=BUDGET_CATEGORIES)
    amount = models.FloatField()
    budget = models.FloatField(null=True)
    spent = models.FloatField(default=0.0)
    description = models.TextField(max_length=400)
    duration = models.CharField(max_length=20, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True)
    date = models.DateTimeField(default=timezone.now, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget', null=True)

    def save(self, *args, **kwargs):
        # Duration for budget validity
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

        # Set expiration date if spent is zero
        if self.spent == 0.0:
            validity_period = _duration.get(self.duration)
            self.expiration_date = self.date + timedelta(weeks=validity_period)

        super(Budget, self).save(*args, **kwargs)

    def __str__(self):
        # Return string representation of the budget
        return f"{self.category} - {self.amount}"


class Income(models.Model):
    # Choices for income sources
    INCOME_SOURCES = [
        ("salary or wages", "Salary or Wages"),
        ("business income", "Business Income"),
        ("rental income", "Rental Income"),
        ("investment income", "Investment Income"),
        ("interest income", "Interest Income"),
        ("pension or retirement income", "Pension or Retirement Income"),
        ("social security benefits", "Social Security Benefits"),
        ("alimony or child support", "Alimony or Child Support"),
        ("royalties", "Royalties"),
        ("gifts or inheritance", "Gifts or Inheritance")
    ]
    # Define fields for the Income model
    category = models.CharField(max_length=40, choices=INCOME_SOURCES)
    amount = models.FloatField()
    notes = models.TextField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    recurring_transaction = models.BooleanField(default=False)
    frequency = models.CharField(max_length=10, blank=True, null=True)
    transaction_title = models.CharField(max_length=40, blank=True, null=True)
    next_occurrence = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="income_data")

    def save(self, *args, **kwargs):
        # Set next occurrence if recurring

        if self.recurring_transaction:
            # frequency = next(_frequency[key] for key in _frequency if key == self.frequency)
            frequency = _frequency.get(self.frequency)
            self.next_occurrence = timezone.now() + timedelta(weeks=frequency)

            # Set transaction title if not provided
            if not self.transaction_title:
                self.transaction_title = self.category
        else:
            # Reset frequency and transaction title if not recurring
            self.frequency = None
            self.transaction_title = None

        super(Income, self).save(*args, **kwargs)

    def __str__(self):
        # Return string representation of the income
        return f"{self.category} - {self.amount}"
