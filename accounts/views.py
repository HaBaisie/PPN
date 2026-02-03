from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm


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
