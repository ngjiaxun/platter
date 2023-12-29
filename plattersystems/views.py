from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm


def home(request):
    return redirect('/multiuser/organisation/')

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/multiuser/organisation/')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})