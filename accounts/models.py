from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class Company(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На проверке'),
        ('active', 'Активна'),
        ('blocked', 'Заблокирована'),
    ]

    PRICE_TYPES = [
        ('retail', 'Розничные'),
        ('wholesale', 'Оптовые'),
        ('special', 'Специальные'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название компании")
    slug = models.SlugField(unique=True, blank=True)
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")
    kpp = models.CharField(max_length=9, blank=True, verbose_name="КПП")
    ogrn = models.CharField(max_length=15, blank=True, verbose_name="ОГРН")

    legal_address = models.TextField(blank=True, verbose_name="Юр. адрес")
    actual_address = models.TextField(blank=True, verbose_name="Факт. адрес")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    manager_contact = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_companies', verbose_name="Контактное лицо"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price_type = models.CharField(max_length=20, choices=PRICE_TYPES, default='retail', verbose_name="Тип цен")
    discount = models.PositiveSmallIntegerField(default=0, verbose_name="Скидка, %")

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, verbose_name="Заметки менеджера")

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:50] or 'company'
            slug = base
            i = 1

            while Company.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
            
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'active'


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='users', verbose_name="Компания"
    )
    is_company_manager = models.BooleanField(default=False, verbose_name="Менеджер компании")

    def __str__(self):
        return self.get_full_name() or self.username
