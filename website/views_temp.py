from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django import forms 
from .models import Product, Category, Testimonial, Season, Subscriber, Size

# ... (other views)

def change_item_size(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        product_id = request.POST.get('product_id')
        new_size = request.POST.get('new_size')
        
        cart = request.session.get('cart', {})
        
        if item_id in cart and new_size:
            quantity = cart[item_id]
            del cart[item_id]
            
            # Construct new key
            new_key = f"{product_id}-{new_size}"
            
            if new_key in cart:
                cart[new_key] += quantity
            else:
                cart[new_key] = quantity
                
            request.session['cart'] = cart
            messages.success(request, "Size updated successfully.")
            
    return redirect('cart_detail')
