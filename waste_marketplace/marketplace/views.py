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
from .models import CartItem, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_lib import SSLCOMMERZ 
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

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



@csrf_exempt
def place_order(request):
    if request.method == "POST":
        cart_items = CartItem.objects.filter(buyer=request.user)
        if not cart_items.exists():
            return redirect_with_message("Your cart is empty.")

        # Calculate subtotal
        subtotal = sum(item.subtotal() for item in cart_items)

        # Create order
        order = Order.objects.create(
            buyer=request.user,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            company=request.POST.get("company"),
            country=request.POST.get("country"),
            street_address=request.POST.get("street_address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            zip_code=request.POST.get("zip"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            payment_method=request.POST.get("payment_method"),
            total_amount=Decimal(subtotal),
        )

        # Create OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                content_type=item.content_type,
                object_id=item.object_id,
                quantity=item.quantity,
                price=item.item.price
            )

        # Clear user's cart
        cart_items.delete()

        return redirect('order_success')

    return redirect('checkout')



@csrf_exempt
def initiate_payment(request):
    if request.method != 'POST':
        return redirect('checkout')

    post_data = request.POST
    user = request.user

    # 1) Gather cart
    cart_items = CartItem.objects.filter(buyer=user)
    if not cart_items.exists():
        return redirect_with_message("Your cart is empty.")

    subtotal = sum(item.subtotal() for item in cart_items)

    # 2) Pre-create Order (Pending)
    order = Order.objects.create(
        buyer=user,
        first_name=post_data.get("first_name"),
        last_name=post_data.get("last_name"),
        company=post_data.get("company"),
        country=post_data.get("country"),
        street_address=post_data.get("street_address"),
        city=post_data.get("city"),
        state=post_data.get("state"),
        zip_code=post_data.get("zip"),
        phone=post_data.get("phone"),
        email=post_data.get("email"),
        payment_method='sslcommerz',
        total_amount=Decimal(subtotal),
        payment_status='Pending',
        delivery_status='Ready',
    )

    # 3) Create its OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            content_type=item.content_type,
            object_id=item.object_id,
            quantity=item.quantity,
            price=item.item.price
        )

    # 4) Save pending order ID in session
    request.session['pending_order_id'] = order.id

    # 5) Build SSLCommerz payload using order.id as tran_id
    store_id = 'trash680a853212384'
    store_passwd = 'trash680a853212384@ssl'
    gateway = SSLCOMMERZ({
        'store_id': store_id,
        'store_pass': store_passwd,
        'issandbox': True
    })

    data = {
        'total_amount': subtotal,
        'currency': "BDT",
        'tran_id': f"TTS_{order.id}",
        'success_url': request.build_absolute_uri('/payment/success/'),
        'fail_url':    request.build_absolute_uri('/payment/fail/'),
        'cancel_url':  request.build_absolute_uri('/payment/cancel/'),
        'ipn_url':     request.build_absolute_uri('/payment/ipn/'),
        'cus_name':    f"{order.first_name} {order.last_name}",
        'cus_email':   order.email,
        'cus_phone':   order.phone,
        'cus_add1':    order.street_address,
        'cus_city':    order.city,
        'cus_country': order.country,
        'shipping_method': "NO",
        'product_name': "TrashToTreasure Order",
        'product_category': "General",
        'product_profile': "general",
    }

    response = gateway.createSession(data)
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
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    if not tran_id or not tran_id.startswith("TTS_"):
        return redirect_with_message("❌ Invalid transaction ID.")
    
    order_id = tran_id.replace("TTS_", "")
    order = get_object_or_404(Order, id=order_id)

    # Same steps as before
    order.payment_status = 'Paid'
    order.save()
    CartItem.objects.filter(buyer=order.buyer).delete()
    
    return redirect_with_message("✅ Payment successful and order placed!")

@csrf_exempt
def payment_fail(request):
    return redirect_with_message("❌ Payment failed.")

@csrf_exempt
def payment_cancel(request):
    return redirect_with_message("⚠️ Payment canceled.")

@csrf_exempt
def payment_ipn(request):
    return HttpResponse("IPN received.")

@csrf_exempt
def order_success(request):
    return redirect_with_message("Order placed successfully!")

@login_required
def my_orders(request):
    # Get orders for the logged-in user
    orders = Order.objects.filter(buyer=request.user)  # Assuming user is a ForeignKey in Order model
    
    context = {
        'orders': orders
    }

    return render(request, 'my_orders.html', context)

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # You can fetch related items like this if using ForeignKey or related_name
    ordered_items = order.items.all()  # Adjust if using another relation

    return render(request, 'order_details.html', {
        'order': order,
        'ordered_items': ordered_items,
    })

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.delivery_status in ['ready', 'packed']:
        order.delivery_status = 'cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled successfully.")
    elif order.delivery_status == 'on the way':
        messages.warning(request, f"Order #{order.id} is on the way and cannot be cancelled.")
    else:
        messages.error(request, f"Order #{order.id} cannot be cancelled at this stage.")

    return redirect('my_orders')  # Adjust this to your actual orders list view name