from django.urls import path
from . import views


app_name = "widget"
urlpatterns = [
    path("", views.home, name="home"),
    path("/shopping-list", views.shopping_list, name="shopping"),
    path("/shopping-list/edit/<int:item_id>", views.edit_item, name="edit_item"),
    path("/shopping-list/delete/<int:item_id>", views.delete_item, name="delete_item"),
    path("/finance",views.finance,name="finance")
]
