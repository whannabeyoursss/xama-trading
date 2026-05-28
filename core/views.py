import random
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver

from .forms import (
    AdminNoteForm,
    BulkPriceForm,
    LoginForm,
    OrderFilterForm,
    OrderForm,
    PasswordResetConfirmForm,
    PhoneResetRequestForm,
    ProductForm,
    ProductSearchForm,
    ReviewForm,
    SignUpForm,
    TwoFactorForm,
    UserEditForm,
)
from .models import (
    AdminNote,
    AuditLog,
    BulkPrice,
    InventoryAlert,
    Order,
    OrderStatusHistory,
    PasswordResetCode,
    Product,
    Review,
    User,
)


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Account created. You can now log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username']
            password = form.cleaned_data['password']
            username = identifier
            if identifier.isdigit():
                user = User.objects.filter(phone_number=identifier).first()
                username = user.username if user else identifier
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            messages.error(request, 'Invalid login details.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    if request.user.is_admin_user():
        return admin_dashboard(request)
    return customer_dashboard(request)


def admin_dashboard(request):
    note_form = AdminNoteForm(request.POST or None)
    if request.method == 'POST' and request.POST.get('form_type') == 'note' and note_form.is_valid():
        note = note_form.save(commit=False)
        note.admin = request.user
        note.save()
        messages.success(request, 'Note saved.')
        return redirect('dashboard')

    products = Product.objects.all()
    orders = Order.objects.select_related('customer', 'product')[:8]
    context = {
        'note_form': note_form,
        'notes': AdminNote.objects.filter(admin=request.user)[:5],
        'product_count': products.count(),
        'low_stock_count': sum(1 for product in products if product.is_low_stock),
        'order_count': Order.objects.count(),
        'sales_total': Order.objects.exclude(status=Order.CANCELLED).aggregate(total=Sum('quantity'))['total'] or 0,
        'recent_orders': orders,
        'low_stock_products': [product for product in products if product.is_low_stock][:6],
    }
    return render(request, 'core/admin_dashboard.html', context)


def customer_dashboard(request):
    products = Product.objects.filter(quantity__gt=0)
    customer_orders = Order.objects.filter(customer=request.user)
    orders = customer_orders.select_related('product')[:8]
    context = {
        'products': products[:8],
        'order_count': customer_orders.count(),
        'pending_count': customer_orders.filter(status=Order.PENDING).count(),
        'recent_orders': orders,
    }
    return render(request, 'core/customer_dashboard.html', context)


@login_required
def product_list(request):
    products = Product.objects.select_related('category')
    search_form = ProductSearchForm(request.GET)
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search', '').strip()
        category_query = search_form.cleaned_data.get('category', '').strip()
        low_stock = search_form.cleaned_data.get('low_stock', False)
        
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(sku__icontains=search_query)
            )
        if category_query:
            products = products.filter(category__name__icontains=category_query)
        if low_stock:
            products = [p for p in products if p.is_low_stock]
    
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/product_list.html', {
        'page_obj': page_obj,
        'search_form': search_form,
    })


@login_required
def product_create(request):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product added.')
        return redirect('products')
    return render(request, 'core/product_form.html', {'form': form})


@login_required
def order_create(request):
    form = OrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.customer = request.user
        order.save()
        messages.success(request, 'Order submitted.')
        return redirect('orders')
    return render(request, 'core/order_form.html', {'form': form})


@login_required
def order_list(request):
    if request.user.is_admin_user():
        orders = Order.objects.select_related('customer', 'product')
    else:
        orders = Order.objects.filter(customer=request.user).select_related('product')
    
    filter_form = OrderFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status', '').strip()
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        
        if status:
            orders = orders.filter(status=status)
        if date_from:
            orders = orders.filter(created_at__date__gte=date_from)
        if date_to:
            orders = orders.filter(created_at__date__lte=date_to)
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/order_list.html', {
        'page_obj': page_obj,
        'filter_form': filter_form,
    })


@login_required
def order_update_status(request, pk, status):
    if not request.user.is_admin_user():
        return redirect('dashboard')
    order = get_object_or_404(Order, pk=pk)
    if status in dict(Order.STATUS_CHOICES):
        old_status = order.status
        order.status = status
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=status,
            changed_by=request.user,
        )
        
        AuditLog.objects.create(
            user=request.user,
            action='update',
            model_name='Order',
            object_id=order.pk,
            changes={'status': {old_status: status}},
        )
        
        messages.success(request, 'Order status updated.')
    return redirect('orders')


def forgot_password(request):
    if request.method == 'POST':
        form = PhoneResetRequestForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(phone_number=form.cleaned_data['phone_number']).first()
            if user:
                code = f'{random.randint(100000, 999999)}'
                PasswordResetCode.objects.create(user=user, code=code)
                request.session['reset_phone'] = user.phone_number
                messages.info(request, f'Development SMS code: {code}')
                return redirect('reset_password')
            messages.error(request, 'No account uses that phone number.')
    else:
        form = PhoneResetRequestForm()
    return render(request, 'registration/forgot_password.html', {'form': form})


def reset_password(request):
    phone = request.session.get('reset_phone')
    if not phone:
        return redirect('forgot_password')
    user = get_object_or_404(User, phone_number=phone)
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            reset_code = PasswordResetCode.objects.filter(
                user=user,
                code=form.cleaned_data['code'],
                used=False,
            ).first()
            if reset_code and reset_code.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                reset_code.used = True
                reset_code.save()
                update_session_auth_hash(request, user)
                request.session.pop('reset_phone', None)
                messages.success(request, 'Password changed. Please log in.')
                return redirect('login')
            messages.error(request, 'Invalid or expired code.')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'registration/reset_password.html', {'form': form, 'phone': phone})


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if order.customer != request.user and not request.user.is_admin_user():
        messages.error(request, 'You cannot cancel this order.')
        return redirect('orders')
    
    if not order.can_cancel():
        messages.error(request, 'Only pending orders can be cancelled.')
        return redirect('orders')
    
    old_status = order.status
    order.status = Order.CANCELLED
    order.save()
    
    OrderStatusHistory.objects.create(
        order=order,
        old_status=old_status,
        new_status=Order.CANCELLED,
        changed_by=request.user,
        notes='Cancelled by customer' if order.customer == request.user else 'Cancelled by admin',
    )
    
    AuditLog.objects.create(
        user=request.user,
        action='update',
        model_name='Order',
        object_id=order.pk,
        changes={'status': {old_status: Order.CANCELLED}},
    )
    
    messages.success(request, 'Order cancelled successfully.')
    return redirect('orders')


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if order.customer != request.user and not request.user.is_admin_user():
        messages.error(request, 'You cannot view this order.')
        return redirect('orders')
    
    review_form = None
    if order.status == Order.COMPLETED and order.customer == request.user:
        existing_review = Review.objects.filter(product=order.product, customer=request.user).first()
        if request.method == 'POST':
            review_form = ReviewForm(request.POST, instance=existing_review)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = order.product
                review.customer = request.user
                review.save()
                messages.success(request, 'Review submitted for approval.')
                return redirect('order_detail', pk=pk)
        else:
            review_form = ReviewForm(instance=existing_review)
    
    status_history = order.status_history.all()
    
    context = {
        'order': order,
        'review_form': review_form,
        'status_history': status_history,
    }
    return render(request, 'core/order_detail.html', context)


@login_required
def customer_history(request, user_id=None):
    if user_id and request.user.is_admin_user():
        customer = get_object_or_404(User, pk=user_id, role=User.CUSTOMER)
    else:
        customer = request.user
    
    if customer != request.user and not request.user.is_admin_user():
        messages.error(request, 'You cannot view other customers\' history.')
        return redirect('dashboard')
    
    orders = Order.objects.filter(customer=customer).select_related('product')
    total_spent = orders.exclude(status=Order.CANCELLED).aggregate(total=Sum('quantity'))['total'] or 0
    avg_order_value = orders.exclude(status=Order.CANCELLED).aggregate(
        avg=Avg('quantity')
    )['avg'] or 0
    
    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customer': customer,
        'page_obj': page_obj,
        'total_spent': total_spent,
        'avg_order_value': round(avg_order_value, 2),
    }
    return render(request, 'core/customer_history.html', context)


@login_required
def audit_logs(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    logs = AuditLog.objects.all()
    
    model_filter = request.GET.get('model', '').strip()
    user_filter = request.GET.get('user', '').strip()
    action_filter = request.GET.get('action', '').strip()
    
    if model_filter:
        logs = logs.filter(model_name__icontains=model_filter)
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'model_filter': model_filter,
        'user_filter': user_filter,
        'action_filter': action_filter,
    }
    return render(request, 'core/audit_logs.html', context)


@login_required
def user_list(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    users = User.objects.all()
    
    role_filter = request.GET.get('role', '').strip()
    if role_filter:
        users = users.filter(role=role_filter)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'role_filter': role_filter,
    }
    return render(request, 'core/user_list.html', context)


@login_required
def user_edit(request, user_id):
    if not request.user.is_admin_user() and request.user.id != user_id:
        messages.error(request, 'You cannot edit other users.')
        return redirect('dashboard')
    
    user_obj = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            old_data = {
                'role': User.objects.get(pk=user_id).role,
            }
            form.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=user_id,
                changes={'role': old_data},
            )
            
            messages.success(request, 'User updated.')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user_obj)
    
    return render(request, 'core/user_edit.html', {'form': form, 'user_obj': user_obj})


@login_required
def user_create(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            user_obj = form.save(commit=False)
            user_obj.username = request.POST.get('username')
            user_obj.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='User',
                object_id=user_obj.pk,
                changes={},
            )
            
            messages.success(request, 'User created.')
            return redirect('user_list')
    else:
        form = UserEditForm()
    
    return render(request, 'core/user_create.html', {'form': form})


@login_required
def user_settings(request):
    if request.method == 'POST':
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            request.user.two_factor_enabled = form.cleaned_data.get('enable_2fa', False)
            request.user.save()
            messages.success(request, 'Settings updated.')
            return redirect('user_settings')
    else:
        form = TwoFactorForm(initial={'enable_2fa': request.user.two_factor_enabled})
    
    return render(request, 'core/user_settings.html', {'form': form})


@login_required
def admin_panel(request):
    if not request.user.is_admin_user():
        redirect('dashboard')
    
    products = Product.objects.all()
    orders = Order.objects.select_related('customer', 'product').order_by('-created_at')
    users = User.objects.all()
    
    pending_orders = orders.filter(status=Order.PENDING).count()
    low_stock_products = [p for p in products if p.is_low_stock]
    
    # Chart data
    last_30_days = datetime.now() - timedelta(days=30)
    daily_orders = {}
    for order in orders.filter(created_at__gte=last_30_days).exclude(status=Order.CANCELLED):
        date_key = order.created_at.strftime('%Y-%m-%d')
        daily_orders[date_key] = daily_orders.get(date_key, 0) + order.quantity
    
    # Top products
    top_products = {}
    for order in orders.exclude(status=Order.CANCELLED):
        product_name = order.product.name
        top_products[product_name] = top_products.get(product_name, 0) + order.quantity
    top_products = sorted(top_products.items(), key=lambda x: x[1], reverse=True)[:10]
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'product_count': products.count(),
        'low_stock_count': len(low_stock_products),
        'order_count': orders.count(),
        'pending_orders_count': pending_orders,
        'user_count': users.count(),
        'admin_count': users.filter(role=User.ADMIN).count(),
        'customer_count': users.filter(role=User.CUSTOMER).count(),
        'sales_total': orders.exclude(status=Order.CANCELLED).aggregate(total=Sum('quantity'))['total'] or 0,
        'page_obj': page_obj,
        'low_stock_products': low_stock_products[:10],
        'recent_products': products.order_by('-created_at')[:10],
        'daily_orders': daily_orders,
        'top_products': top_products,
    }
    return render(request, 'core/admin_panel.html', context)

# Create your views here.
