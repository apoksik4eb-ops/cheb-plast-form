from decimal import Decimal
from catalog.models import Product
from django.contrib.auth import get_user_model

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, update=False, user=None):
        pid = str(product.id)

        if pid not in self.cart:
            price = product.get_price_for(user) if user else product.price
            self.cart[pid] = {
                'quantity': 0,
                'price': str(price)
            }

        if update:
            self.cart[pid]['quantity'] = int(quantity)
        else:
            self.cart[pid]['quantity'] += int(quantity)
        self.save()

    def remove(self, product):
        pid = str(product.id)
        
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['subtotal'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total(self):
        return sum(
            Decimal(item['price']) * item['quantity'] for item in self.cart.values()
        )