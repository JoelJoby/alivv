from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('orders/', views.staff_orders, name='staff_orders'),
    path('categories/', views.staff_categories, name='staff_categories'),
    path('products/', views.staff_products, name='staff_products'),
    path('product-images/', views.staff_all_product_images, name='staff_all_product_images'),
    path('products/<int:product_id>/images/', views.staff_product_images, name='staff_product_images'),
]
