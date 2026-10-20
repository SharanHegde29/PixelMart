from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    stock = models.IntegerField(default=10)
    
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('audio', 'Audio'),
        ('computers', 'Computers & Laptops'),
        ('gaming', 'Gaming'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='electronics')

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20, 
        default='Pending', 
        choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed')]
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.status})"