from django.shortcuts import render, redirect
from django.http import JsonResponse
from urllib.parse import quote
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms 
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from .models import Product,Category,Testimonial,Season,Subscriber,Size,Customer,CustomerDetails, Country, State, Order, Staff
from functools import wraps

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if Subscriber.objects.filter(email=email).exists():
                messages.warning(request, "You are already subscribed with this email!")
            else:
                Subscriber.objects.create(email=email)
                messages.success(request, "Thank you for subscribing!")
        else:
             messages.error(request, "Please provide a valid email address.")
             
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Create your views here.

def home(request):
    top_categories = Category.objects.filter(is_top_category=True).order_by('priority')[:3]
    top_products = Product.objects.filter(is_top_product=True).order_by('priority')[:6]
    testimonials = Testimonial.objects.all()
    season = Season.objects.filter(is_active=True).first()

    return render(request, 'home.html', {
        'top_categories': top_categories,
        'top_products': top_products,
        'testimonials': testimonials,
        'season': season,
    })

def about(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'about.html', {
        'testimonials': testimonials,
    })

def contact(request):
    return render(request, 'contact.html', {}) 
  
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()  # Get all categories
    testimonials = Testimonial.objects.all()
    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'testimonials': testimonials,
    })

def product(request, pk):
    product = Product.objects.get(id=pk)
    product_url = request.build_absolute_uri()
    product_images = product.images.all()  # Uses related_name='images'
    all_sizes = Size.objects.all()

    return render(request, 'product.html', {
        'product': product,
        'product_url': product_url,
        'product_images': product_images,
        'all_sizes': all_sizes,
    })

def category(request, cat):
    all_categories = Category.objects.all()
    categories_with_slugs = [(c.name, c.get_url_name()) for c in all_categories]

    categories = Category.objects.all() 
    
    try:
        # Find the category matching the slugified version
        for category_name, category_slug in categories_with_slugs:
            if category_slug == cat:  # Compare with the incoming slug
                category = Category.objects.get(name=category_name)
                products = Product.objects.filter(category=category)
                return render(request, 'category.html', {
                    'products': products,
                    'category': category,
                    'all_categories': categories_with_slugs,
                    'categories': categories 
                })
        
        # If no match found
        messages.error(request, f"Category '{cat}' doesn't exist")
        return redirect('home')
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('home')

def add_to_cart(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '')
        cart = request.session.get('cart', {})
        
        # Create a unique key for the item (Product ID + Size)
        pk_str = str(pk)
        item_id = f"{pk_str}-{size}" if size else pk_str
        
        if item_id in cart:
            cart[item_id] += quantity
        else:
            cart[item_id] = quantity
            
        request.session['cart'] = cart
        messages.success(request, f"{product.name} ({size}) added to cart successfully!" if size else f"{product.name} added to cart successfully!")
        return redirect('product', pk=pk)
    else:
        return redirect('product', pk=pk)

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    # Extract authentic product IDs from complex keys
    product_ids = set()
    for key in cart.keys():
        # Key format: "id-size" or "id"
        pid = key.split('-')[0]
        if pid.isdigit():
            product_ids.add(int(pid))
            
    products = Product.objects.filter(id__in=product_ids)
    
    # Create a lookup dictionary for efficient access
    product_map = {p.id: p for p in products}
    
    for item_id, quantity in cart.items():
        # Parse item_id to get product ID and size
        parts = item_id.split('-')
        p_id_str = parts[0]
        size = parts[1] if len(parts) > 1 else None
        
        if not p_id_str.isdigit():
            continue
            
        product = product_map.get(int(p_id_str))
        if product:
            price = product.sale_price if product.is_sale else product.price
            item_total = price * quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total_price': item_total,
                'size': size,
                'item_id': item_id  # Pass the unique key for removing/updating
            })
            total_amount += item_total
            
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    
    if item_id in cart:
        del cart[item_id]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    
    return redirect('cart_detail')

@require_POST
def update_cart(request):
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity'))
        
        cart = request.session.get('cart', {})
        
        if item_id in cart:
            if quantity > 0:
                cart[item_id] = quantity
            else:
                del cart[item_id]
            
            request.session['cart'] = cart
            
            # Recalculate totals
            total_amount = 0
            item_total = 0
            
            # Helper to get price
            product_ids = set()
            for key in cart.keys():
                pid = key.split('-')[0]
                if pid.isdigit():
                    product_ids.add(int(pid))
            
            products = Product.objects.filter(id__in=product_ids)
            product_map = {p.id: p for p in products}
            
            for key, val in cart.items():
                pid_str = key.split('-')[0]
                if not pid_str.isdigit():
                    continue
                    
                p = product_map.get(int(pid_str))
                if p:
                    price = p.sale_price if p.is_sale else p.price
                    t = price * val
                    total_amount += t
                    if key == item_id:
                        item_total = t
            
            return JsonResponse({
                'success': True,
                'item_total': item_total,
                'total_amount': total_amount
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def change_item_size(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        product_id = request.POST.get('product_id')
        new_size = request.POST.get('new_size')
        
        cart = request.session.get('cart', {})
        
        if item_id in cart and new_size:
            quantity = cart[item_id]
            
            # Check if sizes are same
            # item_id: "pk-size", new_key: "pk-new_size"
            # If size is same, skip
            
            # Assuming item_id format is correct
            pk_part = item_id.split('-')[0]
            if pk_part != str(product_id):
                messages.error(request, "Invalid product details.")
                return redirect('cart_detail')
                
            new_key = f"{product_id}-{new_size}"
            
            if new_key == item_id:
                return redirect('cart_detail')
                
            del cart[item_id]
            
            if new_key in cart:
                cart[new_key] += quantity
            else:
                cart[new_key] = quantity
                
            request.session['cart'] = cart
            messages.success(request, "Size updated successfully.")
            
    return redirect('cart_detail')

def checkout(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please login to place an order.")
            return redirect('login')
            
        try:
            customer = Customer.objects.get(email=request.user.email)
        except Customer.DoesNotExist:
            messages.error(request, "Customer account not found.")
            return redirect('home')

        # Address Logic
        selected_address_id = request.POST.get('selected_address_id')
        address = None
        
        if selected_address_id:
            try:
                address = CustomerDetails.objects.get(id=selected_address_id, customer=customer)
            except CustomerDetails.DoesNotExist:
                 messages.error(request, "Selected address not found.")
                 return redirect('checkout')
        else:
            # Create New Address
            country_id = request.POST.get('country')
            state_id = request.POST.get('state')
            address_line_1 = request.POST.get('address_line_1')
            city = request.POST.get('city')
            postcode = request.POST.get('postcode')
            
            if not (country_id and address_line_1 and city and postcode):
                 messages.error(request, "Please fill all required address fields.")
                 return redirect('checkout')
                 
            country_inst = Country.objects.filter(id=country_id).first()
            state_inst = State.objects.filter(id=state_id).first() if state_id else None
            
            address = CustomerDetails.objects.create(
                customer=customer,
                address_line_1=address_line_1,
                address_line_2=request.POST.get('address_line_2', ''),
                city=city,
                state=state_inst,
                country=country_inst,
                postcode=postcode,
                order_notes=request.POST.get('order_notes', '')
            )
            
        # Process Cart
        cart = request.session.get('cart', {})
        if not cart:
             messages.error(request, "Your cart is empty.")
             return redirect('product_list')

        # Get Products
        product_ids = set()
        for key in cart.keys():
            pid = key.split('-')[0]
            if pid.isdigit():
                product_ids.add(int(pid))
        
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}
        
        created_order_ids = []
        
        for item_id, quantity in cart.items():
             parts = item_id.split('-')
             # Skip invalid keys
             if not parts[0].isdigit():
                 continue
                 
             p_id = int(parts[0])
             size = parts[1] if len(parts) > 1 else ''
             
             product = product_map.get(p_id)
             if product:
                 new_order = Order.objects.create(
                     product=product,
                     customer=customer,
                     quantity=quantity,
                     address=address,
                     phone=request.POST.get('phone', ''),
                     size=size,
                     status='pending'
                 )
                 created_order_ids.append(str(new_order.id))
        
        # Clear Cart
        request.session['cart'] = {}
        # messages.success(request, "Order placed successfully!")
        
        # Redirect to WhatsApp
        if created_order_ids:
            ids_str = ", ".join(created_order_ids)
            msg = f"Hello, I have placed an order. Order IDs: {ids_str}"
            whatsapp_url = f"https://wa.me/918078956972?text={quote(msg)}"
            return redirect(whatsapp_url)

        return redirect('home')
        
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    # Extract authentic product IDs from complex keys
    product_ids = set()
    for key in cart.keys():
        # Key format: "id-size" or "id"
        pid = key.split('-')[0]
        if pid.isdigit():
            product_ids.add(int(pid))
            
    products = Product.objects.filter(id__in=product_ids)
    
    # Create a lookup dictionary for efficient access
    product_map = {p.id: p for p in products}
    
    for item_id, quantity in cart.items():
        # Parse item_id to get product ID and size
        parts = item_id.split('-')
        p_id_str = parts[0]
        size = parts[1] if len(parts) > 1 else None
        
        if not p_id_str.isdigit():
            continue
            
        product = product_map.get(int(p_id_str))
        if product:
            price = product.sale_price if product.is_sale else product.price
            item_total = price * quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total_price': item_total,
                'size': size,
                'item_id': item_id  # Pass the unique key for removing/updating
            })
            total_amount += item_total
            
    countries = Country.objects.all().order_by('name')
    
    user_addresses = []
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email=request.user.email)
            user_addresses = CustomerDetails.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            pass

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'countries': countries,
        'user_addresses': user_addresses
    })

def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}.")
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    context = {"form": form}
    if next_url:
        context['next'] = next_url
        
    return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect('home')

def create_account(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not email:
            messages.error(request, "Email is required.")
            return redirect('create_account')
            
        if password != confirm_password:
             messages.error(request, "Passwords do not match.")
             return redirect('create_account')

        if User.objects.filter(username=email).exists():
             messages.error(request, "User with this email already exists.")
             return redirect('create_account')
        
        # Create User
        try:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
            user.save()
            
            # Create Customer
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                password=password
            )
            customer.save()
            
            messages.success(request, "Account created successfully. Please login.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('create_account')
        
    return render(request, 'create_account.html')

@login_required
def customer_details(request):
    # Retrieve customer based on logged-in user's email
    try:
        customer = Customer.objects.get(email=request.user.email)
    except Customer.DoesNotExist:
        messages.error(request, "Customer account not found.")
        return redirect('home')

    if request.method == 'POST':
        country_id = request.POST.get('country')
        address_line_1 = request.POST.get('address_line_01')
        address_line_2 = request.POST.get('address_line_02')
        city = request.POST.get('town_city')
        state_id = request.POST.get('state')
        postcode = request.POST.get('postcode_zip')
        order_notes = request.POST.get('order_notes')

        if country_id and address_line_1 and city and postcode:
            # Get Country and State instances
            country_inst = None
            if country_id:
                country_inst = Country.objects.filter(id=country_id).first()
            
            state_inst = None
            if state_id:
                state_inst = State.objects.filter(id=state_id).first()

            # Check if this is an update
            address_id = request.POST.get('address_id')
            if address_id:
                try:
                    address = CustomerDetails.objects.get(id=address_id, customer=customer)
                    address.country = country_inst
                    address.address_line_1 = address_line_1
                    address.address_line_2 = address_line_2
                    address.city = city
                    address.state = state_inst
                    address.postcode = postcode
                    address.order_notes = order_notes
                    address.save()
                    messages.success(request, "Address details updated successfully.")
                except CustomerDetails.DoesNotExist:
                     messages.error(request, "Address not found.")
            else:
                CustomerDetails.objects.create(
                    customer=customer,
                    country=country_inst,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    state=state_inst,
                    postcode=postcode,
                    order_notes=order_notes
                )
                messages.success(request, "Address details added successfully.")
            
            return redirect('customer_details')
        else:
            messages.error(request, "Please fill all required fields.")

    details = CustomerDetails.objects.filter(customer=customer)
    countries = Country.objects.all().order_by('name')
    
    return render(request, 'customer_details.html', {
        'customer': customer,
        'details': details,
        'countries': countries
    })

@login_required
def edit_address(request, pk):
    try:
        address = CustomerDetails.objects.get(id=pk, customer__email=request.user.email)
        # Fetch customer again as needed for context
        customer = Customer.objects.get(email=request.user.email)
        details = CustomerDetails.objects.filter(customer=customer)
        countries = Country.objects.all().order_by('name')
        
        # Determine states for the selected country to populate dropdown
        states = []
        if address.country:
             states = State.objects.filter(country=address.country).order_by('name')

        return render(request, 'customer_details.html', {
            'customer': customer,
            'details': details,
            'countries': countries,
            'editing_address': address,
            'states': states
        })
    except (CustomerDetails.DoesNotExist, Customer.DoesNotExist):
        messages.error(request, "Address or customer not found.")
        return redirect('customer_details')

@login_required
def delete_address(request, pk):
    try:
        address = CustomerDetails.objects.get(id=pk, customer__email=request.user.email)
        address.delete()
        messages.success(request, "Address deleted successfully.")
    except CustomerDetails.DoesNotExist:
        messages.error(request, "Address not found.")
    
    return redirect('customer_details')
def get_states(request):
    country_id = request.GET.get('country_id')
    if not country_id:
        return JsonResponse([], safe=False)
    
    states = State.objects.filter(country_id=country_id).order_by('name')
    data = list(states.values('id', 'name'))
    return JsonResponse(data, safe=False)

@login_required
def my_orders(request):
    try:
        customer = Customer.objects.get(email=request.user.email)
        orders = Order.objects.filter(customer=customer).order_by('-date')
    except Customer.DoesNotExist:
        orders = []
    
    return render(request, 'my_orders.html', {'orders': orders})

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
        except Order.DoesNotExist:
            messages.error(request, "Order ID not found.")
            
        return redirect('staff_orders')

    try:
        staff = Staff.objects.get(id=request.session['staff_id'])
    except Staff.DoesNotExist:
        return redirect('staff_login')
        
    orders = Order.objects.all().order_by('-date')
    return render(request, 'employee/orders.html', {'orders': orders, 'staff': staff})

