from django.contrib import admin
from django.utils.html import format_html
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rating_stars', 'target', 'status', 'created_at')
    list_filter = ('status', 'rating', 'is_verified', 'created_at')
    search_fields = ('name', 'email', 'text', 'company')
    readonly_fields = ('created_at', 'updated_at', 'ip_address')
    list_editable = ('status',)
    actions = ['approve_reviews', 'reject_reviews']

    fieldsets = (
        ('Автор', {'fields': ('user', 'name', 'email', 'company')}),
        ('Отзыв', {'fields': ('product', 'rating', 'title', 'text')}),
        ('Модерация', {'fields': ('status', 'is_verified', 'admin_comment')}),
        ('Метаданные', {'fields': ('created_at', 'updated_at', 'ip_address')}),
    )

    def rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_stars.short_description = 'Оценка'

    def target(self, obj):
        return obj.product.name if obj.product else '— Компания —'
    target.short_description = 'Объект'

    @admin.action(description="Одобрить выбранные отзывы")
    def approve_reviews(self, request, queryset):
        for review in queryset:
            review.status = 'approved'
            review.save()

            if review.product:
                review.product.update_rating()
                
        self.message_user(request, f"Одобрено: {queryset.count()}")

    @admin.action(description="Отклонить выбранные отзывы")
    def reject_reviews(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"Отклонено: {queryset.count()}")