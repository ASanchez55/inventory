from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from inventory_app.models import Inventory, StockMovement

from .forms import PurchaseOrderForm
from .models import Brand, Category, Product, PurchaseOrder, PurchaseOrderItem, Supplier
from .services import receive_purchase_order

User = get_user_model()


class PurchaseOrderServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='receiver', password='testpass123')
        self.category = Category.objects.create(name='Laptops')
        self.brand = Brand.objects.create(name='Lenovo')
        self.supplier = Supplier.objects.create(name='Main Supplier')
        self.product = Product.objects.create(
            name='ThinkPad X1',
            sku='TP-X1',
            category=self.category,
            brand=self.brand,
            supplier=self.supplier,
            price=Decimal('1450.00'),
        )
        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            status=PurchaseOrder.STATUS_ORDERED,
            created_by=self.user,
        )
        PurchaseOrderItem.objects.create(
            purchase_order=self.purchase_order,
            product=self.product,
            quantity_ordered=5,
            unit_cost=Decimal('1200.00'),
        )

    def test_receive_purchase_order_updates_inventory_and_status(self):
        receive_purchase_order(self.purchase_order, self.user)

        inventory = Inventory.objects.get(product=self.product)
        stock_movement = StockMovement.objects.get(product=self.product)
        self.purchase_order.refresh_from_db()

        self.assertEqual(inventory.quantity, 5)
        self.assertEqual(stock_movement.movement_type, 'IN')
        self.assertEqual(stock_movement.reference, self.purchase_order.order_number)
        self.assertEqual(self.purchase_order.status, PurchaseOrder.STATUS_RECEIVED)
        self.assertEqual(self.purchase_order.received_by, self.user)
        self.assertIsNotNone(self.purchase_order.received_at)


class PurchaseOrderFormTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name='Date Check Supplier')

    def test_expected_date_cannot_be_earlier_than_order_date(self):
        form = PurchaseOrderForm(
            data={
                'supplier': self.supplier.pk,
                'status': PurchaseOrder.STATUS_DRAFT,
                'order_date': timezone.localdate(),
                'expected_date': timezone.localdate() - timedelta(days=1),
                'notes': '',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('expected_date', form.errors)
