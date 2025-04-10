from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserSignupForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Logs the user in after signup
            return redirect('home')  # Change 'home' to your desired redirect page
    else:
        form = CustomUserSignupForm()
    return render(request, 'signup.html', {'form': form})
