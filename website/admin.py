from django.contrib import admin
from .models import (
    Category,
    Customer,
    Product,
    ProductImage,
    Order,
    Testimonial,  # If you added it
)

# Register models only once
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(Testimonial)