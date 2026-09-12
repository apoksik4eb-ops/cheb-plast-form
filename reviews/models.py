from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Review(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Опубликован'),
        ('rejected', 'Отклонён'),
    ]

    # Автор
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviews'
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    company = models.CharField(max_length=150, blank=True, verbose_name="Компания")

    # Контент
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    title = models.CharField(max_length=150, blank=True, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст отзыва")

    # Что оцениваем
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE,
        null=True, blank=True, related_name='reviews',
        verbose_name="Товар"
    )

    # Модерация
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False, verbose_name="Подтверждённый заказ")
    admin_comment = models.TextField(blank=True, verbose_name="Комментарий модератора")

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        target = self.product.name if self.product else "Компания"
        return f"{self.name} → {target} ({self.rating}★)"

    def get_absolute_url(self):
        return reverse('reviews:list')