from django.contrib import admin
from .models import ShoppingListItem, finance, FinanceProfile, Transaction

@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'link', 'price', 'priority') 

@admin.register(finance)
class FinanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'funds')

@admin.register(FinanceProfile)
class FinanceProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_funds', 'monthly_income', 'financial_score', 'updated_at')
    readonly_fields = ('financial_score', 'budget_allocation')
    list_filter = ('created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('finance_profile', 'amount', 'transaction_type', 'category', 'description', 'created_at')
    list_filter = ('transaction_type', 'category', 'created_at')
    search_fields = ('description',)
class FinanceWidget(admin.ModelAdmin):
    list_display = ("user","funds")
