from django.contrib import admin
from .models import Category, Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_category', 'price', 'available')  
    list_filter = ('category__name', 'available')  # Filter by category's name, not just 'category'
    search_fields = ('name', 'category__name')  # Allow search by category name

    def get_category(self, obj):
        return obj.category.name  # Get the name of the associated category
    get_category.short_description = 'Category'  # Optional: Set a custom column name for 'Category'

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}  # Auto-populate slug based on category name

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
