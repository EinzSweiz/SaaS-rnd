from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from auth.forms import RegistrationForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email or password are not correct')
            return redirect('login')

    return render(request, 'auth/auth.html', {})


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Everything passed very well!")
            return redirect('home')
        else:
            return redirect('register/')
    return render(request, 'auth/register.html', {' form':RegistrationForm()})

def logout_view(request):
    logout(request)
    return redirect('home')