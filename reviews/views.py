from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Count
from .models import Review
from .forms import ReviewForm


def review_list(request):
    """Список одобренных отзывов о компании"""
    reviews = Review.objects.filter(status='approved', product__isnull=True)
    stats = Review.objects.filter(status='approved').aggregate(
        avg=Avg('rating'), count=Count('id')
    )
    return render(request, 'reviews/list.html', {
        'reviews': reviews,
        'stats': stats,
    })


def review_create(request):
    """Создание отзыва"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.status = 'pending'

            if request.user.is_authenticated:
                review.user = request.user
                review.is_verified = _user_has_orders(request.user)

            review.ip_address = _get_client_ip(request)

            if _is_spam(review):
                messages.error(request, "Слишком много отзывов. Попробуйте позже.")

                return render(request, 'reviews/form.html', {'form': form})

            review.save()
            _notify_moderator(review)
            messages.success(
                request,
                "Спасибо! Ваш отзыв отправлен на модерацию. "
                "Он появится на сайте после проверки."
            )

            return redirect('reviews:success')
        
    else:
        initial = {}

        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }

            if request.user.company:
                initial['company'] = request.user.company.name

        form = ReviewForm(initial=initial)

    return render(request, 'reviews/form.html', {'form': form})


def review_success(request):
    return render(request, 'reviews/success.html')


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


def _is_spam(review):
    from django.utils import timezone
    from datetime import timedelta

    if not review.ip_address:
        return False
    hour_ago = timezone.now() - timedelta(hours=1)
    return Review.objects.filter(
        ip_address=review.ip_address,
        created_at__gte=hour_ago
    ).count() >= 3


def _user_has_orders(user):
    try:
        from orders.models import Order
        return Order.objects.filter(user=user, status='done').exists()
    except Exception:
        return False


def _notify_moderator(review):
    try:
        send_mail(
            subject=f"Новый отзыв на модерации: {review.name}",
            message=(
                f"Автор: {review.name}\n"
                f"Email: {review.email}\n"
                f"Компания: {review.company or '—'}\n"
                f"Оценка: {review.rating}/5\n\n"
                f"{review.text}\n\n"
                f"Модерировать: /admin/reviews/review/{review.id}/change/"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.MANAGER_EMAIL],
            fail_silently=True,
        )
        
    except Exception:
        pass