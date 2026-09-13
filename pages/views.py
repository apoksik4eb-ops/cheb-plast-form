from django.shortcuts import render
from django.views.generic import TemplateView
from catalog.models import Product
from django.shortcuts import redirect


class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        products = Product.objects.filter(is_active=True, is_new=True).select_related('category')[:4]

        for p in products:
            p.display_price = p.get_price_for(user)
        ctx['new_products'] = products

        return ctx


def about(request):
    return render(request, 'pages/about.html')


def contacts(request):
    return render(request, 'pages/contacts.html')


def custom_404(request, exception):
    return redirect('pages:home')