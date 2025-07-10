from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ----------------------------
# 1. Custom User with Roles
# ----------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
        ('DIRECTOR', 'Director'),
        ('INVENTORY_MANAGER', 'Inventory Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

# ----------------------------
# 2. Business Unit
# ----------------------------
class BusinessUnit(models.Model):
    name = models.CharField(max_length=100)
    director = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'DIRECTOR'})

    def __str__(self):
        return self.name

# ----------------------------
# 3. Product Category
# ----------------------------
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ----------------------------
# 4. Unit of Measurement
# ----------------------------
class UnitOfMeasurement(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __str__(self):
        return self.abbreviation

# ----------------------------
# 5. Product
# ----------------------------
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    unit_of_measurement = models.ForeignKey(UnitOfMeasurement, on_delete=models.CASCADE)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def quantity_in_stock(self):
        return self.item_set.filter(status='Available').count()

# ----------------------------
# 6. Item (Physical Instance of Product)
# ----------------------------
class Item(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Assigned', 'Assigned'),
        ('In Repair', 'In Repair'),
        ('Retired', 'Retired'),
    ]
    CONDITION_CHOICES = [
        ('New', 'New'),
        ('Used', 'Used'),
        ('Refurbished', 'Refurbished'),
        ('Damaged', 'Damaged'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    location = models.CharField(max_length=100)
    warranty_expiry_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'EMPLOYEE'})
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} ({self.serial_number})"

# ----------------------------
# 7. Request (Approval Workflow)
# ----------------------------
class Request(models.Model):
    STATUS_CHOICES = [
        ('PENDING_DIRECTOR', 'Pending Director Approval'),
        ('REJECTED_DIRECTOR', 'Rejected by Director'),
        ('PENDING_MANAGER', 'Pending Inventory Manager Approval'),
        ('REJECTED_MANAGER', 'Rejected by Inventory Manager'),
        ('APPROVED', 'Approved'),
    ]
    employee = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'EMPLOYEE'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reason = models.TextField()
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING_DIRECTOR')
    final_approval_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} requested by {self.employee.username}"

# ----------------------------
# 8. RequestApproval (Log Each Step)
# ----------------------------
class RequestApproval(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    status = models.CharField(max_length=10, choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected')])
    comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request} - {self.status} by {self.approver.username}"

# ----------------------------
# 9. Transaction (Borrow/Return)
# ----------------------------
class Transaction(models.Model):
    STATUS_CHOICES = [
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'EMPLOYEE'})
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Borrowed')
    condition_on_borrow = models.CharField(max_length=20, choices=Item.CONDITION_CHOICES)
    condition_on_return = models.CharField(max_length=20, choices=Item.CONDITION_CHOICES, null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.item} borrowed by {self.employee.username}"

# ----------------------------
# 10. Notification
# ----------------------------
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.message[:30]}..."

# ----------------------------
# 11. AuditLog
# ----------------------------
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.user.username} {self.action_type} {self.object_type} {self.object_id}"
