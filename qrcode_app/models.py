# qrcode_app/models.py

from django.db import models

class Table(models.Model):
    table_number = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.table_number

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='menu_photos/')

    def __str__(self):
        return self.name