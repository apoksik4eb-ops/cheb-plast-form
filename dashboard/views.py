from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from orders.models import Order
from orders.cart import Cart


class DashboardHome(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        company = user.company

        if company:
            orders = Order.objects.filter(company=company)
        else:
            orders = Order.objects.filter(user=user)

        ctx['company'] = company
        ctx['orders_total'] = orders.count()
        ctx['orders_active'] = orders.exclude(status__in=['done', 'canceled']).count()
        ctx['orders_last'] = orders.order_by('-created_at')[:5]
        ctx['total_sum'] = orders.filter(status='done').aggregate(s=Sum('total'))['s'] or 0
        return ctx


class OrderList(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard/order_list.html'
    paginate_by = 20
    context_object_name = 'orders'

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related('items')
        if user.company:
            if user.is_company_manager or user.is_superuser:
                qs = qs.filter(company=user.company)
            else:
                qs = qs.filter(user=user)
        else:
            qs = qs.filter(user=user)

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        return qs.order_by('-created_at')


class OrderDetail(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'dashboard/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related('items')
        if user.company and (user.is_company_manager or user.is_superuser):
            return qs.filter(company=user.company)
        return qs.filter(user=user)


@require_POST
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status not in ('new', 'processing'):
        messages.error(request, "Заказ уже в работе, отмена невозможна")
        return redirect('dashboard:order_detail', pk=pk)
    order.status = 'canceled'
    order.save(update_fields=['status'])
    messages.success(request, f"Заказ №{order.id} отменён")
    return redirect('dashboard:order_list')


@require_POST
def order_repeat(request, pk):
    old = get_object_or_404(Order, pk=pk, user=request.user)
    cart = Cart(request)
    for item in old.items.all():
        if item.product.is_available:
            cart.add(item.product, item.quantity)
    messages.success(request, "Товары из заказа добавлены в корзину")
    return redirect('orders:cart_detail')