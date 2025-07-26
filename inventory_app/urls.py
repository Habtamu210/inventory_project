from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    # Auth
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    # Password Change
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'
    ), name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),

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
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-user-role/<int:user_id>/', views.change_user_role, name='change_user_role'),

    # Audit Logs
    path('audit-logs/', views.audit_logs, name='audit_logs'),

    # Transactions (borrow/return)
    path('borrow/', views.borrow_item, name='borrow_item'),
    path('return/<int:pk>/', views.return_item, name='return_item'),
    path('transactions/', views.manage_transactions, name='manage_transactions'),

]
