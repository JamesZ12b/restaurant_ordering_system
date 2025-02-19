# qrcode_app/models.py

from django.db import models

class Table(models.Model):
    table_number = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.table_number

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Main Course', 'Main Course'),
        ('Snack', 'Snack'),
        ('Drink', 'Drink'),
        ('Dessert', 'Dessert'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Main Course')  #

    def __str__(self):
        return self.name