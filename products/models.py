from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=64)


class Brand(models.Model):
    name = models.CharField(max_length=64)


class Product(models.Model):
    name = models.CharField(max_length=64)
    sku = models.CharField(max_length=64, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
