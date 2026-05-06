from django.db import transaction

from .models import Product
from inventory_app.models import Inventory


def create_product(name, sku, category, brand, price):
    with transaction.atomic():
        product = Product.objects.create(
            name=name,
            sku=sku,
            category=category,
            brand=brand,
            price=price,
        )
        Inventory.objects.create(product=product)

    return product
