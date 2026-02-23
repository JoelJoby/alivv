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
    Country,
    State,
    Staff,
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
admin.site.register(Country)
admin.site.register(State)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('sizes',)

admin.site.register(Product, ProductAdmin)

from django.contrib.auth.hashers import make_password

class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('is_active', 'created_at')
    
    def save_model(self, request, obj, form, change):
        # Hash the password if it's new or has changed
        if not change or 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(Staff, StaffAdmin)