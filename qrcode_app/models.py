# qrcode_app/models.py

from django.db import models

class Table(models.Model):
    table_number = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def __str__(self):
        return f"Table {self.table_number}"

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Main Course', 'Main Course'),
        ('Snack', 'Snack'),
        ('Drink', 'Drink'),
        ('Dessert', 'Dessert'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='menu_items/', null=True)
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    items = models.JSONField()  # Store cart items as JSON
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - Table {self.table.table_number}"
