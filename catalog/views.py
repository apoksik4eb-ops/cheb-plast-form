from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category')
        slug = self.kwargs.get('slug')
        if slug:
            qs = qs.filter(category__slug=slug)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(article__icontains=q) |
                Q(short_description__icontains=q)
            )
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'new':
            qs = qs.order_by('-created_at')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        for product in ctx['products']:
            product.display_price = product.get_price_for(user)

        ctx['categories'] = Category.objects.all()
        ctx['current_category'] = self.kwargs.get('slug')
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        self.object.display_price = self.object.get_price_for(user)

        related = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(pk=self.object.pk)[:4]
        for p in related:
            p.display_price = p.get_price_for(user)

        ctx['reviews'] = self.object.reviews.filter(status='approved')[:10]
        ctx['gallery'] = self.object.gallery.all()
        ctx['related'] = related
        return ctx