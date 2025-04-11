from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserSignupForm
from .models import DriverProfile, ArtisanProfile, BuyerProfile

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # ✅ Create profile based on role
            if user.role == 'buyer':
                BuyerProfile.objects.create(user=user)
            elif user.role == 'driver':
                DriverProfile.objects.create(user=user)
            elif user.role == 'artisan':
                ArtisanProfile.objects.create(user=user)

            messages.success(request, 'Signup successful. Please log in.')
            return redirect('login')
    else:
        form = CustomUserSignupForm()

    return render(request, 'signup.html', {'form': form})
