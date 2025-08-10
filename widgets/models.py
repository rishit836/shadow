from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import json

class ShoppingListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_list')
    name = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    priority = models.BooleanField(default=False, verbose_name="Is Need?")

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    @property
    def can_afford(self):
        """Check if user can afford this item based on their budget"""
        try:
            profile = FinanceProfile.objects.get(user=self.user)
            budget = profile.budget_allocation
            category = 'needs' if self.priority else 'wants'
            
            # Get spending in this category for current month
            from django.db.models import Sum
            import datetime
            thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
            
            spent_this_month = Transaction.objects.filter(
                finance_profile=profile,
                category=category,
                transaction_type='debit',
                created_at__gte=thirty_days_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            remaining_budget = budget.get(category, 0) - float(spent_this_month)
            return remaining_budget >= float(self.price) and profile.total_funds >= self.price
        except:
            return False
    
    @property
    def affordability_message(self):
        """Get message about affordability status"""
        if self.can_afford:
            return "✅ You can afford this!"
        else:
            try:
                profile = FinanceProfile.objects.get(user=self.user)
                if profile.total_funds < self.price:
                    return "❌ Insufficient funds"
                else:
                    return "⚠️ Over budget for this category"
            except:
                return "❌ Set up your finance profile first"

class FinanceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="finance_profile")
    total_funds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.total_funds}"

    @property
    def budget_allocation(self):
        """Smart budget allocation based on best practices"""
        if self.monthly_income <= 0:
            return {}
        
        income = float(self.monthly_income)
        return {
            'needs': round(income * 0.50, 2),  # 50% for needs
            'wants': round(income * 0.30, 2),  # 30% for wants
            'savings': round(income * 0.20, 2),  # 20% for savings/investments
        }

    @property
    def financial_score(self):
        """Calculate financial health score out of 100"""
        transactions = self.transactions.all()
        if not transactions:
            return 75  # Default score for new users
        
        # Calculate spending patterns
        needs_spending = sum(float(t.amount) for t in transactions.filter(category='needs', transaction_type='debit'))
        wants_spending = sum(float(t.amount) for t in transactions.filter(category='wants', transaction_type='debit'))
        savings = sum(float(t.amount) for t in transactions.filter(category='savings', transaction_type='credit'))
        
        total_spending = needs_spending + wants_spending
        if total_spending == 0:
            return 75
        
        # Score calculation based on spending patterns
        needs_ratio = needs_spending / total_spending if total_spending > 0 else 0
        wants_ratio = wants_spending / total_spending if total_spending > 0 else 0
        savings_ratio = savings / float(self.monthly_income) if self.monthly_income > 0 else 0
        
        score = 0
        # Good needs spending (40-60% of income)
        if 0.4 <= needs_ratio <= 0.6:
            score += 40
        else:
            score += max(0, 40 - abs(needs_ratio - 0.5) * 80)
        
        # Controlled wants spending (20-35% of income)
        if 0.2 <= wants_ratio <= 0.35:
            score += 30
        else:
            score += max(0, 30 - abs(wants_ratio - 0.275) * 100)
        
        # Good savings rate (15%+ of income)
        if savings_ratio >= 0.15:
            score += 30
        else:
            score += savings_ratio * 200  # Scale to 30 points max
        
        return min(100, max(0, round(score)))

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    CATEGORIES = [
        ('needs', 'Needs'),
        ('wants', 'Wants'),
        ('savings', 'Savings'),
    ]
    
    finance_profile = models.ForeignKey(FinanceProfile, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=10, choices=CATEGORIES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        sign = '+' if self.transaction_type == 'credit' else '-'
        return f"{sign}₹{self.amount} - {self.description}"

# Keep the old finance model for backward compatibility
class finance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="finance")
    funds = models.DecimalField(max_digits=10 ,decimal_places=2,default=0)

    def __str__(self):
        return f"{self.user} has {self.funds} bucks"