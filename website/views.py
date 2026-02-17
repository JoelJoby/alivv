from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms 
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.models import User
from .models import Product,Category,Testimonial,Season,Subscriber,Size,Customer,CustomerDetails, Country, State

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
            
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
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
        country = request.POST.get('country')
        address_line_1 = request.POST.get('address_line_01')
        address_line_2 = request.POST.get('address_line_02')
        city = request.POST.get('town_city')
        district = request.POST.get('district')
        postcode = request.POST.get('postcode_zip')
        order_notes = request.POST.get('order_notes')

        if country and address_line_1 and city and postcode:
            CustomerDetails.objects.create(
                customer=customer,
                country=country,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                district=district,
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
def get_states(request):
    country_id = request.GET.get('country_id')
    if not country_id:
        return JsonResponse([], safe=False)
    
    states = State.objects.filter(country_id=country_id).order_by('name')
    data = list(states.values('id', 'name'))
    return JsonResponse(data, safe=False)
