from django.shortcuts import render, redirect
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