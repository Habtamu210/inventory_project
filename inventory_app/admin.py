from django.contrib import admin
from .models import (
    User,
    BusinessUnit,
    ProductCategory,
    UnitOfMeasurement,
    Product,
    Item,
    Request,
    RequestApproval,
    Transaction,
    Notification,
    AuditLog,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# -----------------------------
# Custom User Admin
# -----------------------------
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(User, UserAdmin)

# -----------------------------
# Business Unit Admin
# -----------------------------
@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'director')
    search_fields = ('name',)

# -----------------------------
# Product Category Admin
# -----------------------------
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# -----------------------------
# Unit of Measurement Admin
# -----------------------------
@admin.register(UnitOfMeasurement)
class UnitOfMeasurementAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')
    search_fields = ('name', 'abbreviation')

# -----------------------------
# Product Admin
# -----------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_of_measurement', 'price_per_unit', 'reorder_level', 'is_active', 'quantity_in_stock')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)

# -----------------------------
# Item Admin
# -----------------------------
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'serial_number', 'status', 'condition', 'location', 'assigned_to', 'business_unit')
    list_filter = ('status', 'condition', 'business_unit')
    search_fields = ('serial_number',)

# -----------------------------
# Request Admin
# -----------------------------
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('product', 'employee', 'status', 'request_date', 'final_approval_date')
    list_filter = ('status', 'request_date')
    search_fields = ('employee__username', 'product__name')

# -----------------------------
# Request Approval Admin
# -----------------------------
@admin.register(RequestApproval)
class RequestApprovalAdmin(admin.ModelAdmin):
    list_display = ('request', 'approver', 'role', 'status', 'timestamp')
    list_filter = ('role', 'status')

# -----------------------------
# Transaction Admin
# -----------------------------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('item', 'employee', 'borrow_date', 'expected_return_date', 'actual_return_date', 'status')
    list_filter = ('status', 'borrow_date', 'actual_return_date')

# -----------------------------
# Notification Admin
# -----------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('recipient__username',)

# -----------------------------
# Audit Log Admin
# -----------------------------
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'object_type', 'object_id', 'timestamp')
    list_filter = ('action_type', 'object_type', 'timestamp')
    search_fields = ('user__username', 'description')


# Register your models here.
