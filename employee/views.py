from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from functools import wraps

from website.models import Product, Customer, Order, Staff, Category

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

@staff_login_required
def staff_categories(request):
    try:
        staff = Staff.objects.get(id=request.session['staff_id'])
    except Staff.DoesNotExist:
        return redirect('staff_login')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            image = request.FILES.get('image')
            is_top_category = request.POST.get('is_top_category') == 'on'
            priority = request.POST.get('priority', 0)
            
            category = Category(
                name=name,
                is_top_category=is_top_category,
                priority=priority
            )
            if image:
                category.image = image
            category.save()
            messages.success(request, f"Category '{name}' added successfully.")
            
        elif action == 'edit':
            category_id = request.POST.get('category_id')
            try:
                category = Category.objects.get(id=category_id)
                category.name = request.POST.get('name')
                if request.FILES.get('image'):
                    category.image = request.FILES.get('image')
                category.is_top_category = request.POST.get('is_top_category') == 'on'
                category.priority = request.POST.get('priority', 0)
                category.save()
                messages.success(request, f"Category '{category.name}' updated successfully.")
            except Category.DoesNotExist:
                messages.error(request, "Category not found.")
                
        elif action == 'delete':
            category_id = request.POST.get('category_id')
            try:
                category = Category.objects.get(id=category_id)
                name = category.name
                category.delete()
                messages.success(request, f"Category '{name}' deleted successfully.")
            except Category.DoesNotExist:
                messages.error(request, "Category not found.")
                
        return redirect('staff_categories')

    categories = Category.objects.all().order_by('-id')
    return render(request, 'employee/categories.html', {'categories': categories, 'staff': staff})

@staff_login_required
def staff_products(request):
    try:
        staff = Staff.objects.get(id=request.session['staff_id'])
    except Staff.DoesNotExist:
        return redirect('staff_login')
        
    from website.models import Size # Assuming we need size and category
    categories = Category.objects.all()
    sizes_all = Size.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            price = request.POST.get('price', 0)
            category_id = request.POST.get('category')
            description = request.POST.get('description', '')
            image = request.FILES.get('image')
            is_sale = request.POST.get('is_sale') == 'on'
            sale_price = request.POST.get('sale_price', 0)
            is_top_product = request.POST.get('is_top_product') == 'on'
            priority = request.POST.get('priority', 0)
            sizes_ids = request.POST.getlist('sizes')
            
            try:
                category = Category.objects.get(id=category_id)
                product = Product(
                    name=name,
                    price=price,
                    category=category,
                    description=description,
                    is_sale=is_sale,
                    sale_price=sale_price,
                    is_top_product=is_top_product,
                    priority=priority
                )
                if image:
                    product.image = image
                product.save()
                
                if sizes_ids:
                    sizes = Size.objects.filter(id__in=sizes_ids)
                    product.sizes.set(sizes)
                    
                messages.success(request, f"Product '{name}' added successfully.")
            except Category.DoesNotExist:
                messages.error(request, "Selected Category not found.")
            
        elif action == 'edit':
            product_id = request.POST.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
                product.name = request.POST.get('name')
                product.price = request.POST.get('price', 0)
                category_id = request.POST.get('category')
                try:    
                    product.category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    pass
                product.description = request.POST.get('description', '')
                if request.FILES.get('image'):
                    product.image = request.FILES.get('image')
                    
                product.is_sale = request.POST.get('is_sale') == 'on'
                product.sale_price = request.POST.get('sale_price', 0)
                product.is_top_product = request.POST.get('is_top_product') == 'on'
                product.priority = request.POST.get('priority', 0)
                product.save()
                
                sizes_ids = request.POST.getlist('sizes')
                if sizes_ids:
                    sizes = Size.objects.filter(id__in=sizes_ids)
                    product.sizes.set(sizes)
                else:
                    product.sizes.clear()
                    
                messages.success(request, f"Product '{product.name}' updated successfully.")
            except Product.DoesNotExist:
                messages.error(request, "Product not found.")
                
        elif action == 'delete':
            product_id = request.POST.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
                name = product.name
                product.delete()
                messages.success(request, f"Product '{name}' deleted successfully.")
            except Product.DoesNotExist:
                messages.error(request, "Product not found.")
                
        return redirect('staff_products')

    products = Product.objects.all().order_by('-id')
    return render(request, 'employee/products.html', {
        'products': products, 
        'staff': staff,
        'categories': categories,
        'sizes_all': sizes_all
    })
