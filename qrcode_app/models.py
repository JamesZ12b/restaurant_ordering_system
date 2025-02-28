# qrcode_app/models.py

from django.db import models

class Floor(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    floor = models.ForeignKey(
        Floor,
        on_delete=models.CASCADE,
        related_name='tables',
        null=True,  # 如果已有数据，先允许为空
        blank=True
    )
    table_number = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    position_x = models.FloatField(default=0.0)  # 新增坐标字段
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

