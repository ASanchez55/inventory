from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from inventory_app.models import Inventory
from inventory_app.services import stock_in
from products.models import Brand, Category, Product, Supplier

User = get_user_model()


class ReportsExportViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reporter', password='testpass123')
        permission = Permission.objects.get(codename='access_reports_module')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        category = Category.objects.create(name='Networking')
        brand = Brand.objects.create(name='Cisco')
        supplier = Supplier.objects.create(name='Infra Supplier')
        product = Product.objects.create(
            name='Switch',
            sku='CS-SW1',
            category=category,
            brand=brand,
            supplier=supplier,
            price=Decimal('999.99'),
        )
        Inventory.objects.create(product=product, quantity=0, reorder_level=3)
        stock_in(product, 4, self.user, reference='TEST-EXPORT')

    def test_reports_export_returns_csv_snapshot(self):
        response = self.client.get(reverse('users:reports_export'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')

        content = response.content.decode('utf-8-sig')
        self.assertIn('InventoryHub Reports Export', content)
        self.assertIn('Switch', content)
        self.assertIn('TEST-EXPORT', content)
