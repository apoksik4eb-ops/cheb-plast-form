from django import template

register = template.Library()


@register.filter
def price_for(product, user):
    """Возвращает цену товара для пользователя."""
    if hasattr(product, 'get_price_for'):
        return product.get_price_for(user)
    return product.price