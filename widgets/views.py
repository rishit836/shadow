from .models import ShoppingListItem
from django.shortcuts import get_object_or_404
from django.contrib import messages
def edit_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    if request.method == "POST":
        item.name = request.POST.get("item-name")
        item.link = request.POST.get("item-link")
        item.price = request.POST.get("item-price")
        item.save()
        messages.success(request, "Item updated successfully!")
        return redirect(reverse("widget:shopping"))
    return render(request, "edit_item.html", {"item": item})

def delete_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item marked as bought and removed!")
        return redirect(reverse("widget:shopping"))
    return redirect(reverse("widget:shopping"))
from django.shortcuts import render,redirect
from django.urls import reverse
from .operations import push_item,list_exists

# Create your views here.
def home(request):
    return render(request,'widget_home.html')


def shopping_list(request):
    context = {}
    if request.method == "POST":
        item_name = request.POST.get("item-name")
        item_link = request.POST.get("item-link")
        item_price = request.POST.get("item-price")
        push_item(request.user, item_name, item_link, item_price)
    if not request.user.is_authenticated:
        return redirect(reverse("main:login"))
    else:
        le = list_exists(request.user)
        shopping_items = []
        if le:
            from .operations import get_shopping_list
            shopping_items = get_shopping_list(request.user)
        context.update({
            "list_exists": le,
            "shopping_items": shopping_items
        })
    return render(request, 'shopping.html', context=context)