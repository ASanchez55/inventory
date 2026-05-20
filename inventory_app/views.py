
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Inventory, StockMovement
from .forms import InventoryForm, StockMovementForm

from inventory_app.services import stock_in, stock_out

# Create your views here.


@login_required
def inventory_list(request):
    inventory = Inventory.objects.select_related('product').all()
    return render(request, 'inventory/inventory_list.html', {'inventory': inventory})


@login_required
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
def stock_movement_list(request):
    movements = StockMovement.objects.select_related(
        'product', 'user').order_by('-created_at')
    return render(request, 'inventory/stock_movement_list.html', {'movements': movements})


@login_required
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
