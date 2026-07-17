from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.exporting import build_csv_response
from core.utils import paginate_queryset

from .forms import (
    BrandForm,
    CategoryForm,
    ProductForm,
    PurchaseOrderForm,
    PurchaseOrderItemFormSet,
    SupplierForm,
)
from .models import Brand, Category, Product, PurchaseOrder, Supplier
from .services import create_product, receive_purchase_order, save_purchase_order


def _build_lookup_payload(obj):
    return {
        'id': obj.pk,
        'name': obj.name,
    }


def _purchase_order_form_context(form, formset, page_title, button_label, purchase_order=None):
    return {
        'form': form,
        'formset': formset,
        'purchase_order': purchase_order,
        'page_title': page_title,
        'button_label': button_label,
        'has_products': Product.objects.exists(),
        'has_suppliers': Supplier.objects.exists(),
    }


def _get_category_queryset(search=''):
    categories = Category.objects.order_by('name')
    if search:
        categories = categories.filter(name__icontains=search)
    return categories


def _get_brand_queryset(search=''):
    brands = Brand.objects.order_by('name')
    if search:
        brands = brands.filter(name__icontains=search)
    return brands


def _get_supplier_queryset(search=''):
    suppliers = Supplier.objects.order_by('name')
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search)
            | Q(contact_person__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )
    return suppliers


def _get_product_queryset(search='', category_id='', brand_id='', supplier_id=''):
    products = Product.objects.select_related(
        'category',
        'brand',
        'supplier',
    ).order_by('name')

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(sku__icontains=search)
            | Q(supplier__name__icontains=search)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if brand_id:
        products = products.filter(brand_id=brand_id)

    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    return products


def _get_purchase_order_queryset(search='', status=''):
    purchase_orders = PurchaseOrder.objects.select_related(
        'supplier',
        'created_by',
        'received_by',
    ).prefetch_related('items__product')

    if search:
        purchase_orders = purchase_orders.filter(
            Q(order_number__icontains=search)
            | Q(supplier__name__icontains=search)
            | Q(notes__icontains=search)
        )

    if status:
        purchase_orders = purchase_orders.filter(status=status)

    return purchase_orders


# Category views
@login_required
@permission_required('products.access_products_module', raise_exception=True)
def category_list(request):
    search = request.GET.get('search', '').strip()
    categories = _get_category_queryset(search)

    page_obj, pagination_query = paginate_queryset(request, categories)

    return render(
        request,
        'products/category_list.html',
        {
            'categories': page_obj,
            'page_obj': page_obj,
            'search': search,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(
                    {'success': True, 'category': _build_lookup_payload(category)},
                    status=201,
                )
            messages.success(request, 'Category added successfully.')
            return redirect('products:category_list')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = CategoryForm()

    return render(
        request,
        'products/category_form.html',
        {
            'form': form,
            'page_title': 'Add Category',
            'button_label': 'Save Category',
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('products:category_list')
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        'products/category_form.html',
        {
            'form': form,
            'category': category,
            'page_title': 'Edit Category',
            'button_label': 'Update Category',
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('products:category_list')

    return render(
        request,
        'products/category_confirm_delete.html',
        {'category': category},
    )


# Brand views
@login_required
@permission_required('products.access_products_module', raise_exception=True)
def brand_list(request):
    search = request.GET.get('search', '').strip()
    brands = _get_brand_queryset(search)

    page_obj, pagination_query = paginate_queryset(request, brands)

    return render(
        request,
        'products/brand_list.html',
        {
            'brands': page_obj,
            'page_obj': page_obj,
            'search': search,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            brand = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(
                    {'success': True, 'brand': _build_lookup_payload(brand)},
                    status=201,
                )
            messages.success(request, 'Brand added successfully.')
            return redirect('products:brand_list')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = BrandForm()

    return render(
        request,
        'products/brand_form.html',
        {
            'form': form,
            'page_title': 'Add Brand',
            'button_label': 'Save Brand',
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated successfully.')
            return redirect('products:brand_list')
    else:
        form = BrandForm(instance=brand)

    return render(
        request,
        'products/brand_form.html',
        {
            'form': form,
            'brand': brand,
            'page_title': 'Edit Brand',
            'button_label': 'Update Brand',
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Brand deleted successfully.')
        return redirect('products:brand_list')

    return render(
        request,
        'products/brand_confirm_delete.html',
        {'brand': brand},
    )


# Supplier views
@login_required
@permission_required('products.access_suppliers_module', raise_exception=True)
def supplier_list(request):
    search = request.GET.get('search', '').strip()
    suppliers = _get_supplier_queryset(search)

    page_obj, pagination_query = paginate_queryset(request, suppliers)

    return render(
        request,
        'products/supplier_list.html',
        {
            'suppliers': page_obj,
            'page_obj': page_obj,
            'search': search,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('products.access_suppliers_module', raise_exception=True)
def supplier_export(request):
    search = request.GET.get('search', '').strip()
    suppliers = _get_supplier_queryset(search)

    rows = [
        ['Name', 'Contact Person', 'Email', 'Phone', 'Lead Time (Days)', 'Notes'],
    ]
    rows.extend(
        [
            supplier.name,
            supplier.contact_person,
            supplier.email,
            supplier.phone,
            supplier.lead_time_days,
            supplier.notes,
        ]
        for supplier in suppliers
    )
    return build_csv_response('suppliers', rows)


@login_required
@permission_required('products.access_suppliers_module', raise_exception=True)
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully.')
            return redirect('products:supplier_list')
    else:
        form = SupplierForm()

    return render(
        request,
        'products/supplier_form.html',
        {
            'form': form,
            'page_title': 'Add Supplier',
            'button_label': 'Save Supplier',
        },
    )


@login_required
@permission_required('products.access_suppliers_module', raise_exception=True)
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('products:supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(
        request,
        'products/supplier_form.html',
        {
            'form': form,
            'supplier': supplier,
            'page_title': 'Edit Supplier',
            'button_label': 'Update Supplier',
        },
    )


@login_required
@permission_required('products.access_suppliers_module', raise_exception=True)
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('products:supplier_list')

    return render(
        request,
        'products/supplier_confirm_delete.html',
        {'supplier': supplier},
    )


# Product views
@login_required
@permission_required('products.access_products_module', raise_exception=True)
def product_list(request):
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    brand_id = request.GET.get('brand', '').strip()
    supplier_id = request.GET.get('supplier', '').strip()
    selected_category_id = int(category_id) if category_id.isdigit() else None
    selected_brand_id = int(brand_id) if brand_id.isdigit() else None
    selected_supplier_id = int(supplier_id) if supplier_id.isdigit() else None

    products = _get_product_queryset(search, category_id, brand_id, supplier_id)

    page_obj, pagination_query = paginate_queryset(request, products)

    categories = Category.objects.order_by('name')
    brands = Brand.objects.order_by('name')
    suppliers = Supplier.objects.order_by('name')

    return render(
        request,
        'products/product_list.html',
        {
            'page_obj': page_obj,
            'products': page_obj,
            'categories': categories,
            'brands': brands,
            'suppliers': suppliers,
            'search': search,
            'selected_category': category_id,
            'selected_brand': brand_id,
            'selected_supplier': supplier_id,
            'selected_category_id': selected_category_id,
            'selected_brand_id': selected_brand_id,
            'selected_supplier_id': selected_supplier_id,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def product_export(request):
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    brand_id = request.GET.get('brand', '').strip()
    supplier_id = request.GET.get('supplier', '').strip()
    products = _get_product_queryset(search, category_id, brand_id, supplier_id)

    rows = [
        ['Name', 'SKU', 'Category', 'Brand', 'Supplier', 'Price'],
    ]
    rows.extend(
        [
            product.name,
            product.sku,
            product.category.name,
            product.brand.name,
            product.supplier.name if product.supplier else '',
            f'{product.price:.2f}',
        ]
        for product in products
    )
    return build_csv_response('products', rows)


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            create_product(
                name=form.cleaned_data['name'],
                sku=form.cleaned_data['sku'],
                category=form.cleaned_data['category'],
                brand=form.cleaned_data['brand'],
                supplier=form.cleaned_data['supplier'],
                price=form.cleaned_data['price'],
            )
            messages.success(request, 'Product added successfully.')
            return redirect('products:product_list')
    else:
        form = ProductForm()

    return render(
        request,
        'products/product_form.html',
        {
            'form': form,
            'page_title': 'Add Product',
            'button_label': 'Save Product',
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'products/product_form.html',
        {
            'form': form,
            'product': product,
            'page_title': 'Edit Product',
            'button_label': 'Update Product',
        },
    )


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('products:product_list')

    return render(
        request,
        'products/product_confirm_delete.html',
        {'product': product},
    )


# Purchase order views
@login_required
@permission_required('products.access_purchase_orders_module', raise_exception=True)
def purchase_order_list(request):
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    status_choices = PurchaseOrder.STATUS_CHOICES
    valid_statuses = {value for value, _label in status_choices}
    selected_status = status if status in valid_statuses else ''
    purchase_orders = _get_purchase_order_queryset(search, selected_status)

    page_obj, pagination_query = paginate_queryset(request, purchase_orders)

    return render(
        request,
        'products/purchase_order_list.html',
        {
            'purchase_orders': page_obj,
            'page_obj': page_obj,
            'search': search,
            'status_choices': status_choices,
            'selected_status': selected_status,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('products.access_purchase_orders_module', raise_exception=True)
def purchase_order_export(request):
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    valid_statuses = {value for value, _label in PurchaseOrder.STATUS_CHOICES}
    selected_status = status if status in valid_statuses else ''
    purchase_orders = _get_purchase_order_queryset(search, selected_status)

    rows = [
        [
            'Order Number',
            'Supplier',
            'Status',
            'Order Date',
            'Expected Date',
            'Items',
            'Total Amount',
            'Created By',
            'Received By',
            'Received At',
        ],
    ]
    rows.extend(
        [
            purchase_order.order_number,
            purchase_order.supplier.name,
            purchase_order.get_status_display(),
            purchase_order.order_date.isoformat(),
            purchase_order.expected_date.isoformat() if purchase_order.expected_date else '',
            purchase_order.items.count(),
            f'{purchase_order.total_amount:.2f}',
            purchase_order.created_by.username if purchase_order.created_by else '',
            purchase_order.received_by.username if purchase_order.received_by else '',
            purchase_order.received_at.strftime('%Y-%m-%d %H:%M:%S')
            if purchase_order.received_at
            else '',
        ]
        for purchase_order in purchase_orders
    )
    return build_csv_response('purchase_orders', rows)


@login_required
@permission_required('products.access_purchase_orders_module', raise_exception=True)
def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            purchase_order = save_purchase_order(form, formset, request.user)
            messages.success(
                request,
                f'Purchase order {purchase_order.order_number} created successfully.',
            )
            return redirect('products:purchase_order_detail', pk=purchase_order.pk)
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet(prefix='items')

    return render(
        request,
        'products/purchase_order_form.html',
        _purchase_order_form_context(
            form=form,
            formset=formset,
            page_title='Create Purchase Order',
            button_label='Save Purchase Order',
        ),
    )


@login_required
@permission_required('products.access_purchase_orders_module', raise_exception=True)
def purchase_order_detail(request, pk):
    purchase_order = get_object_or_404(
        PurchaseOrder.objects.select_related(
            'supplier',
            'created_by',
            'received_by',
        ).prefetch_related('items__product'),
        pk=pk,
    )

    return render(
        request,
        'products/purchase_order_detail.html',
        {
            'purchase_order': purchase_order,
            'can_receive': purchase_order.status in {
                PurchaseOrder.STATUS_DRAFT,
                PurchaseOrder.STATUS_ORDERED,
            },
        },
    )


@login_required
@permission_required('products.access_purchase_orders_module', raise_exception=True)
def purchase_order_update(request, pk):
    purchase_order = get_object_or_404(
        PurchaseOrder.objects.prefetch_related('items__product'),
        pk=pk,
    )

    if purchase_order.status == PurchaseOrder.STATUS_RECEIVED:
        messages.warning(request, 'Received purchase orders can no longer be edited.')
        return redirect('products:purchase_order_detail', pk=purchase_order.pk)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        formset = PurchaseOrderItemFormSet(
            request.POST,
            instance=purchase_order,
            prefix='items',
        )
        if form.is_valid() and formset.is_valid():
            purchase_order = save_purchase_order(form, formset, request.user)
            messages.success(
                request,
                f'Purchase order {purchase_order.order_number} updated successfully.',
            )
            return redirect('products:purchase_order_detail', pk=purchase_order.pk)
    else:
        form = PurchaseOrderForm(instance=purchase_order)
        formset = PurchaseOrderItemFormSet(instance=purchase_order, prefix='items')

    return render(
        request,
        'products/purchase_order_form.html',
        _purchase_order_form_context(
            form=form,
            formset=formset,
            purchase_order=purchase_order,
            page_title=f'Edit {purchase_order.order_number}',
            button_label='Update Purchase Order',
        ),
    )


@login_required
@permission_required('products.access_purchase_orders_module', raise_exception=True)
@require_POST
def purchase_order_receive(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    try:
        receive_purchase_order(purchase_order, request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(
            request,
            f'Purchase order {purchase_order.order_number} was received successfully.',
        )

    return redirect('products:purchase_order_detail', pk=purchase_order.pk)


@login_required
@permission_required('products.access_purchase_orders_module', raise_exception=True)
def purchase_order_delete(request, pk):
    purchase_order = get_object_or_404(
        PurchaseOrder.objects.select_related('supplier'),
        pk=pk,
    )

    if purchase_order.status == PurchaseOrder.STATUS_RECEIVED:
        messages.warning(request, 'Received purchase orders cannot be deleted.')
        return redirect('products:purchase_order_detail', pk=purchase_order.pk)

    if request.method == 'POST':
        order_number = purchase_order.order_number
        purchase_order.delete()
        messages.success(request, f'Purchase order {order_number} deleted successfully.')
        return redirect('products:purchase_order_list')

    return render(
        request,
        'products/purchase_order_confirm_delete.html',
        {'purchase_order': purchase_order},
    )
