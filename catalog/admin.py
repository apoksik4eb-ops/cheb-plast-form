from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage
from accounts.models import User


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'slug')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'preview')
    readonly_fields = ('preview',)
    verbose_name = "Фотография"
    verbose_name_plural = "Фотографии товара"

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    preview.short_description = 'Превью'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('preview', 'name', 'article', 'category', 'price',
                    'stock', 'is_active', 'manager')
    list_display_links = ('preview', 'name')
    list_filter = ('category', 'is_active', 'is_available', 'is_new', 'is_hit', 'manager')
    search_fields = ('name', 'article', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock', 'is_active')
    list_per_page = 50
    save_on_top = True
    inlines = [ProductImageInline]

    fieldsets = (
        ('Основное', {'fields': ('name', 'slug', 'article', 'category')}),
        ('Описание', {'fields': ('short_description', 'description', 'specs')}),
        ('Цена и склад', {'fields': ('price', 'price_wholesale', 'unit',
                                     'min_order', 'stock', 'is_available')}),
        ('Медиа', {'fields': ('image',)}),
        ('Публикация', {'fields': ('is_active', 'is_new', 'is_hit')}),
        ('Ответственный', {'fields': ('manager',)}),
        ('SEO', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    preview.short_description = 'Фото'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(manager=request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.manager:
            obj.manager = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.manager == request.user
        return super().has_change_permission(request, obj)