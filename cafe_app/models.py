from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('netbanking', 'NetBanking'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    
    customer_name = models.CharField(max_length=100, blank=True, default='Guest')
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_email = models.EmailField(blank=True)
    
    items = models.TextField()  # JSON format: item names and quantities
    subtotal = models.FloatField()
    gst = models.FloatField()
    total_amount = models.FloatField()
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.total_amount} - {self.status}"


class OrderError(models.Model):
    STATUS_CHOICES = [
        ('invalid', 'Invalid'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = Order.PAYMENT_METHOD_CHOICES

    customer_name = models.CharField(max_length=100, blank=True, default='Guest')
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_email = models.EmailField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    items = models.TextField(blank=True)
    subtotal = models.FloatField(null=True, blank=True)
    gst = models.FloatField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    error_message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='failed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OrderError #{self.id} - {self.status} - {self.error_message[:40]}"
