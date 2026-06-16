from datetime import timedelta

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.utils import timezone

from inventory_app.models import Inventory, StockMovement
from products.models import Brand, Category, Product


def build_reports_snapshot():
    thirty_days_ago = timezone.now() - timedelta(days=30)
    inventory_value_expression = ExpressionWrapper(
        F('quantity') * F('product__price'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    totals = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_brands': Brand.objects.count(),
        'units_in_stock': Inventory.objects.aggregate(total=Sum('quantity'))['total'] or 0,
        'inventory_value': Inventory.objects.aggregate(total=Sum(inventory_value_expression))['total'] or 0,
        'low_stock_count': Inventory.objects.filter(quantity__lte=F('reorder_level')).count(),
        'out_of_stock_count': Inventory.objects.filter(quantity=0).count(),
    }

    movement_summary = StockMovement.objects.filter(created_at__gte=thirty_days_ago).aggregate(
        stock_in_count=Count('id', filter=Q(movement_type='IN')),
        stock_out_count=Count('id', filter=Q(movement_type='OUT')),
    )

    top_stocked_items = list(
        Inventory.objects.select_related('product')
        .order_by('-quantity', 'product__name')[:5]
    )
    low_stock_items = list(
        Inventory.objects.select_related('product')
        .filter(quantity__lte=F('reorder_level'))
        .order_by('quantity', 'product__name')[:5]
    )
    recent_movements = list(
        StockMovement.objects.select_related('product', 'user')
        .order_by('-created_at')[:5]
    )
    category_breakdown = list(
        Category.objects.annotate(product_count=Count('product'))
        .filter(product_count__gt=0)
        .order_by('-product_count', 'name')[:5]
    )

    return {
        **totals,
        'stock_in_count': movement_summary['stock_in_count'] or 0,
        'stock_out_count': movement_summary['stock_out_count'] or 0,
        'top_stocked_items': top_stocked_items,
        'low_stock_items': low_stock_items,
        'recent_movements': recent_movements,
        'category_breakdown': category_breakdown,
        'window_label': 'Last 30 days',
    }
