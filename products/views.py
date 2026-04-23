from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm
from .models import Category


@login_required
def category_list(request):
    categories = Category.objects.order_by('name')
    return render(request, 'products/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('products:category_list')
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
