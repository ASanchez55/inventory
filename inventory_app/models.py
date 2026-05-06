from django.db import models
from django.conf import settings

# Create your models here.


class Inventory(models.Model):
    product = models.OneToOneField(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="inventory"
    )
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - Stock: {self.quantity}"


class StockMovement(models.Model):
    MOVEMENT_TYPE = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    )

    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.movement_type}: {self.quantity}"
