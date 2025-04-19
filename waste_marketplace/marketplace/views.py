from django.shortcuts import render, redirect
from .models import UpcycledProduct
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from users.models import CustomUser  # adjust if needed
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .forms import UpcycledProductForm 
from django.contrib.contenttypes.models import ContentType
from .models import CartItem


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
    featured_products = UpcycledProduct.objects.order_by('-id')[:4]
    return render(request, 'home.html', {'featured_products': featured_products})

@login_required
def driver_dashboard(request):
    if request.user.role != 'driver':
        return HttpResponseForbidden("You are not authorized to view this page.")

    return render(request, 'driver_dashboard.html')

@login_required
def contact(request):
    return render(request, 'contact.html')

@login_required
def cart(request):
    if request.user.role == 'driver':
        return HttpResponseForbidden("You are not authorized to view this page.")

    cart_items = CartItem.objects.filter(buyer=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })
    
    
@login_required
def about(request):
    return render(request, 'about.html')

from django.core.paginator import Paginator

@login_required
def listed_products(request):
    if request.user.role != 'artisan':
        return HttpResponseForbidden("You are not authorized to view this page.")

    products = UpcycledProduct.objects.filter(artisan=request.user)

    # Pagination logic
    paginator = Paginator(products, 12) # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listed_products.html', {
        'products': products,  # Keep this if you want to use it elsewhere
        'page_obj': page_obj   # This is the one your grid uses
    })

@login_required
def order_history(request):
    if request.user.role != 'artisan':
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    # Assuming you have an Order model to fetch order history
    # orders = Order.objects.filter(buyer=request.user)
    # return render(request, 'order_history.html', {'orders': orders})
    return render(request, 'order_history.html')

@login_required
def product_listing(request):
    if request.user.role != 'artisan':
        return HttpResponseForbidden("Not allowed")

    if request.method == 'POST':
        form = UpcycledProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.artisan        = request.user
            product.approval_status = False
            product.save()
            messages.success(request, "Product listed successfully!")
            return redirect('listed_products')
    else:
        form = UpcycledProductForm()

    return render(request, 'product_listing.html', {'form': form})

def checkout(request):
    return render(request, 'checkout.html')


#profile_views

@login_required
def driver_profile(request):
    if request.user.role != 'driver':
        return HttpResponseForbidden("Access denied.")

    profile = request.user.driverprofile
    return render(request, 'driver_profile.html', {'profile': profile})

@login_required
def artisan_profile(request):
    if request.user.role != 'artisan':
        return HttpResponseForbidden("Access denied.")

    profile = request.user.artisanprofile
    return render(request, 'artisan_profile.html', {'profile': profile})

@login_required
def buyer_profile(request):
    if request.user.role != 'buyer':
        return HttpResponseForbidden("Access denied.")

    profile = request.user.buyerprofile
    return render(request, 'buyer_profile.html', {'profile': profile})


@login_required
def upcycled_product_details(request, slug):
    product = get_object_or_404(UpcycledProduct, slug=slug)
    return render(request, 'upcycled_product_details.html', {'product': product})


@login_required
def upcycled_products(request):
    products = UpcycledProduct.objects.all().order_by('-id')
    paginator = Paginator(products, 12)  # 12 products per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'upcycled_products.html', {'page_obj': page_obj})



@login_required
def edit_product(request, pk):
    product = get_object_or_404(UpcycledProduct, pk=pk, artisan=request.user)
    if request.method == 'POST':
        form = UpcycledProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('listed_products')
    else:
        form = UpcycledProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(UpcycledProduct, pk=pk, artisan=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('listed_products')
    return redirect('listed_products')


# views.py


@login_required
def add_to_cart(request, model_name, object_id):
    # 1. Identify what model we’re adding
    ct = get_object_or_404(ContentType, model=model_name)
    product = get_object_or_404(ct.model_class(), pk=object_id)

    # 2. Role‑based guardrails
    if request.user.role == 'artisan' and ct.model_class().__name__ != 'TrashMaterial':
        messages.error(request, "As an Artisan you can only add trash materials to your cart.")
        return redirect('upcycled_product_details', slug=product.slug)

    if request.user.role not in ('artisan','buyer'):
        messages.error(request, "Only Buyers or Artisans can add items to cart.")
        return redirect('upcycled_product_details', slug=product.slug)

    # 3. Quantity from POST, clamped to [1..stock]
    qty = int(request.POST.get('quantity', 1))
    qty = max(1, min(qty, product.stock_availability))

    # 4. Create or update
    cart_item, created = CartItem.objects.get_or_create(
        buyer=request.user,
        content_type=ct,
        object_id=object_id,
        defaults={'quantity': qty}
    )
    if not created:
        cart_item.quantity = min(cart_item.quantity + qty, product.stock_availability)
        cart_item.save()

    messages.success(request, "Item added to cart!")
    return redirect(request.POST.get('next') or 'upcycled_product_details', slug=product.slug)


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, buyer=request.user)
    item.delete()
    return redirect('cart')
