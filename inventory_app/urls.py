from django.urls import path

from . import views

app_name = 'inventory_app'

urlpatterns = [
    # inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/export/', views.inventory_export, name='inventory_export'),
    path('inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),
    # stock movement URLs
    path('stock-movements/', views.stock_movement_list,
         name='stock_movement_list'),
    path('stock-movements/export/', views.stock_movement_export, name='stock_movement_export'),
    path('stock-in/<int:pk>/', views.stock_in_view, name='stock_in'),
    path('stock-out/<int:pk>/', views.stock_out_view, name='stock_out'),
]
