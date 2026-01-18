from django.db import models
import datetime
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to='uploads/category/', 
        default='default/category_default.jpg',
        help_text="Please upload an image for the category in 520*435 resolution."
    )
    is_top_category = models.BooleanField(default=False, help_text="Select this to mark as a Top Category")
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Use 1, 2, or 3 to define order for top categories. Leave as 0 if not a top category."
    )

    def get_url_name(self):
        return slugify(self.name)
    
    def __str__(self):
        return self.name
    
class Season(models.Model):
    name = models.CharField(max_length=100)
    banner_image = models.ImageField(
        upload_to='uploads/seasons/',
        help_text="Please upload an image for the Home Page Banner in 1080*800 resolution.")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name        = models.CharField(max_length=100)
    price       = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=300, default='', blank=True, null=True)
    image       = models.ImageField(
        upload_to='uploads/products/',
        help_text="Please upload an image for the product in 360*250 resolution.")
    
    # Sale Stuff
    is_sale     = models.BooleanField(default=False)
    sale_price  = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    
    # Top Product Fields
    is_top_product = models.BooleanField(default=False, help_text="Mark as Top Product (max 6)")
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Use numbers 1 to 6 for top product priority. Leave 0 if not top."
    )

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='uploads/products/images/')
    alt_text = models.CharField(max_length=100, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='uploads/testimonials/', 
        default='default/testimonial_default.jpg'
    )
    remark = models.TextField()

    def __str__(self):
        return self.name
    
    # this is the code for phase 2 of the project

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=250, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.product
