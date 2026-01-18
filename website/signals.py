import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Category, Season, Product, ProductImage, Testimonial

def delete_file_if_changed(sender, instance, field_name, **kwargs):
    """
    Deletes the old file from the filesystem if the file field has changed.
    """
    if not instance.pk:
        return False

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False

    old_file = getattr(old_instance, field_name)
    new_file = getattr(instance, field_name)

    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            try:
                os.remove(old_file.path)
            except Exception as e:
                print(f"Error deleting old file: {e}")

def delete_file_on_delete(sender, instance, field_name, **kwargs):
    """
    Deletes the file from the filesystem when the corresponding object is deleted.
    """
    file_field = getattr(instance, field_name)
    if file_field:
        if os.path.isfile(file_field.path):
            try:
                os.remove(file_field.path)
            except Exception as e:
                print(f"Error deleting file on delete: {e}")

# Category
@receiver(pre_save, sender=Category)
def category_pre_save(sender, instance, **kwargs):
    delete_file_if_changed(sender, instance, 'image')

@receiver(post_delete, sender=Category)
def category_post_delete(sender, instance, **kwargs):
    delete_file_on_delete(sender, instance, 'image')

# Product
@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    delete_file_if_changed(sender, instance, 'image')

@receiver(post_delete, sender=Product)
def product_post_delete(sender, instance, **kwargs):
    delete_file_on_delete(sender, instance, 'image')

# ProductImage
@receiver(pre_save, sender=ProductImage)
def product_image_pre_save(sender, instance, **kwargs):
    delete_file_if_changed(sender, instance, 'image')

@receiver(post_delete, sender=ProductImage)
def product_image_post_delete(sender, instance, **kwargs):
    delete_file_on_delete(sender, instance, 'image')

# Testimonial
@receiver(pre_save, sender=Testimonial)
def testimonial_pre_save(sender, instance, **kwargs):
    delete_file_if_changed(sender, instance, 'image')

@receiver(post_delete, sender=Testimonial)
def testimonial_post_delete(sender, instance, **kwargs):
    delete_file_on_delete(sender, instance, 'image')

# Season
@receiver(pre_save, sender=Season)
def season_pre_save(sender, instance, **kwargs):
    delete_file_if_changed(sender, instance, 'banner_image')

@receiver(post_delete, sender=Season)
def season_post_delete(sender, instance, **kwargs):
    delete_file_on_delete(sender, instance, 'banner_image')
