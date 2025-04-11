from django.shortcuts import render, redirect
from .models import UpcycledProduct
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from users.models import CustomUser  # adjust if needed
from django.http import HttpResponseForbidden


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == role:
                login(request, user)
                if role == 'driver':
                    return redirect('driver_dashboard')
                else:
                    return redirect('home')  # or redirect based on role if you want
            else:
                messages.error(request, 'Invalid role selected.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def driver_dashboard(request):
    if request.user.role != 'driver':
        return HttpResponseForbidden("You are not authorized to view this page.")

    return render(request, 'driver_dashboard.html')

def contact(request):
    return render(request, 'contact.html')

@login_required
def cart(request):
    if request.user.role == 'driver':
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    return render(request, 'cart.html')

def about(request):
    return render(request, 'about.html')

@login_required
def product_listing(request):
    # ✅ Allow only artisans
    if request.user.role != 'artisan':
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_availability = request.POST.get('stock_availability')
        product_images = request.FILES.get('product_images')
        tags = request.POST.get('tags')
        
        # Assuming the logged-in user is the artisan
        artisan_name = request.user.get_full_name()  # Example: Get artisan's name
        # ✅ Make sure you access the correct artisan profile for shop location
        artisan_profile = getattr(request.user, 'artisanprofile', None)
        location = request.user.profile.shop_location  # Assuming shop location is in the user's profile

        # Create and save the UpcycledProduct instance
        UpcycledProduct.objects.create(
            product_name=product_name,
            category=category,
            description=description,
            price=price,
            stock_availability=stock_availability,
            product_images=product_images,
            location=location,
            artisan_name=artisan_name,
            artisan_contact_info=request.user.email,
            tags=tags,
            approval_status=False,  # Pending admin approval
            listing_date=date.today(),  # Capture the current date
        )

        return redirect('product_listing')  # Redirect back after submission

    return render(request, 'product_listing.html')

def checkout(request):
    return render(request, 'checkout.html')