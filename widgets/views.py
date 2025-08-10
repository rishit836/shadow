from .models import ShoppingListItem, finance, FinanceProfile, Transaction
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
import datetime

def edit_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    if request.method == "POST":
        item.name = request.POST.get("item-name")
        item.link = request.POST.get("item-link")
        
        # Clean the price input using helper function
        raw_price = request.POST.get("item-price")
        item.price = clean_price_input(raw_price)
            
        item.priority = request.POST.get("item-priority") == "need"
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

def buy_item(request, item_id):
    """Handle buying an item - creates transaction and removes from list"""
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    
    if request.method == "POST":
        # Get or create finance profile
        profile, created = FinanceProfile.objects.get_or_create(user=request.user)
        
        # Check if user can afford the item
        if item.can_afford:
            # Create transaction
            category = 'needs' if item.priority else 'wants'
            Transaction.objects.create(
                finance_profile=profile,
                amount=item.price,
                transaction_type='debit',
                category=category,
                description=f"Purchased: {item.name}"
            )
            
            # Update total funds
            profile.total_funds -= item.price
            profile.save()
            
            # Remove item from shopping list
            item_name = item.name
            item.delete()
            
            messages.success(request, f"Successfully purchased '{item_name}' for ₹{item.price}!")
        else:
            messages.error(request, "Cannot afford this item right now. Check your budget!")
    
    return redirect(reverse("widget:shopping"))

def remove_item(request, item_id):
    """Remove item from shopping list without buying"""
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    
    if request.method == "POST":
        item_name = item.name
        item.delete()
        messages.success(request, f"Removed '{item_name}' from your shopping list.")
    
    return redirect(reverse("widget:shopping"))

from django.shortcuts import render,redirect
from django.urls import reverse
from .operations import push_item,list_exists, clean_price_input

# Create your views here.
def home(request):
    return render(request,'widget_home.html')

def shopping_list(request):
    context = {}
    if request.method == "POST":
        item_name = request.POST.get("item-name")
        item_link = request.POST.get("item-link")
        item_price = request.POST.get("item-price")
        item_priority = request.POST.get("item-priority") == "need"
        push_item(request.user, item_name, item_link, item_price, item_priority)
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

def get_smart_tips(profile):
    """Generate smart financial tips based on user's spending patterns"""
    tips = []
    
    if profile.financial_score < 60:
        tips.append("Your spending seems high. Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.")
    
    transactions = profile.transactions.filter(
        created_at__gte=datetime.datetime.now() - datetime.timedelta(days=30)
    )
    
    wants_spending = transactions.filter(category='wants', transaction_type='debit').aggregate(
        total=Sum('amount'))['total'] or 0
    
    if wants_spending > profile.monthly_income * Decimal('0.4'):
        tips.append("Consider reducing entertainment and luxury expenses to improve your financial health.")
    
    savings_rate = profile.transactions.filter(category='savings').aggregate(
        total=Sum('amount'))['total'] or 0
    
    if savings_rate < profile.monthly_income * Decimal('0.15'):
        tips.append("Aim to save at least 15% of your income for emergencies and future goals.")
    
    if profile.total_funds < profile.monthly_income:
        tips.append("Build an emergency fund equal to 3-6 months of expenses for financial security.")
    
    # Shopping list related tips
    shopping_items = ShoppingListItem.objects.filter(user=profile.user)
    if shopping_items.exists():
        affordable_items = [item for item in shopping_items if item.can_afford]
        if affordable_items:
            tips.append(f"🛒 You can afford {len(affordable_items)} items from your shopping list!")
        
        total_shopping_value = sum(float(item.price) for item in shopping_items)
        if total_shopping_value > float(profile.total_funds):
            tips.append("Your shopping list total exceeds your current funds. Prioritize 'needs' over 'wants'.")
    
    if not tips:
        tips.append("Great job! Your financial habits look healthy. Keep up the good work!")
        tips.append("Consider investing your savings for long-term wealth building.")
    
    return tips[:4]  # Return max 4 tips

def finance_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse("main:login"))
    
    # Get or create finance profile
    profile, created = FinanceProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "update_funds":
            total_funds = request.POST.get("total_funds")
            monthly_income = request.POST.get("monthly_income")
            if total_funds and monthly_income:
                try:
                    profile.total_funds = Decimal(str(clean_price_input(total_funds)))
                    profile.monthly_income = Decimal(str(clean_price_input(monthly_income)))
                    profile.save()
                    messages.success(request, "Financial information updated successfully!")
                except (ValueError, TypeError, InvalidOperation):
                    messages.error(request, "Please enter valid amounts.")
        
        elif action == "add_money":
            amount = request.POST.get("amount")
            description = request.POST.get("description")
            category = request.POST.get("category")
            if amount and description and category:
                try:
                    amount_decimal = Decimal(str(clean_price_input(amount)))
                    Transaction.objects.create(
                        finance_profile=profile,
                        amount=amount_decimal,
                        transaction_type='credit',
                        category=category,
                        description=description
                    )
                    profile.total_funds += amount_decimal
                    profile.save()
                    messages.success(request, f"Added ₹{amount_decimal} to your account!")
                except (ValueError, TypeError, InvalidOperation):
                    messages.error(request, "Please enter a valid amount.")
        
        elif action == "deduct_money":
            amount = request.POST.get("amount")
            description = request.POST.get("description")
            category = request.POST.get("category")
            if amount and description and category:
                try:
                    amount_decimal = Decimal(str(clean_price_input(amount)))
                    if profile.total_funds >= amount_decimal:
                        Transaction.objects.create(
                            finance_profile=profile,
                            amount=amount_decimal,
                            transaction_type='debit',
                            category=category,
                            description=description
                        )
                        profile.total_funds -= amount_decimal
                        profile.save()
                        messages.success(request, f"Recorded expense of ₹{amount_decimal}")
                    else:
                        messages.error(request, "Insufficient funds!")
                except (ValueError, TypeError, InvalidOperation):
                    messages.error(request, "Please enter a valid amount.")
        
        elif action == "add_transaction":
            amount = request.POST.get("amount")
            description = request.POST.get("description")
            category = request.POST.get("category")
            transaction_type = request.POST.get("transaction_type")
            if amount and description and category and transaction_type:
                try:
                    amount_decimal = Decimal(str(clean_price_input(amount)))
                    Transaction.objects.create(
                        finance_profile=profile,
                        amount=amount_decimal,
                        transaction_type=transaction_type,
                        category=category,
                        description=description
                    )
                    if transaction_type == 'credit':
                        profile.total_funds += amount_decimal
                    else:
                        profile.total_funds -= amount_decimal
                    profile.save()
                    messages.success(request, "Transaction added successfully!")
                except (ValueError, TypeError, InvalidOperation):
                    messages.error(request, "Please enter a valid amount.")
        
        return redirect(reverse("widget:finance"))
    
    # Get recent transactions
    recent_transactions = profile.transactions.all()[:5]
    
    # Calculate spending by category (last 30 days)
    thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    recent_transactions_month = profile.transactions.filter(created_at__gte=thirty_days_ago)
    
    needs_spent = recent_transactions_month.filter(
        category='needs', transaction_type='debit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    wants_spent = recent_transactions_month.filter(
        category='wants', transaction_type='debit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    savings_amount = recent_transactions_month.filter(
        category='savings', transaction_type='credit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate budget percentages
    budget_allocation = profile.budget_allocation
    if budget_allocation:  # Check if budget_allocation is not empty
        needs_percentage = min(100, (float(needs_spent) / budget_allocation['needs'] * 100)) if budget_allocation.get('needs', 0) > 0 else 0
        wants_percentage = min(100, (float(wants_spent) / budget_allocation['wants'] * 100)) if budget_allocation.get('wants', 0) > 0 else 0
        savings_percentage = min(100, (float(savings_amount) / budget_allocation['savings'] * 100)) if budget_allocation.get('savings', 0) > 0 else 0
    else:
        needs_percentage = wants_percentage = savings_percentage = 0
        budget_allocation = {'needs': 0, 'wants': 0, 'savings': 0}
    
    # Generate smart tips
    smart_tips = get_smart_tips(profile)
    
    # Get shopping list items and their affordability
    shopping_items = ShoppingListItem.objects.filter(user=request.user)
    affordable_items = [item for item in shopping_items if item.can_afford]
    
    context = {
        'total_funds': profile.total_funds,
        'monthly_income': profile.monthly_income,
        'financial_score': profile.financial_score,
        'budget_allocation': budget_allocation,
        'needs_spent': needs_spent,
        'wants_spent': wants_spent,
        'savings_amount': savings_amount,
        'needs_percentage': needs_percentage,
        'wants_percentage': wants_percentage,
        'savings_percentage': savings_percentage,
        'recent_transactions': recent_transactions,
        'smart_tips': smart_tips,
        'affordable_items': affordable_items,
        'total_shopping_items': shopping_items.count(),
    }
    
    return render(request, "finance.html", context)