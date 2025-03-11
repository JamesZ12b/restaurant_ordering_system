# qrcode_app/models.py

from django.db import models


class Floor(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Table(models.Model):
    floor = models.ForeignKey(
        Floor,
        on_delete=models.CASCADE,
        related_name='tables',
        null=True,        # 允许为空以兼容已有数据
        blank=True
    )
    table_number = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)

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

class KitchenOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', '待处理'), ('preparing', '准备中'), ('completed', '已完成'), ('cancelled', '已取消')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order.id} - Status: {self.status}"