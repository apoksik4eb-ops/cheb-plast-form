from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product_name', 'price', 'quantity', 'subtotal_display')
    readonly_fields = ('product_name', 'price', 'quantity', 'subtotal_display')

    def subtotal_display(self, obj):
        if obj.pk:
            return f"{obj.subtotal} ₽"
        return '—'
    subtotal_display.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company_name', 'phone', 'total', 'status', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('status', 'payment', 'created_at')
    search_fields = ('name', 'phone', 'email', 'company_name', 'company_inn')
    list_editable = ('status',)
    readonly_fields = ('total', 'created_at', 'updated_at', 'user', 'company')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 50

    fieldsets = (
        ('Клиент', {
            'fields': ('user', 'company', 'name', 'company_name',
                       'company_inn', 'email', 'phone', 'address')
        }),
        ('Заказ', {
            'fields': ('payment', 'comment', 'status', 'total')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'price', 'quantity', 'subtotal_display')
    search_fields = ('product_name', 'order__id')
    list_filter = ('order__status',)

    def subtotal_display(self, obj):
        return f"{obj.subtotal} ₽"
    subtotal_display.short_description = 'Сумма'