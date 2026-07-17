from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.reports_export, name='reports_export'),
    path('register/', views.register, name='register'),
    path('manage/', views.user_list, name='user_list'),
    path('manage/export/', views.user_export, name='user_export'),
    path('manage/<int:pk>/access/', views.user_access_update, name='user_access_update'),
]
