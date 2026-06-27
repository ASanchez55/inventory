from decimal import Decimal
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

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

    def __str__(self):
        return f'{self.name} ({self.sku})'


class PurchaseOrder(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_ORDERED = 'ORDERED'
    STATUS_RECEIVED = 'RECEIVED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_ORDERED, 'Ordered'),
        (STATUS_RECEIVED, 'Received'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    order_date = models.DateField(default=timezone.localdate)
    expected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_purchase_orders',
        null=True,
        blank=True,
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='received_purchase_orders',
        null=True,
        blank=True,
    )
    received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('access_purchase_orders_module', 'Can access purchase orders module'),
        ]

    def __str__(self):
        return self.order_number

    @property
    def total_amount(self):
        return sum(
            (item.line_total for item in self.items.all()),
            Decimal('0.00'),
        )

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_order_number(cls):
        while True:
            candidate = f"PO-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
            if not cls.objects.filter(order_number=candidate).exists():
                return candidate


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_ordered = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.purchase_order.order_number} - {self.product.name}'

    @property
    def line_total(self):
        return self.quantity_ordered * self.unit_cost
