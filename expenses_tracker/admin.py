from django.contrib import admin
from .models import Transaction, Budget, Profile
from django.contrib.auth.admin import User

# Register your models here.


admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(Profile)
