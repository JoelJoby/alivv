from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path('about.html',views.about, name="about"),
    path('contact.html',views.contact, name="contact"),    
    path('product_list.html',views.product_list, name="product_list"),    
    path('product/<int:pk>',views.product, name="product"),
    path('category/<str:cat>',views.category, name="category"),
    path('subscribe', views.subscribe, name="subscribe"),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
]
