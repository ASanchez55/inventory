
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate_queryset
from .models import Inventory, StockMovement
from .forms import InventoryForm, StockMovementForm

from inventory_app.services import stock_in, stock_out

from products.models import Category, Brand

from django.db.models import Q, F


# Create your views here.


@login_required
@permission_required('inventory_app.access_inventory_module', raise_exception=True)
def inventory_list(request):
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    brand_id = request.GET.get('brand', '').strip()
    stock_status = request.GET.get('stock_status', '').strip()

    selected_category_id = int(category_id) if category_id.isdigit() else None
    selected_brand_id = int(brand_id) if brand_id.isdigit() else None

    inventory = Inventory.objects.select_related(
        'product',
        'product__category',
        'product__brand',
    ).order_by('product__name')

    if search:
        inventory = inventory.filter(
            Q(product__name__icontains=search) |
            Q(product__sku__icontains=search)
        )

    if category_id:
        inventory = inventory.filter(product__category_id=category_id)

    if brand_id:
        inventory = inventory.filter(product__brand_id=brand_id)

    if stock_status == 'low':
        inventory = inventory.filter(quantity__lte=F('reorder_level'))
    elif stock_status == 'ok':
        inventory = inventory.filter(quantity__gt=F('reorder_level'))

    page_obj, pagination_query = paginate_queryset(request, inventory)

    categories = Category.objects.order_by('name')
    brands = Brand.objects.order_by('name')

    return render(
        request,
        'inventory/inventory_list.html',
        {
            'inventory': page_obj,
            'page_obj': page_obj,
            'categories': categories,
            'brands': brands,
            'search': search,
            'stock_status': stock_status,
            'selected_category': category_id,
            'selected_brand': brand_id,
            'selected_category_id': selected_category_id,
            'selected_brand_id': selected_brand_id,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('inventory_app.access_inventory_module', raise_exception=True)
def inventory_edit(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory updated successfully.')
            return redirect('inventory_app:inventory_list')
    else:
        form = InventoryForm(instance=inventory)

    return render(
        request,
        'inventory/inventory_form.html',
        {
            'form': form,
            'inventory': inventory,
            'page_title': 'Edit Inventory',
            'button_label': 'Save Inventory',
            'product_name': inventory.product.name,
            'sku': inventory.product.sku,

        },
    )


@login_required
@permission_required('inventory_app.access_inventory_module', raise_exception=True)
def stock_movement_list(request):
    search = request.GET.get('search', '').strip()
    movements = StockMovement.objects.select_related(
        'product', 'user').order_by('-created_at')

    if search:
        movements = movements.filter(
            Q(product__name__icontains=search)
            | Q(product__sku__icontains=search)
            | Q(reference__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(movement_type__icontains=search)
        )

    page_obj, pagination_query = paginate_queryset(request, movements)

    return render(
        request,
        'inventory/stock_movement_list.html',
        {
            'movements': page_obj,
            'page_obj': page_obj,
            'search': search,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('inventory_app.access_inventory_module', raise_exception=True)
def stock_in_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            reference = form.cleaned_data['reference']
            stock_in(inventory.product, quantity, request.user, reference)
            messages.success(request, 'Stock added successfully.')
            return redirect('inventory_app:inventory_list')
    else:
        form = StockMovementForm()

    return render(
        request,
        'inventory/stock_movement_form.html',
        {
            'form': form,
            'page_title': f'Stock In - {inventory.product.name}',
            'button_label': 'Add Stock'
        },
    )


@login_required
@permission_required('inventory_app.access_inventory_module', raise_exception=True)
def stock_out_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            reference = form.cleaned_data['reference']
            try:
                stock_out(inventory.product, quantity, request.user, reference)
                messages.success(request, 'Stock removed successfully.')
            except ValueError as e:
                messages.error(request, str(e))
            return redirect('inventory_app:inventory_list')
    else:
        form = StockMovementForm()

    return render(
        request,
        'inventory/stock_movement_form.html',
        {
            'form': form,
            'page_title': f'Stock Out - {inventory.product.name}',
            'button_label': 'Remove Stock'
        },
    )
