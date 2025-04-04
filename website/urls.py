from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path('about.html',views.about, name="about"),
    path('contact.html',views.contact, name="contact"),    
    path('product_list.html',views.product_list, name="product_list"),    
]
