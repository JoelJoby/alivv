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
    path('cart/remove/<str:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/change-size/', views.change_item_size, name='change_item_size'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_account/', views.create_account, name='create_account'),
    path('customer_details/', views.customer_details, name='customer_details'),
    path('get_states/', views.get_states, name='get_states'),
    path('customer_details/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('customer_details/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('employee/login/', views.staff_login, name='staff_login'),
    path('employee/logout/', views.staff_logout, name='staff_logout'),
    path('employee/dashboard/', views.staff_dashboard, name='staff_dashboard'),
]
