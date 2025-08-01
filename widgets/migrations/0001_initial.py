# Generated by Django 5.2.4 on 2025-07-25 09:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingListItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('link', models.URLField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
