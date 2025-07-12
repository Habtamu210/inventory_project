from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, BusinessUnit, ProductCategory, UnitOfMeasurement,
    Product, Item, Request, RequestApproval,
    Transaction, Notification, AuditLog
)

# -----------------------------
# Custom User Admin
# -----------------------------
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

# -----------------------------
# Business Unit
# -----------------------------
@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'director')
    search_fields = ('name',)

# -----------------------------
# Product Category
# -----------------------------
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# -----------------------------
# Unit of Measurement
# -----------------------------
@admin.register(UnitOfMeasurement)
class UnitOfMeasurementAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')
    search_fields = ('name', 'abbreviation')

# -----------------------------
# Product
# -----------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_of_measurement', 'price_per_unit', 'reorder_level', 'is_active', 'quantity_in_stock')
    list_filter = ('is_active', 'category')
    search_fields = ('name',)

# -----------------------------
# Item
# -----------------------------
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'serial_number', 'condition', 'status', 'location', 'assigned_to', 'business_unit')
    list_filter = ('status', 'condition', 'business_unit')
    search_fields = ('serial_number',)

# -----------------------------
# Request
# -----------------------------
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('product', 'employee', 'status', 'request_date', 'final_approval_date')
    list_filter = ('status',)
    search_fields = ('product__name', 'employee__username')

# -----------------------------
# Request Approval
# -----------------------------
@admin.register(RequestApproval)
class RequestApprovalAdmin(admin.ModelAdmin):
    list_display = ('request', 'approver', 'role', 'status', 'timestamp')
    list_filter = ('role', 'status')

# -----------------------------
# Transaction
# -----------------------------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('item', 'employee', 'borrow_date', 'expected_return_date', 'actual_return_date', 'status')
    list_filter = ('status',)

# -----------------------------
# Notification
# -----------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read',)
    search_fields = ('recipient__username', 'message')

# -----------------------------
# Audit Log
# -----------------------------
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'object_type', 'object_id', 'timestamp')
    search_fields = ('user__username', 'action_type', 'object_type')
