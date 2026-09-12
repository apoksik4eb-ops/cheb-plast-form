from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from catalog.models import Product
from .cart import Cart
from .models import Order, OrderItem
from .forms import OrderForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_available=True)
    quantity = int(request.POST.get('quantity', 1))
    update = request.POST.get('update') == '1'
    cart.add(product, quantity, update=update, user=request.user)

    messages.success(request, f"«{product.name}» добавлен в корзину")

    return redirect(request.POST.get('next', 'orders:cart_detail'))


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(get_object_or_404(Product, id=product_id))

    messages.info(request, "Товар удалён")

    return redirect('orders:cart_detail')


def cart_detail(request):
    cart = Cart(request)

    return render(request, 'orders/cart.html', {'cart': cart})


def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Корзина пуста")
        return redirect('catalog:list')

    user = request.user
    if user.is_authenticated and user.company and user.company.status != 'active':
        messages.warning(request, "Заказы доступны после одобрения компании")
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if user.is_authenticated:
                    order.user = user
                    order.company = user.company
                    if user.company:
                        order.company_name = user.company.name
                        order.company_inn = user.company.inn
                order.total = cart.get_total()
                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        product_name=item['product'].name,
                        price=item['price'],
                        quantity=item['quantity'],
                    )

            cart.clear()
            _send_order_email(order)

            return redirect('orders:order_success', pk=order.pk)
    else:
        initial = {}
        if user.is_authenticated:
            initial = {
                'name': user.get_full_name() or user.username,
                'email': user.email,
            }
            if user.company:
                initial['company_name'] = user.company.name
                initial['company_inn'] = user.company.inn
        form = OrderForm(initial=initial)

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


def order_success(request, pk):
    """Страница успешного оформления заказа"""
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/order_success.html', {'order': order})


def _send_order_email(order):
    """Отправка уведомления менеджеру о новом заказе"""
    items = "\n".join(
        f"  - {i.product_name} × {i.quantity} = {i.subtotal} ₽"
        for i in order.items.all()
    )
    text = (
        f"Новый заказ №{order.id}\n\n"
        f"Клиент: {order.name}\n"
        f"Компания: {order.company_name or 'физлицо'}\n"
        f"ИНН: {order.company_inn or '—'}\n"
        f"Телефон: {order.phone}\n"
        f"Email: {order.email}\n"
        f"Оплата: {order.get_payment_display()}\n\n"
        f"Состав:\n{items}\n\n"
        f"ИТОГО: {order.total} ₽\n\n"
        f"Комментарий: {order.comment}"
    )
    try:
        send_mail(
            subject=f"Заказ №{order.id} с сайта",
            message=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.MANAGER_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass