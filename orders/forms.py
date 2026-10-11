from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order

        fields = ['name', 'company_name', 'email', 'phone', 'address', 'payment', 'comment']

        labels = {
            'name': 'Контактное лицо',
            'company_name': 'Название компании',
            'email': 'Email',
            'phone': 'Телефон',
            'address': 'Адрес доставки',
            'payment': 'Способ оплаты',
            'comment': 'Комментарий'
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
            'company_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
            'payment': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500'}),
        }
