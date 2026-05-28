from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    AdminNote,
    AuditLog,
    BulkPrice,
    Category,
    InventoryAlert,
    Order,
    OrderStatusHistory,
    PasswordResetCode,
    Product,
    Review,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Xama profile', {'fields': ('role', 'phone_number', 'address', 'two_factor_enabled', 'email_notifications_enabled')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Xama profile', {'fields': ('role', 'phone_number', 'address')}),
    )
    list_display = ('username', 'phone_number', 'role', 'is_staff', 'two_factor_enabled')
    list_filter = ('role', 'is_staff', 'is_superuser', 'two_factor_enabled')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'quantity', 'reorder_level', 'is_low_stock')
    search_fields = ('name', 'sku')
    list_filter = ('category',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'status', 'created_at', 'total')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'product__name')
    readonly_fields = ('total', 'created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'rating', 'approved', 'created_at')
    list_filter = ('rating', 'approved', 'created_at')
    search_fields = ('customer__username', 'product__name')
    actions = ['approve_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = 'Approve selected reviews'


@admin.register(BulkPrice)
class BulkPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_min', 'discount_percent')
    search_fields = ('product__name',)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'changed_at')
    search_fields = ('order__id', 'changed_by__username')
    readonly_fields = ('changed_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name')
    readonly_fields = ('timestamp', 'changes')


@admin.register(InventoryAlert)
class InventoryAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_at_alert', 'alert_sent_at')
    list_filter = ('alert_sent_at',)
    search_fields = ('product__name',)
    readonly_fields = ('alert_sent_at',)


admin.site.register(Category)
admin.site.register(AdminNote)
admin.site.register(PasswordResetCode)
