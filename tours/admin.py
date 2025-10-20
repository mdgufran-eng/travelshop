from django.contrib import admin
from .models import Product, Booking

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price_per_person", "capacity_per_day", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("name",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("product", "date", "customer_name", "num_pax", "status", "created_at")
    list_filter = ("status", "date", "product")
    search_fields = ("customer_name", "customer_email")
    autocomplete_fields = ("product",)
    date_hierarchy = "date"
