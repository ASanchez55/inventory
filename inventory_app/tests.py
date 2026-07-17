from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from products.models import Brand, Category, Product, Supplier

from .models import Inventory

User = get_user_model()


class InventoryExportViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='inventoryexport', password='testpass123')
        permission = Permission.objects.get(codename='access_inventory_module')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        category = Category.objects.create(name='Hardware')
        brand = Brand.objects.create(name='HP')
        supplier = Supplier.objects.create(name='Warehouse Supplier')
        low_product = Product.objects.create(
            name='Printer',
            sku='HP-P1',
            category=category,
            brand=brand,
            supplier=supplier,
            price=Decimal('250.00'),
        )
        ok_product = Product.objects.create(
            name='Scanner',
            sku='HP-S1',
            category=category,
            brand=brand,
            supplier=supplier,
            price=Decimal('210.00'),
        )
        Inventory.objects.create(product=low_product, quantity=2, reorder_level=5)
        Inventory.objects.create(product=ok_product, quantity=9, reorder_level=5)

    def test_inventory_export_respects_stock_status_filter(self):
        response = self.client.get(
            reverse('inventory_app:inventory_export'),
            {'stock_status': 'low'},
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8-sig')
        self.assertIn('Printer', content)
        self.assertNotIn('Scanner', content)
