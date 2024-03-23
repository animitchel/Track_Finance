from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Profile, Budget, Transaction, Income
from django.contrib.auth.models import User


# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']
#
#         labels = {'username': 'Username', 'email': 'Email', 'password': 'Password'}
#
#         widgets = {'password': forms.PasswordInput(attrs={'placeholder': 'Enter a password'}),
#                    'username': forms.TextInput(attrs={'placeholder': 'Enter a username'}),
#                    'email': forms.EmailInput(attrs={'placeholder': 'Enter an email address'})
#                    }
#
#         error_messages = {
#             'username': {'required': 'Please enter a username'},
#             'email': {'required': 'Please enter a valid email address'},
#             'password': {'required': 'Please enter a password'}
#         }

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

class ExpenseReportForm(forms.Form):
    purpose = forms.CharField(max_length=150, required=True)
    note = forms.CharField(max_length=400, required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile

        # fields = "__all__"
        exclude = ["user"]

        labels = {'username': 'Username', 'email_address': 'Email', 'password': 'Password', 'currency': 'Currency'}

        widgets = {'username': forms.TextInput(attrs={'placeholder': 'Enter a username'}),
                   'email_address': forms.EmailInput(attrs={'placeholder': 'Enter an email address'}),
                   'password': forms.PasswordInput(attrs={'placeholder': 'Enter a password'}),
                   'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
                   'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
                   'occupation': forms.TextInput(attrs={'placeholder': 'Enter your occupation'}),
                   'city': forms.TextInput(attrs={'placeholder': 'Enter your city name'}),
                   'country': forms.TextInput(attrs={'placeholder': 'Enter your country'}),
                   'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number e.g +999999999'}),
                   }

        error_messages = {'username': {'required': 'Please enter a username'},
                          'email_address': {'required': 'Please enter an email'},
                          'password': {'required': 'Please enter a password'},
                          'first_name': {'required': 'Please enter your first name'},
                          'last_name': {'required': 'Please enter your last'},
                          'occupation': {'required': 'Please enter your occupation'},
                          'city': {'required': 'Please enter your city'},
                          'country': {'required': 'Please enter your country'},
                          'currency': {'required': 'Please choose your currency'},
                          'phone_number': {'required': 'Please enter your phone number'},
                          }

    first_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter '
                                                                                                              'your '
                                                                                                              'first '
                                                                                                              'name'}))
    last_name = forms.CharField(required=False, max_length=100,
                                widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    occupation = forms.CharField(required=False, max_length=100,
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter your occupation'}))
    city = forms.CharField(required=False, max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Enter your city name'}))
    country = forms.CharField(required=False, max_length=100,
                              widget=forms.TextInput(attrs={'placeholder': 'Enter your country'}))
    phone_number = forms.CharField(required=False, max_length=15,
                                   widget=forms.TextInput(
                                       attrs={'placeholder': 'Enter your phone number e.g +999999999'}
                                   ))
    # image = forms.ImageField(required=False)
    # username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter a username'}))


class TransactionForm(forms.ModelForm):


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
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True, max_length=400)


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
        exclude = ['user', 'budget', 'spent', 'expiration_date', 'date']

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
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, max_length=500,
                                  min_length=50)


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        exclude = ['user', 'date']

        labels = {
            'source': 'Source', 'amount': 'Amount', 'notes': 'Notes'
        }

        error_messages = {
            'source': {'required': 'please select a valid source'},
            'amount': {'required': 'please enter a valid amount',
                       'invalid': 'Please enter a valid amount'},
            'notes': {'required': 'please enter a valid notes/description',
                      'max_length': 'Please keep your notes 50 characters long and under',
                      'min_length': 'Please keep your notes/description above 10 characters'}

        }

    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True, max_length=50, min_length=10)
    # frequency = forms.ChoiceField(required=False, choices=FREQUENCY_CHOICES)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Please enter your name'}),
        error_messages={'required': 'Please enter your name.'}
    )
    email = forms.EmailField(
        required=True,
        max_length=100,
        widget=forms.EmailInput(attrs={'placeholder': 'Please enter your email address'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please enter a message'}),
        max_length=500,
        min_length=10,
        error_messages={
            'required': 'Please enter a message.',
            'min_length': 'Message must be at least 10 characters long.',
            'max_length': 'Message must be less than 500 characters long'
        }
    )
    phone = PhoneNumberField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number e.g +12125552368'}),
        max_length=15,
        min_length=10,
        error_messages={
            'required': 'Please enter your phone number.',
            'min_length': 'Phone number must be at least 10 digits long.',
            'max_length': 'Phone number must be less than 15 digits long.'
        }
    )
