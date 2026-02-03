from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import CustomUser


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if user.is_approved:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'registration/pending.html')
        else:
            # Log errors to console and notify user
            print('Registration form errors:', form.errors.as_json())
            messages.error(request, 'There were errors with your submission. Please correct them below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def approver_dashboard(request):
    # Only approver users (or staff) can access
    if not (request.user.user_type == 'approver' or request.user.is_staff):
        return HttpResponseForbidden('Forbidden')

    pending = CustomUser.objects.filter(is_approved=False, user_type__in=['policymaker', 'analyst'])
    return render(request, 'approver/panel.html', {'pending': pending})


@login_required
def approve_user(request, user_id):
    if not (request.user.user_type == 'approver' or request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
    try:
        u = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('approver_dashboard')

    if request.method == 'POST':
        u.is_approved = True
        u.save()
        messages.success(request, f'Approved user {u.username}')
    return redirect('approver_dashboard')
