from django.db import transaction
from .models import Inventory, StockMovement


def stock_in(product, quantity, user, reference=None):
    inventory, _ = Inventory.objects.get_or_create(product=product)

    with transaction.atomic():
        inventory.quantity += quantity
        inventory.save()

        StockMovement.objects.create(
            product=product,
            user=user,
            movement_type="IN",
            quantity=quantity,
            reference=reference
        )


def stock_out(product, quantity, user, reference=None):
    inventory = Inventory.objects.get(product=product)

    if inventory.quantity < quantity:
        raise ValueError("Not enough stock")

    with transaction.atomic():
        inventory.quantity -= quantity
        inventory.save()

        StockMovement.objects.create(
            product=product,
            user=user,
            movement_type="OUT",
            quantity=quantity,
            reference=reference
        )
