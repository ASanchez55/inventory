from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    # category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_edit'),
    path('categories/<int:pk>/delete/',
         views.category_delete, name='category_delete'),
    # brand URLs
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_create, name='brand_add'),
    path('brands/<int:pk>/edit/', views.brand_update, name='brand_edit'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    # supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/export/', views.supplier_export, name='supplier_export'),
    path('suppliers/add/', views.supplier_create, name='supplier_add'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/export/', views.product_export, name='product_export'),
    path('products/add/', views.product_create, name='product_add'),
    path('products/<int:pk>/edit/', views.product_update, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # purchase order URLs
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/export/', views.purchase_order_export, name='purchase_order_export'),
    path('purchase-orders/add/', views.purchase_order_create, name='purchase_order_add'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/edit/', views.purchase_order_update, name='purchase_order_edit'),
    path('purchase-orders/<int:pk>/receive/', views.purchase_order_receive, name='purchase_order_receive'),
    path('purchase-orders/<int:pk>/delete/', views.purchase_order_delete, name='purchase_order_delete'),
]
