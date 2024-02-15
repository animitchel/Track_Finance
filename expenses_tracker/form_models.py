from django import forms
from .models import User, Budget, Transaction


class UserForm(forms.ModelForm):
    class Meta:
        model = User

        fields = ['username', 'email_address', 'password']

        labels = {'username': 'Username', 'email_address': 'Email', 'password': 'Password'}

        widgets = {'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
                   'email_address': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
                   'password': forms.PasswordInput(attrs={'placeholder': 'Enter your password'})}

        error_messages = {'username': {'required': 'Please enter a username'},
                          'email_address': {'required': 'Please enter an email'},
                          'password': {'required': 'Please enter a password'}
                          }


class TransactionForm(forms.ModelForm):
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('2 weeks', 'Biweekly'),
        ('3 weeks', 'Every 3 weeks'),
        ('2 months', 'Bimonthly'),
        ('4 months', 'Every 4 months'),
        ('5 months', 'Every 5 months'),
        ('6 months', 'Semiannual'),
        ('7 months', 'Every 7 months'),
        ('8 months', 'Every 8 months'),
        ('9 months', 'Every 9 months'),
        ('10 months', 'Every 10 months'),
        ('11 months', 'Every 11 months')
    ]

    class Meta:
        model = Transaction
        # fields = '__all__'
        exclude = ['user', 'next_occurrence', 'date']

        labels = {'category': 'Category', 'amount': 'Amount', 'description': 'Description',
                  'recurring_transaction': 'Recurring Transaction', 'frequency': 'Frequency',
                  'transaction_title': 'Transaction_Title', 'date': 'Transaction_Date'}

        error_messages = {'category': {'required': 'Please enter a category'},
                          'amount': {'required': 'Please enter a valid transaction amount'},
                          'description': {'required': 'Please enter a description.'}
                          }

    transaction_title = forms.CharField(max_length=50, required=False)
    frequency = forms.ChoiceField(required=False, choices=FREQUENCY_CHOICES)
    amount = forms.DecimalField(min_value=1.00, decimal_places=2, max_digits=10)


class BudgetForm(forms.ModelForm):
    DURATION_CHOICES = [
        ('1 week', '1 Week'),
        ('2 weeks', '2 Weeks'),
        ('3 weeks', '3 Weeks'),
        ('1 month', '1 Month'),
        ('2 months', '2 Months'),
        ('3 months', '3 Months'),
        ('4 months', '4 Months'),
        ('5 months', '5 Months'),
        ('6 months', '6 Months'),
        ('7 months', '7 Months'),
        ('8 months', '8 Months'),
        ('9 months', '9 Months'),
        ('10 months', '10 Months'),
        ('11 months', '11 Months'),
        ('1 year', '1 Year'),
    ]

    class Meta:
        model = Budget
        exclude = ['user', 'budget', 'spent', 'expiration_date']

        labels = {
            'category': 'Category', 'amount': 'Amount', 'description': 'Description', 'duration': 'Duration'
        }

        error_messages = {
            'amount': {
                'required': 'Please enter a valid budget amount.',
                'invalid': 'Please enter a valid budget amount.',
                'max_length': 'Please enter a valid budget amount.',
                'min_length': 'Please enter a valid budget amount'
            },
            'category': {'required': 'Please select a valid category'},
            'description': {'required': 'Please enter a description of the budget'}
        }

    amount = forms.DecimalField(min_value=1.00, decimal_places=2, max_digits=10)
    duration = forms.ChoiceField(choices=DURATION_CHOICES)
