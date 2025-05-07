from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административная панель для категорий"""
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Административная панель для товаров"""
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    """Встроенная админка для товаров в заказе"""
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Административная панель для заказов"""
    list_display = ['id', 'user', 'full_name', 'email', 'address', 'city', 'created', 'status']
    list_filter = ['created', 'updated', 'status']
    list_editable = ['status']
    inlines = [OrderItemInline]