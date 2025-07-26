from django.contrib import admin
from .models import ShoppingListItem
# Register your models here.


@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'link', 'price') 
