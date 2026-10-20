import smtplib
import ssl
from email.message import EmailMessage

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login
from django.conf import settings
from django.urls import reverse

from .models import Product, Order
from .forms import ProductForm, CustomRegisterForm 

def is_admin(user):
    return user.is_superuser

def home(request):
    products = Product.objects.all()

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)
    
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-id')

    return render(request, 'home.html', {'products': products})

def signup(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!") 
            return redirect('home')
    else:
        form = CustomRegisterForm()
    return render(request, 'registration/signup.html', {'form': form})

@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form, 'title': 'Add New Gadget'})

@user_passes_test(is_admin)
def delete_product(request,pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.error(request, 'Product deleted!')
        return redirect('home')
    return render(request,'store/delete_confirm.html', {'product': product})

@user_passes_test(is_admin)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.info(request, 'Product updated successfully!')
            return redirect('home')
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'store/add_product.html', {'form': form, 'title': 'Update Gadget'})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def my_orders(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to see your orders.")
        return redirect('login')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

def confirm_order(request, pk):
    # --- FIX: Login Check ---
    # If on mobile and not logged in, send them to login first
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to confirm your order.")
        return redirect(f'/accounts/login/?next={request.path}')

    order = get_object_or_404(Order, pk=pk)
    
    if request.user != order.user:
        messages.error(request, "Access Denied.")
        return redirect('home')

    if order.status == 'Confirmed':
        messages.info(request, "This order is already confirmed!") # Fixed typo: message -> messages
        return redirect('my_orders')    
    
    if request.method == 'POST':
        order.status = 'Confirmed'
        order.save()
        messages.success(request, "Success! Your order has been confirmed.")
        return redirect('my_orders')
    
    return render(request, 'store/confirm_prompt.html', {'order': order})

def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to buy this item!")
        return redirect('login')
    
    if not request.user.email:
        messages.error(request, "Please add an email address to your profile first.")
        return redirect('product_detail', pk=pk)

    order = Order.objects.create(user=request.user, product=product, status='Pending')

    relative_link = reverse('confirm_order', args=[order.pk])
    confirmation_link = request.build_absolute_uri(relative_link)

    subject = f"Action Required: Confirm your order for {product.name}"
    body = f"""
    Hello {request.user.username},

    You have placed an order for: {product.name}.
    
    Current Status: PENDING
    
    Please click the link below to confirm this order:
    {confirmation_link}
    
    (If you did not make this request, simply ignore this email)
    """

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = request.user.email

    try:
        context = ssl._create_unverified_context()
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls(context=context) 
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
            
        messages.success(request, f"Verification email sent! Check your inbox to confirm.")

    except Exception as e:
        print(f"Email Error: {e}")
        messages.error(request, "Error sending email. Please try again later.")

    return redirect('my_orders')