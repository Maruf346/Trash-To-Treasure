from django.shortcuts import render

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