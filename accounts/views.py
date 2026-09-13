from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from .forms import CompanyRegistrationForm, ProfileForm
from .models import Company


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                company = Company.objects.create(
                    name=form.cleaned_data['company_name'],
                    inn=form.cleaned_data['inn'],
                    kpp=form.cleaned_data.get('kpp', ''),
                    ogrn=form.cleaned_data.get('ogrn', ''),
                    legal_address=form.cleaned_data['legal_address'],
                    phone=form.cleaned_data['company_phone'],
                    email=form.cleaned_data['company_email'],
                    status='pending',
                )
                user = form.save(commit=False)
                user.company = company
                user.is_company_manager = True
                user.phone = form.cleaned_data.get('phone', '')
                user.save()
                company.manager_contact = user
                company.save()

            send_mail(
                subject=f"Новая регистрация компании: {company.name}",
                message=f"Компания: {company.name}\nИНН: {company.inn}\n"
                        f"Контакт: {user.get_full_name()} / {user.phone} / {user.email}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.MANAGER_EMAIL],
                fail_silently=True,
            )

            login(request, user)
            messages.success(request, "Регистрация принята! Компания на модерации.")
            
            return redirect('dashboard:home')
        
    else:
        form = CompanyRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")

            return redirect('accounts:profile')
        
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})