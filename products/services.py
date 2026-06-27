from django.db import transaction
from django.utils import timezone

from inventory_app.models import Inventory
from inventory_app.services import stock_in

from .models import Product, PurchaseOrder


def create_product(name, sku, category, brand, supplier, price):
    with transaction.atomic():
        product = Product.objects.create(
            name=name,
            sku=sku,
            category=category,
            brand=brand,
            supplier=supplier,
            price=price,
        )
        Inventory.objects.create(product=product)

    return product


def save_purchase_order(form, formset, user):
    with transaction.atomic():
        purchase_order = form.save(commit=False)
        if purchase_order.pk is None:
            purchase_order.created_by = user
        purchase_order.save()
        form.save_m2m()

        formset.instance = purchase_order
        formset.save()

    return purchase_order


def receive_purchase_order(purchase_order, user):
    if purchase_order.status == PurchaseOrder.STATUS_RECEIVED:
        raise ValueError('This purchase order has already been received.')

    if purchase_order.status == PurchaseOrder.STATUS_CANCELLED:
        raise ValueError('Cancelled purchase orders cannot be received.')

    items = list(purchase_order.items.select_related('product'))
    if not items:
        raise ValueError('Add at least one item before receiving this purchase order.')

    with transaction.atomic():
        for item in items:
            stock_in(
                product=item.product,
                quantity=item.quantity_ordered,
                user=user,
                reference=purchase_order.order_number,
            )

        purchase_order.status = PurchaseOrder.STATUS_RECEIVED
        purchase_order.received_by = user
        purchase_order.received_at = timezone.now()
        purchase_order.save(
            update_fields=['status', 'received_by', 'received_at', 'updated_at'],
        )

    return purchase_order
