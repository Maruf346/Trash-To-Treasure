from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserSignupForm
from .models import DriverProfile, ArtisanProfile, BuyerProfile
from django.contrib.auth.decorators import login_required
from .forms import BuyerProfileForm, CustomUserForm

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

@login_required
def buyer_profile(request):
    if request.user.role != 'buyer':
        return redirect('home')  # Block access if not a buyer

    buyer_profile = request.user.buyerprofile
    user_form = CustomUserForm(instance=request.user)
    profile_form = BuyerProfileForm(instance=buyer_profile)

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=request.user)
        profile_form = BuyerProfileForm(request.POST, instance=buyer_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('buyer_profile')  # Refresh the page

    return render(request, 'buyer_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
    
def artisan_profile(request):
    if request.user.role != 'artisan':
        return redirect('home')  # Block access if not an artisan

    artisan_profile = request.user.artisanprofile
    user_form = CustomUserForm(instance=request.user)
    profile_form = BuyerProfileForm(instance=artisan_profile)

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=request.user)
        profile_form = BuyerProfileForm(request.POST, instance=artisan_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('artisan_profile')  # Refresh the page

    return render(request, 'artisan_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
    
def driver_profile(request):
    if request.user.role != 'driver':
        return redirect('driver_dashboard')  # Block access if not a driver

    driver_profile = request.user.driverprofile
    user_form = CustomUserForm(instance=request.user)
    profile_form = BuyerProfileForm(instance=driver_profile)

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=request.user)
        profile_form = BuyerProfileForm(request.POST, instance=driver_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('driver_profile')  # Refresh the page

    return render(request, 'driver_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })