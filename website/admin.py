from django.contrib import admin
from .models import (
    Category,
    Customer,
    Product,
    ProductImage,
    Order,
    Testimonial,
    Season, 
    Size,
    Subscriber,
    CustomerDetails,
)

# Register models only once
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(CustomerDetails)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(Testimonial)
admin.site.register(Season)
admin.site.register(Size)
admin.site.register(Subscriber)

class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('sizes',)

admin.site.register(Product, ProductAdmin)