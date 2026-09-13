from django import forms
from django.utils.html import strip_tags
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} ★") for i in range(5, 0, -1)],
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        initial=5,
        label="Оценка",
    )

    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="",
    )

    class Meta:
        model = Review
        fields = ['name', 'email', 'company', 'rating', 'title', 'text']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'company': forms.TextInput(attrs={'placeholder': 'Название компании (необязательно)'}),
            'title': forms.TextInput(attrs={'placeholder': 'Кратко о впечатлении'}),
            'text': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Расскажите о вашем опыте работы с нами...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            'w-full px-4 py-3 bg-gray-100 border-2 border-gray-400 rounded-lg '
            'text-gray-900 placeholder-gray-500 transition '
            'hover:border-gray-500 '
            'focus:outline-none focus:ring-0 focus:bg-white focus:border-brand-500'
        )

        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.RadioSelect, forms.HiddenInput)):
                continue
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = base + ' resize-none'
            else:
                field.widget.attrs['class'] = base

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Bot detected")
        return ''

    def clean_text(self):
        text = strip_tags(self.cleaned_data['text']).strip()
        if len(text) < 20:
            raise forms.ValidationError("Отзыв должен содержать минимум 20 символов")
        if len(text) > 3000:
            raise forms.ValidationError("Слишком длинный отзыв (макс. 3000 символов)")
        return text

    def clean_name(self):
        name = strip_tags(self.cleaned_data['name']).strip()
        if len(name) < 2:
            raise forms.ValidationError("Укажите имя (минимум 2 символа)")
        return name