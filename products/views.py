from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate_queryset
from .forms import BrandForm, CategoryForm, ProductForm
from .models import Category, Brand, Product

from products.services import create_product

from django.db.models import Q


def _build_lookup_payload(obj):
    return {
        'id': obj.pk,
        'name': obj.name,
    }

# Category views


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def category_list(request):
    search = request.GET.get('search', '').strip()
    categories = Category.objects.order_by('name')

    if search:
        categories = categories.filter(name__icontains=search)

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
    brands = Brand.objects.order_by('name')

    if search:
        brands = brands.filter(name__icontains=search)

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

# product views


@login_required
@permission_required('products.access_products_module', raise_exception=True)
def product_list(request):
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    brand_id = request.GET.get('brand', '').strip()
    selected_category_id = int(category_id) if category_id.isdigit() else None
    selected_brand_id = int(brand_id) if brand_id.isdigit() else None

    products = Product.objects.select_related(
        'category', 'brand').order_by('name')

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if brand_id:
        products = products.filter(brand_id=brand_id)

    page_obj, pagination_query = paginate_queryset(request, products)

    categories = Category.objects.order_by('name')
    brands = Brand.objects.order_by('name')

    return render(
        request,
        'products/product_list.html',
        {
            'page_obj': page_obj,
            'products': page_obj,
            'categories': categories,
            'brands': brands,
            'search': search,
            'selected_category': category_id,
            'selected_brand': brand_id,
            'selected_category_id': selected_category_id,
            'selected_brand_id': selected_brand_id,
            'pagination_query': pagination_query,
        },
    )


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
