from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views



urlpatterns = [
    # Auth
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),

    # Requests
    path('request/create/', views.create_request, name='create_request'),
    path('request/<int:pk>/approve/', views.approve_request, name='approve_request'),
    path('request/<int:pk>/reject/', views.reject_request, name='reject_request'),

    # Products
    path('products/', views.product_list, name='product_list'),           # list products for Inventory Officer
    path('products/add/', views.add_product, name='add_product'),

    # Items
    path('items/add/', views.add_item, name='add_item'),

    # Users (Admin)
    path('admin/users/', views.manage_users, name='manage_users'),

    # Audit Logs
    path('audit-logs/', views.audit_logs, name='audit_logs'),

    # Transactions (borrow/return)
    path('borrow/', views.borrow_item, name='borrow_item'),
    path('return/<int:pk>/', views.return_item, name='return_item'),
]
