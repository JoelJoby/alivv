from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django import forms 

from .models import Product,Category,Testimonial,Season,Subscriber

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

    return render(request, 'product.html', {
        'product': product,
        'product_url': product_url,
        'product_images': product_images,
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
        cart = request.session.get('cart', {})
        
        # Ensure cart keys are strings (JSON serialization)
        pk_str = str(pk)
        
        if pk_str in cart:
            cart[pk_str] += quantity
        else:
            cart[pk_str] = quantity
            
        request.session['cart'] = cart
        messages.success(request, f"{product.name} added to cart successfully!")
        return redirect('product', pk=pk)
    else:
        return redirect('product', pk=pk)

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    # Get all product IDs from cart
    product_ids = [int(k) for k in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    
    # Create a lookup dictionary for efficient access
    product_map = {p.id: p for p in products}
    
    for pk_str, quantity in cart.items():
        product = product_map.get(int(pk_str))
        if product:
            price = product.sale_price if product.is_sale else product.price
            item_total = price * quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total_price': item_total
            })
            total_amount += item_total
            
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    pk_str = str(pk)
    
    if pk_str in cart:
        del cart[pk_str]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    
    return redirect('cart_detail')

@require_POST
def update_cart(request):
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        
        cart = request.session.get('cart', {})
        pk_str = str(product_id)
        
        if pk_str in cart:
            if quantity > 0:
                cart[pk_str] = quantity
            else:
                del cart[pk_str]
            
            request.session['cart'] = cart
            
            # Recalculate totals
            total_amount = 0
            item_total = 0
            
            product_ids = [int(k) for k in cart.keys()]
            products = Product.objects.filter(id__in=product_ids)
            product_map = {p.id: p for p in products}
            
            for k, v in cart.items():
                p = product_map.get(int(k))
                if p:
                    price = p.sale_price if p.is_sale else p.price
                    t = price * v
                    total_amount += t
                    if str(p.id) == pk_str:
                        item_total = t
            
            return JsonResponse({
                'success': True,
                'item_total': item_total,
                'total_amount': total_amount
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
