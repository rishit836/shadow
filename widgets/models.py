from django.db import models
from django.contrib.auth.models import User

class ShoppingListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_list')
    name = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.user.username})"