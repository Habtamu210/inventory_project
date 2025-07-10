from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView  # <-- Add this import
from .models import Request, AuditLog, Notification, Item, RequestApproval
from .forms import RequestForm, ProductForm, ItemForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import *
from .forms import *

# -----------------------------
# Dashboard View
# -----------------------------
@login_required
def dashboard(request):
    role = request.user.role
    if role == 'EMPLOYEE':
        requests = Request.objects.filter(employee=request.user)
    elif role == 'DIRECTOR':
        requests = Request.objects.filter(
            employee__business_unit=request.user.businessunit,
            status='PENDING_DIRECTOR'
        )
    elif role == 'INVENTORY_OFFICER':
        requests = Request.objects.filter(status='PENDING_OFFICER')
    else:  # ADMIN
        requests = Request.objects.all()

    return render(request, 'inventory/dashboard.html', {
        'requests': requests
    })

# -----------------------------
# LoginView
# -----------------------------

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # or your home page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'
    authentication_form = CustomLoginForm

login_view = CustomLoginView.as_view()
# -----------------------------
# Create register View
# -----------------------------

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # optionally log in immediately
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'inventory/register.html', {'form': form})

# -----------------------------
# Create Notification View
# -----------------------------
@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'inventory/notifications.html', {'notifications': user_notifications})

# -----------------------------
# Create Request View
# -----------------------------
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

    return render(request, 'inventory/request_form.html', {
        'form': form
    })


# -----------------------------
# Approve Request View
# -----------------------------
@login_required
def approve_request(request, pk):
    req = get_object_or_404(Request, pk=pk)

    if request.user.role == 'DIRECTOR' and req.status == 'PENDING_DIRECTOR':
        req.status = 'PENDING_OFFICER'
    elif request.user.role == 'INVENTORY_OFFICER' and req.status == 'PENDING_OFFICER':
        # Approve the request, assign item
        item = Item.objects.filter(product=req.product, status='Available').first()
        if not item:
            messages.error(request, 'No available item to assign.')
            return redirect('dashboard')
        item.status = 'Assigned'
        item.assigned_to = req.employee
        item.save()

        req.status = 'APPROVED'
        req.final_approval_date = timezone.now()
        req.item = item

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

# -----------------------------
# audit_logs View
# -----------------------------
@login_required
def audit_logs(request):
    user_audit_logs = AuditLog.objects.filter(user=request.user)
    return render(request, 'inventory/audit_logs.html', {'audit_logs': user_audit_logs})

# -----------------------------
# Reject Request View
# -----------------------------
@login_required
def reject_request(request, pk):
    req = get_object_or_404(Request, pk=pk)

    if request.user.role == 'DIRECTOR' and req.status == 'PENDING_DIRECTOR':
        req.status = 'REJECTED_DIRECTOR'
    elif request.user.role == 'INVENTORY_OFFICER' and req.status == 'PENDING_OFFICER':
        req.status = 'REJECTED'
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


# -----------------------------
# Inventory Officer: Add Product
# -----------------------------
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


# -----------------------------
# Inventory Officer: Add Item
# -----------------------------
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



