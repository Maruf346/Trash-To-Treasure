from django.shortcuts import render, redirect
from .models import UpcycledProduct
from datetime import date
from django.contrib.auth.decorators import login_required


# Create your views here.
def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def home(request):
    return render(request, 'home.html')

def driver_dashboard(request):
    return render(request, 'driver_dashboard.html')

def contact(request):
    return render(request, 'contact.html')

def cart(request):
    return render(request, 'cart.html')

def about(request):
    return render(request, 'about.html')

@login_required
def product_listing(request):
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