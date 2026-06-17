from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=128, unique=True)
    contact_person = models.CharField(max_length=128, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    lead_time_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        permissions = [
            ('access_suppliers_module', 'Can access suppliers module'),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=64)
    sku = models.CharField(max_length=64, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        permissions = [
            ('access_products_module', 'Can access products module'),
        ]
