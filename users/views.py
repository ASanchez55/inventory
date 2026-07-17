from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.exporting import build_csv_response
from core.reporting import build_reports_snapshot
from core.utils import paginate_queryset
from .forms import RegisterForm, UserAccessForm

User = get_user_model()


def _get_user_queryset(search=''):
    users = User.objects.order_by('username')
    if search:
        users = users.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )
    return users


def _get_user_display(user):
    if not user:
        return ''
    return user.get_full_name() or user.username


@login_required
def dashboard(request):
    context = {}
    if request.user.has_perm('users.access_reports_module'):
        context['reports_snapshot'] = build_reports_snapshot()
    return render(request, 'accounts/dashboard.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            messages.success(
                request,
                'Account created successfully. An administrator must activate your account before you can log in.',
            )
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@permission_required('users.access_users_module', raise_exception=True)
def user_list(request):
    search = request.GET.get('search', '').strip()
    users = _get_user_queryset(search)

    page_obj, pagination_query = paginate_queryset(request, users)
    user_rows = [
        {
            'user': managed_user,
            'has_products_access': managed_user.has_perm('products.access_products_module'),
            'has_suppliers_access': managed_user.has_perm('products.access_suppliers_module'),
            'has_purchase_orders_access': managed_user.has_perm(
                'products.access_purchase_orders_module',
            ),
            'has_inventory_access': managed_user.has_perm('inventory_app.access_inventory_module'),
            'has_users_access': managed_user.has_perm('users.access_users_module'),
            'has_reports_access': managed_user.has_perm('users.access_reports_module'),
        }
        for managed_user in page_obj
    ]
    return render(
        request,
        'accounts/user_list.html',
        {
            'user_rows': user_rows,
            'page_obj': page_obj,
            'search': search,
            'pagination_query': pagination_query,
        },
    )


@login_required
@permission_required('users.access_users_module', raise_exception=True)
def user_export(request):
    search = request.GET.get('search', '').strip()
    users = _get_user_queryset(search)

    rows = [
        [
            'Username',
            'Full Name',
            'Email',
            'Status',
            'Products',
            'Suppliers',
            'Purchase Orders',
            'Inventory',
            'Reports',
            'Users',
        ],
    ]
    rows.extend(
        [
            managed_user.username,
            managed_user.get_full_name(),
            managed_user.email,
            'Active' if managed_user.is_active else 'Pending',
            'Yes' if managed_user.has_perm('products.access_products_module') else 'No',
            'Yes' if managed_user.has_perm('products.access_suppliers_module') else 'No',
            'Yes' if managed_user.has_perm('products.access_purchase_orders_module') else 'No',
            'Yes' if managed_user.has_perm('inventory_app.access_inventory_module') else 'No',
            'Yes' if managed_user.has_perm('users.access_reports_module') else 'No',
            'Yes' if managed_user.has_perm('users.access_users_module') else 'No',
        ]
        for managed_user in users
    )
    return build_csv_response('users_access', rows)


@login_required
@permission_required('users.access_users_module', raise_exception=True)
def user_access_update(request, pk):
    managed_user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserAccessForm(request.POST, instance=managed_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Access updated for {managed_user.username}.')
            return redirect('users:user_list')
    else:
        form = UserAccessForm(instance=managed_user)

    return render(
        request,
        'accounts/user_access_form.html',
        {
            'form': form,
            'managed_user': managed_user,
            'page_title': f'Manage Access - {managed_user.username}',
            'button_label': 'Save Access',
        },
    )


@login_required
@permission_required('users.access_reports_module', raise_exception=True)
def reports(request):
    return render(
        request,
        'accounts/reports.html',
        {'reports_snapshot': build_reports_snapshot()},
    )


@login_required
@permission_required('users.access_reports_module', raise_exception=True)
def reports_export(request):
    snapshot = build_reports_snapshot()
    generated_at = timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')

    rows = [
        ['InventoryHub Reports Export'],
        ['Generated At', generated_at],
        [],
        ['Summary Metric', 'Value'],
        ['Total Products', snapshot['total_products']],
        ['Total Categories', snapshot['total_categories']],
        ['Total Brands', snapshot['total_brands']],
        ['Total Suppliers', snapshot['total_suppliers']],
        ['Units In Stock', snapshot['units_in_stock']],
        ['Inventory Value', f"{snapshot['inventory_value']:.2f}"],
        ['Low Stock Count', snapshot['low_stock_count']],
        ['Out Of Stock Count', snapshot['out_of_stock_count']],
        [f"Stock In Count {snapshot['window_label']}", snapshot['stock_in_count']],
        [f"Stock Out Count {snapshot['window_label']}", snapshot['stock_out_count']],
        [],
        ['Top Stocked Items'],
        ['Product', 'SKU', 'Quantity'],
    ]
    rows.extend(
        [
            item.product.name,
            item.product.sku,
            item.quantity,
        ]
        for item in snapshot['top_stocked_items']
    )
    rows.extend(
        [
            [],
            ['Low Stock Watchlist'],
            ['Product', 'SKU', 'Quantity', 'Reorder Level'],
        ]
    )
    rows.extend(
        [
            item.product.name,
            item.product.sku,
            item.quantity,
            item.reorder_level,
        ]
        for item in snapshot['low_stock_items']
    )
    rows.extend(
        [
            [],
            ['Recent Stock Movements'],
            ['Product', 'Type', 'Quantity', 'Reference', 'User', 'Date'],
        ]
    )
    rows.extend(
        [
            movement.product.name,
            movement.get_movement_type_display(),
            movement.quantity,
            movement.reference or '',
            _get_user_display(movement.user),
            movement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]
        for movement in snapshot['recent_movements']
    )
    rows.extend(
        [
            [],
            ['Category Coverage'],
            ['Category', 'Product Count'],
        ]
    )
    rows.extend(
        [
            category.name,
            category.product_count,
        ]
        for category in snapshot['category_breakdown']
    )
    return build_csv_response('reports_snapshot', rows)
