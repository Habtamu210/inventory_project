from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_protect

from .forms import (
    CustomUserCreationForm, CustomLoginForm,
    RequestForm, ProductForm, ItemForm,
    TransactionForm, AdminUserCreationForm
)
from .models import (
    User, BusinessUnit, Request, RequestApproval,
    Product, Item, AuditLog, Notification, Transaction
)

@login_required
def dashboard(request):
    role = request.user.role

    if role == 'EMPLOYEE':
        requests = Request.objects.filter(employee=request.user)
        return render(request, 'inventory/dashboard_employee.html', {'requests': requests})

    elif role == 'DIRECTOR':
        try:
            business_unit = request.user.businessunit
        except BusinessUnit.DoesNotExist:
            business_unit = None

        if business_unit:
            requests = Request.objects.filter(
                employee__business_unit=business_unit,
                status='PENDING_DIRECTOR'
            )
        else:
            requests = Request.objects.none()

        return render(request, 'inventory/dashboard_director.html', {'requests': requests})

    elif role == 'INVENTORY_OFFICER':
        requests = Request.objects.filter(status='PENDING_OFFICER')
        products = Product.objects.all()
        return render(request, 'inventory/dashboard_officer.html', {'requests': requests, 'products': products})

    elif role == 'ADMIN':
        users = User.objects.exclude(id=request.user.id)
        return render(request, 'inventory/dashboard_admin.html', {'users': users})

    else:
        return redirect('login')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'inventory/login.html')

class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'
    authentication_form = CustomLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dashboard')

@login_required
@csrf_protect
def register(request):
    if request.user.role != 'ADMIN':
        messages.warning(request, 'You are not authorized to access the registration page.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User registered successfully.')
            return redirect('manage_users')
    else:
        form = AdminUserCreationForm()
    return render(request, 'inventory/register.html', {'form': form})



@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'inventory/notifications.html', {'notifications': user_notifications})

@login_required
def create_request(request):
    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard')

    form = RequestForm(request.POST or None, user=request.user)
    if form.is_valid():
        req = form.save(commit=False)
        req.employee = request.user
        req.save()
        AuditLog.objects.create(
            user=request.user,
            action_type='Create',
            object_type='Request',
            object_id=req.id,
            description=f'{request.user.username} requested item {req.product}'
        )
        messages.success(request, 'Request submitted successfully.')
        return redirect('dashboard')

    return render(request, 'inventory/request_form.html', {'form': form})

@login_required
def approve_request(request, pk):
    req = get_object_or_404(Request, pk=pk)

    if request.user.role == 'DIRECTOR' and req.status == 'PENDING_DIRECTOR':
        req.status = 'PENDING_OFFICER'
    elif request.user.role == 'INVENTORY_OFFICER' and req.status == 'PENDING_OFFICER':
        item = Item.objects.filter(product=req.product, status='Available').first()
        if not item:
            messages.error(request, 'No available item to assign.')
            return redirect('dashboard')
        item.status = 'Assigned'
        item.assigned_to = req.employee
        item.save()

        req.status = 'APPROVED'
        req.final_approval_date = timezone.now()
    else:
        messages.warning(request, 'Unauthorized or invalid request status.')
        return redirect('dashboard')

    req.save()

    RequestApproval.objects.create(
        request=req,
        approver=request.user,
        role=request.user.role,
        status='APPROVED'
    )

    AuditLog.objects.create(
        user=request.user,
        action_type='Approve',
        object_type='Request',
        object_id=req.id,
        description=f'{request.user.username} approved request {req.id}'
    )

    messages.success(request, 'Request approved successfully.')
    return redirect('dashboard')

@login_required
def reject_request(request, pk):
    req = get_object_or_404(Request, pk=pk)

    if request.user.role == 'DIRECTOR' and req.status == 'PENDING_DIRECTOR':
        req.status = 'REJECTED_DIRECTOR'
    elif request.user.role == 'INVENTORY_OFFICER' and req.status == 'PENDING_OFFICER':
        req.status = 'REJECTED_OFFICER'
    else:
        messages.warning(request, 'Unauthorized or invalid request status.')
        return redirect('dashboard')

    req.save()

    RequestApproval.objects.create(
        request=req,
        approver=request.user,
        role=request.user.role,
        status='REJECTED'
    )

    AuditLog.objects.create(
        user=request.user,
        action_type='Reject',
        object_type='Request',
        object_id=req.id,
        description=f'{request.user.username} rejected request {req.id}'
    )

    messages.success(request, 'Request rejected.')
    return redirect('dashboard')

@login_required
def add_product(request):
    if request.user.role != 'INVENTORY_OFFICER':
        return redirect('dashboard')

    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save()
        AuditLog.objects.create(
            user=request.user,
            action_type='Create',
            object_type='Product',
            object_id=product.id,
            description=f'{request.user.username} added product {product.name}'
        )
        messages.success(request, 'Product added successfully.')
        return redirect('dashboard')

    return render(request, 'inventory/add_product.html', {'form': form})

@login_required
def add_item(request):
    if request.user.role != 'INVENTORY_OFFICER':
        return redirect('dashboard')

    form = ItemForm(request.POST or None)
    if form.is_valid():
        item = form.save()
        AuditLog.objects.create(
            user=request.user,
            action_type='Create',
            object_type='Item',
            object_id=item.id,
            description=f'{request.user.username} added item {item.serial_number}'
        )
        messages.success(request, 'Item added successfully.')
        return redirect('dashboard')

    return render(request, 'inventory/add_item.html', {'form': form})

@login_required
def product_list(request):
    if request.user.role != 'INVENTORY_OFFICER':
        return redirect('dashboard')
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def manage_users(request):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'inventory/admin_user_list.html', {'users': users})

@login_required
def audit_logs(request):
    user_audit_logs = AuditLog.objects.filter(user=request.user)
    return render(request, 'inventory/audit_logs.html', {'audit_logs': user_audit_logs})

@login_required
def borrow_item(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.employee = request.user
            transaction.status = 'Borrowed'
            transaction.save()

            # Update item status to 'Assigned'
            item = transaction.item
            item.status = 'Assigned'
            item.assigned_to = request.user
            item.save()

            messages.success(request, f'You have borrowed {item.product.name} successfully.')
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'inventory/borrow_item.html', {'form': form})

@login_required
def return_item(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, employee=request.user)
    if transaction.status != 'Borrowed':
        messages.warning(request, 'This item is already returned or invalid.')
        return redirect('dashboard')

    if request.method == 'POST':
        condition_on_return = request.POST.get('condition_on_return')
        remarks = request.POST.get('remarks', '')
        transaction.actual_return_date = timezone.now().date()
        transaction.condition_on_return = condition_on_return
        transaction.remarks = remarks
        transaction.status = 'Returned'
        transaction.save()

        # Update item status to Available
        item = transaction.item
        item.status = 'Available'
        item.assigned_to = None
        item.save()

        messages.success(request, f'Item {item.product.name} returned successfully.')
        return redirect('dashboard')

    return render(request, 'inventory/return_item.html', {'transaction': transaction})

@login_required
def manage_transactions(request):
    if request.user.role != 'INVENTORY_OFFICER':
        return redirect('dashboard')
    transactions = Transaction.objects.all()
    return render(request, 'inventory/manage_transactions.html', {'transactions': transactions})
