# qrcode_app/models.py

from django.db import models

class Table(models.Model):
    table_number = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.table_number