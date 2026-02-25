from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from functools import wraps

from website.models import Product, Customer, Order, Staff

# Staff Authentication System

def staff_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'staff_id' not in request.session:
            messages.warning(request, "Restricted access. Please login.")
            return redirect('staff_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def staff_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            staff = Staff.objects.get(email=email)
            if check_password(password, staff.password):
                if staff.is_active:
                    request.session['staff_id'] = staff.id
                    messages.success(request, f"Welcome, {staff.name}!")
                    return redirect('staff_dashboard')
                else:
                    messages.error(request, "Account is inactive. Contact admin.")
            else:
                messages.error(request, "Invalid credentials.")
        except Staff.DoesNotExist:
            messages.error(request, "Invalid credentials.")
            
    return render(request, 'employee/login.html')

def staff_logout(request):
    if 'staff_id' in request.session:
        del request.session['staff_id']
        messages.success(request, "Staff logged out successfully.")
    return redirect('staff_login')

@staff_login_required
def staff_dashboard(request):
    try:
        staff = Staff.objects.get(id=request.session['staff_id'])
    except Staff.DoesNotExist:
        del request.session['staff_id']
        return redirect('staff_login')

    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    pending_requests = Order.objects.filter(status='pending').count()
    recent_orders = Order.objects.order_by('-date')[:5]
        
    return render(request, 'employee/dashboard.html', {
        'staff': staff,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'pending_requests': pending_requests,
        'recent_orders': recent_orders
    })

@staff_login_required
def staff_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        staff_comment = request.POST.get('staff_comment')
        
        try:
            order = Order.objects.get(id=order_id)
            if action == 'accept':
                order.status = 'accepted'
                order.save()
                messages.success(request, f"Order #{order.id} accepted.")
            elif action == 'reject':
                if not staff_comment:
                    messages.error(request, "Comment is required when rejecting an order.")
                else:
                    order.status = 'rejected'
                    order.staff_comment = staff_comment
                    order.save()
                    messages.success(request, f"Order #{order.id} rejected.")
            elif action == 'pending':
                order.status = 'pending'
                order.save()
                messages.success(request, f"Order #{order.id} set to pending.")
            elif action == 'completed':
                order.status = 'completed'
                order.save()
                messages.success(request, f"Order #{order.id} marked as completed.")
        except Order.DoesNotExist:
            messages.error(request, "Order ID not found.")
            
        return redirect('staff_orders')

    try:
        staff = Staff.objects.get(id=request.session['staff_id'])
    except Staff.DoesNotExist:
        return redirect('staff_login')
        
    orders = Order.objects.all().order_by('-date')
    return render(request, 'employee/orders.html', {'orders': orders, 'staff': staff})
