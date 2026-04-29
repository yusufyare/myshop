from django.contrib import admin
from .models import Category, Product

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    # Added a comma after 'name'
    prepopulated_fields = {'slug': ('name',)} 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'price',
        'available',
        'created',
        'updated'
    ]
    # Changed st_filter to list_filter
    list_filter = ['available', 'created', 'updated'] 
    list_editable = ['price', 'available']
    # Added a comma after 'name'
    prepopulated_fields = {'slug': ('name',)}