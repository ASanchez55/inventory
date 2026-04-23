from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
