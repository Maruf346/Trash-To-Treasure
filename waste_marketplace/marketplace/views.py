from django.shortcuts import render

# Create your views here.
def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def home(request):
    return render(request, 'home.html')