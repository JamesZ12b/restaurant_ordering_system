from django.db import models  
from django.core.validators import MinValueValidator  


class Floor(models.Model):  
    name = models.CharField(max_length=50)  

    def __str__(self):  
        return self.name  


class Table(models.Model):  
    floor = models.ForeignKey(  
        Floor,  
        on_delete=models.CASCADE,  
        related_name='tables',  
        null=True,  
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
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])  
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)  
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Main Course')  

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
    items = models.JSONField()  
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  
    stripe_payment_intent = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:  
        indexes = [  
            models.Index(fields=['table']),  
            models.Index(fields=['created_at']),  
        ]  

    def __str__(self):  
        return f"Order {self.id} - Table {self.table.table_number}"  