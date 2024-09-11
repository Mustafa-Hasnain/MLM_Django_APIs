from django.contrib import admin
from .models import Product, Category, SubCategory  # Import your models

# Register the Category model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_url')  # Display these fields in the list view
    search_fields = ('name',)  # Searchable fields
    fields = ('name', 'description', 'image_url')  # Fields to display in the form

# Register the SubCategory model
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the 'name' field in the list view
    search_fields = ('name',)  # Searchable field
    fields = ('name',)  # Field to display in the form

# Register the Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'category', 'sub_category', 'items_in_stock', 'is_active', 'is_featured')  # Fields to display in the list view
    search_fields = ('name', 'category__name', 'sub_category__name', 'brand')  # Searchable fields
    list_filter = ('category', 'sub_category', 'is_active', 'is_featured')  # Add filters for quick access
    fieldsets = (
        ('General Information', {
            'fields': ('name', 'description', 'price', 'discount_price', 'items_in_stock', 'brand', 'category', 'sub_category', 'image_url')
        }),
        ('Additional Information', {
            'fields': ('weight', 'dimensions', 'warranty')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),  # Make this section collapsible
        }),
    )
    readonly_fields = ('created_at', 'updated_at')  # Mark the timestamps as read-only

# Register all models to the admin site
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
