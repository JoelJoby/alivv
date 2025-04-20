from django.shortcuts import render
from .models import Product

# Create your views here.

def home(request):
    return render(request, 'home.html', {})

def about(request):
    return render(request, 'about.html', {})

def contact(request):
    return render(request, 'contact.html', {}) 

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})