from django.contrib import admin
from .models import Transaction, Budget, Profile
from django.contrib.auth.admin import User


# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('category', 'amount')
    search_fields = ('category', 'description')
    list_filter = ('category',)


class BudgetAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('category', 'amount')
    search_fields = ('category', 'description')
    list_filter = ('category',)


class ProfileAdmin(admin.ModelAdmin):
    # list_display = ('first_name', 'occupation')
    ordering = ('id',)
    search_fields = ('first_name',)
    list_filter = ('first_name', 'last_name', 'occupation', 'city', 'country')


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(Profile, ProfileAdmin)
