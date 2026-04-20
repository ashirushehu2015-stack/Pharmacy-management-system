from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='landing.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('inventory/', views.medicine_list, name='medicine_list'),
    path('inventory/add/', views.medicine_create, name='medicine_create'),
    path('inventory/<int:pk>/edit/', views.medicine_update, name='medicine_update'),
    path('inventory/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/new/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:pk>/print/', views.prescription_print, name='prescription_print'),
    path('prescriptions/<int:pk>/fill/', views.prescription_fill, name='prescription_fill'),
    
    path('sales/new/', views.sale_create, name='sale_create'),
    
    path('analytics/', views.analytics, name='analytics'),
    
    path('reports/', views.reports_portal, name='reports'),
    path('reports/export/inventory/', views.export_inventory, name='export_inventory'),
    path('reports/export/prescriptions/', views.export_prescriptions, name='export_prescriptions'),
    path('reports/export/sales/', views.export_sales, name='export_sales'),
    
    # Print Reports
    path('reports/print/inventory/', views.report_inventory_print, name='report_inventory_print'),
    path('reports/print/low-stock/', views.report_low_stock_print, name='report_low_stock_print'),
    path('reports/print/sales/', views.report_sales_print, name='report_sales_print'),

    # User Management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Stock Entry URLs
    path('stock/add/', views.stock_entry_create, name='stock_entry_create'),
    
    # System Setup URL
    path('setup-system/', views.setup_system, name='setup_system'),
]
