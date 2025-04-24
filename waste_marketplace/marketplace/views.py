from django.shortcuts import render, redirect
from .models import UpcycledProduct, TrashItem
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
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_lib import SSLCOMMERZ 
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

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
    featured_trash_items = TrashItem.objects.order_by('-id')[:4]  # or any filter you like

    context = {
        'featured_products': featured_products,
        'featured_trash_items': featured_trash_items,
    }
    return render(request, 'home.html', context)


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

@login_required
def checkout(request):
    # 1) grab all cart items for the current user
    cart_items = CartItem.objects.filter(buyer=request.user)

    # 2) compute the overall subtotal
    subtotal = sum(item.subtotal() for item in cart_items)

    # 3) render with both in the context
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
    })

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
    if request.user.role == 'artisan' and ct.model_class().__name__ != 'TrashItem':
        messages.error(request, "As an Artisan you can only add trash materials to your cart.")
        # Determine which detail view to redirect to based on product type
        if isinstance(product, TrashItem):
            return redirect('trash_item_details', slug=product.slug)
        else:
            return redirect('upcycled_product_details', slug=product.slug)


    if request.user.role not in ('artisan','buyer'):
        messages.error(request, "Only Buyers or Artisans can add items to cart.")
        # Determine which detail view to redirect to based on product type
        if isinstance(product, TrashItem):
            return redirect('trash_item_details', slug=product.slug)
        else:
            return redirect('upcycled_product_details', slug=product.slug)


    # 3. Quantity from POST, clamped to [1..stock]
    qty = int(request.POST.get('quantity', 1))
    # clamp to product.quantity for trash, or product.stock_availability for upcycled
    max_stock = getattr(product, 'quantity', None) or product.stock_availability
    qty = max(1, min(qty, max_stock))

    # 4. Create or update
    cart_item, created = CartItem.objects.get_or_create(
        buyer=request.user,
        content_type=ct,
        object_id=object_id,
        defaults={'quantity': qty}
    )
    if not created:
        cart_item.quantity = min(cart_item.quantity + qty, max_stock)
        cart_item.save()

    messages.success(request, "Item added to cart!")
    
    action = request.POST.get('action')
    if action == 'buy':
        return redirect('cart')
    
    return redirect(request.POST.get('next'))


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, buyer=request.user)
    item.delete()
    return redirect('cart')


def trash_item_list(request):
    items = TrashItem.objects.filter(product_status="active")  # Add filters as needed
    paginator = Paginator(items, 12)  # Or however many per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "trash_items.html", {"page_obj": page_obj})


@login_required
def trash_item_details(request, slug):
    product = get_object_or_404(TrashItem, slug=slug)
    return render(request, 'trash_item_details.html', {'product': product})


def checkout_view(request):
    cart_items = CartItem.objects.filter(buyer=request.user)
    subtotal = sum([item.subtotal() for item in cart_items])
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
    })



@csrf_exempt  # optional, depends on SSLCommerz requirements
def place_order(request):
    if request.method == "POST":
        # You will handle order placement logic here
        return redirect('order_success')  # temporary redirection
    else:
        return redirect('checkout')


def order_success(request):
    return render(request, 'order_success.html')


@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        # collect data from checkout form
        post_data = request.POST

        store_id = 'trash680a853212384'
        store_passwd = 'trash680a853212384@ssl'

        mypayment = SSLCOMMERZ({'store_id': store_id, 'store_pass': store_passwd, 'issandbox': True})

        cart_items = CartItem.objects.filter(buyer=request.user)
        subtotal = sum(item.quantity * item.item.price for item in cart_items)
        
        data = {
            'total_amount': subtotal,  # Replace with dynamic subtotal from your cart
            'currency': "BDT",
            'tran_id': "TTS_" + str(request.user.id) + "_001",  # Generate dynamically
            'success_url': "http://127.0.0.1:8000/payment/success/",
            'fail_url': "http://127.0.0.1:8000/payment/fail/",
            'cancel_url': "http://127.0.0.1:8000/payment/cancel/",
            'ipn_url': "http://127.0.0.1:8000/payment/ipn/",
            'cus_name': post_data.get("first_name") + " " + post_data.get("last_name"),
            'cus_email': post_data.get("email"),
            'cus_phone': post_data.get("phone"),
            'cus_add1': post_data.get("street_address"),
            'cus_city': post_data.get("city"),
            'cus_country': post_data.get("country"),
            'shipping_method': "NO",
            'product_name': "TrashToTreasure Cart Checkout",
            'product_category': "Mixed",
            'product_profile': "general",
        }

        response = mypayment.createSession(data)

        # Redirect user to SSLCOMMERZ payment page
        return redirect(response['GatewayPageURL'])
    

def redirect_with_message(message):
    return HttpResponse(f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Redirecting...</title>
                <script>
                    setTimeout(function() {{
                        window.location.href = '/';
                    }}, 3000); // Redirects after 3 seconds
                </script>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background-color: #f4f4f4;
                    }}
                    .message {{
                        padding: 20px;
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                        font-size: 18px;
                        color: #333;
                    }}
                </style>
            </head>
            <body>
                <div class="message">{message} Redirecting to homepage...</div>
            </body>
        </html>
    """)

@csrf_exempt
def payment_success(request):
    return redirect_with_message("✅ Payment successful!")

@csrf_exempt
def payment_fail(request):
    return redirect_with_message("❌ Payment failed.")

@csrf_exempt
def payment_cancel(request):
    return redirect_with_message("⚠️ Payment canceled.")

@csrf_exempt
def payment_ipn(request):
    return HttpResponse("IPN received.")