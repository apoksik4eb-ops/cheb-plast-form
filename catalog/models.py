# catalog/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:50]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    article = models.CharField(max_length=50, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_wholesale = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, default='шт')
    min_order = models.PositiveIntegerField(default=1)
    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to='products/', blank=True, null=True)
    specs = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    is_hit = models.BooleanField(default=False)

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_products'
    )

    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.article} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:50] or 'product'
            slug = base
            i = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    def get_price_for(self, user):
        if not user.is_authenticated:
            return None

        base = self.price

        if user.company:
            c = user.company

            if c.price_type == 'wholesale' and self.price_wholesale:
                base = self.price_wholesale

            if c.discount:
                base = base * (100 - c.discount) / 100

        return round(base, 2)

    def update_rating(self):
        from django.db.models import Avg, Count
        agg = self.reviews.filter(status='approved').aggregate(avg=Avg('rating'), count=Count('id'))
        
        self.rating_avg = agg['avg'] or 0
        self.rating_count = agg['count'] or 0
        self.save(update_fields=['rating_avg', 'rating_count'])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Фото для {self.product.name}"