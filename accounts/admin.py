from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.utils import timezone
from .models import Company, User


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'status_badge', 'price_type', 'users_count', 'created_at')
    list_filter = ('status', 'price_type', 'created_at')
    search_fields = ('name', 'inn', 'email', 'phone')
    list_editable = ('price_type',)
    actions = ['approve_companies', 'block_companies']
    readonly_fields = ('created_at', 'approved_at', 'slug')

    fieldsets = (
        ('Реквизиты', {'fields': ('name', 'slug', 'inn', 'kpp', 'ogrn')}),
        ('Контакты', {'fields': ('legal_address', 'actual_address', 'phone', 'email', 'website')}),
        ('Управление', {'fields': ('manager_contact', 'status', 'price_type', 'discount')}),
        ('Метаданные', {'fields': ('created_at', 'approved_at', 'notes')}),
    )

    def status_badge(self, obj):
        colors = {'pending': '#f0ad4e', 'active': '#5cb85c', 'blocked': '#d9534f'}

        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:3px">{}</span>',
            colors.get(obj.status, '#999'), obj.get_status_display()
        )
    
    status_badge.short_description = 'Статус'

    def users_count(self, obj):
        return obj.users.count()
    
    users_count.short_description = 'Сотрудников'

    @admin.action(description="Одобрить компании")
    def approve_companies(self, request, queryset):
        for company in queryset:
            company.status = 'active'
            company.approved_at = timezone.now()
            company.save()

            for user in company.users.all():
                send_mail(
                    subject="Регистрация одобрена",
                    message=f"Компания «{company.name}» активирована. Можно делать заказы.",
                    from_email='noreply@poliform.ru',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                
        self.message_user(request, f"Одобрено: {queryset.count()}")

    @admin.action(description="Заблокировать компании")
    def block_companies(self, request, queryset):
        queryset.update(status='blocked')
        self.message_user(request, f"Заблокировано: {queryset.count()}")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'get_full_name', 'company', 'is_company_manager', 'is_staff')
    list_filter = ('company', 'is_company_manager', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'position', 'company', 'is_company_manager')}),
    )