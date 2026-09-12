from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Company


class CompanyRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, label="Название компании")
    inn = forms.CharField(max_length=12, label="ИНН")
    kpp = forms.CharField(max_length=9, required=False, label="КПП")
    ogrn = forms.CharField(max_length=15, required=False, label="ОГРН")
    legal_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        label="Юридический адрес"
    )
    company_phone = forms.CharField(max_length=20, label="Телефон компании")
    company_email = forms.EmailField(label="Email компании")

    first_name = forms.CharField(max_length=100, label="Имя")
    last_name = forms.CharField(max_length=100, label="Фамилия")
    phone = forms.CharField(max_length=20, required=False, label="Личный телефон")

    agree = forms.BooleanField(
        label="Согласен на обработку персональных данных",
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            'w-full px-4 py-3 bg-gray-100 border-2 border-gray-400 rounded-lg '
            'text-gray-900 placeholder-gray-500 transition '
            'hover:border-gray-500 '
            'focus:outline-none focus:bg-white focus:border-brand-500'
        )
        for name, field in self.fields.items():
            if field.widget.__class__.__name__ == 'CheckboxInput':
                field.widget.attrs['class'] = 'w-4 h-4 text-brand-600 rounded focus:ring-brand-500'
            else:
                field.widget.attrs['class'] = base
                field.widget.attrs.setdefault('placeholder', field.label or name)

        self.fields['company_name'].widget.attrs['autofocus'] = True

    def clean_inn(self):
        inn = self.cleaned_data['inn']
        if not inn.isdigit() or len(inn) not in (10, 12):
            raise forms.ValidationError("ИНН: 10 или 12 цифр")
        if Company.objects.filter(inn=inn).exists():
            raise forms.ValidationError("Компания с таким ИНН уже зарегистрирована")
        return inn

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email уже используется")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'position')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            'w-full px-4 py-3 bg-gray-100 border-2 border-gray-400 rounded-lg '
            'text-gray-900 focus:outline-none focus:bg-white focus:border-brand-500'
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = base


class StyledLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            'w-full px-4 py-3 bg-gray-100 border-2 border-gray-400 rounded-lg '
            'text-gray-900 placeholder-gray-500 transition '
            'hover:border-gray-500 '
            'focus:outline-none focus:bg-white focus:border-brand-500'
        )
        self.fields['username'].widget.attrs.update({
            'class': base,
            'placeholder': 'Введите логин',
        })
        self.fields['password'].widget.attrs.update({
            'class': base,
            'placeholder': 'Введите пароль',
        })