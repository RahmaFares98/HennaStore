from django.shortcuts import render, redirect, get_object_or_404
from .models import Dress, Order, OrderItem, Payment, Review
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone

def home(request):
    dresses = list(Dress.objects.all())
    grouped_dresses = [dresses[i:i + 3] for i in range(0, len(dresses), 3)]
    context = {
        'grouped_dresses': grouped_dresses,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    dresses = Dress.objects.all()
    return render(request, 'store/product_list.html', {'dresses': dresses})

def product_detail(request, dress_id):
    dress = get_object_or_404(Dress, pk=dress_id)
    return render(request, 'store/product_detail.html', {'dress': dress})

@login_required
def cart(request):
    order = Order.objects.filter(UserID=request.user, PaymentStatus='Pending').first()
    order_items = OrderItem.objects.filter(OrderID=order) if order else []
    return render(request, 'store/cart.html', {'order_items': order_items, 'order': order})

@login_required
def checkout(request):
    if request.method == 'POST':
        order = Order.objects.filter(UserID=request.user, PaymentStatus='Pending').first()
        if order:
            order.PaymentStatus = 'Paid'
            order.save()
            Payment.objects.create(OrderID=order, PaymentDate=timezone.now(), PaymentAmount=order.TotalAmount, PaymentMethod='Credit Card')
        return redirect('home')
    return render(request, 'store/checkout.html')

@login_required
def user_profile(request):
    orders = Order.objects.filter(UserID=request.user)
    return render(request, 'store/user_profile.html', {'orders': orders})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Invalid credentials")
    return render(request, 'store/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user = User.objects.create_user(username, email, password)
        user.save()
        return redirect('home')
    return render(request, 'store/register.html')

@login_required
def add_to_cart(request, dress_id):
    dress = get_object_or_404(Dress, pk=dress_id)
    order, created = Order.objects.get_or_create(UserID=request.user, PaymentStatus='Pending', defaults={'TotalAmount': 0})
    order_item, created = OrderItem.objects.get_or_create(OrderID=order, DressID=dress, defaults={'Quantity': 1, 'Price': dress.Price})
    if not created:
        order_item.Quantity += 1
        order_item.save()
    order.TotalAmount += dress.Price
    order.save()
    return redirect('cart')

@login_required
def payment(request):
    if request.method == 'POST':
        order = Order.objects.filter(UserID=request.user, PaymentStatus='Pending').first()
        if order:
            payment_method = request.POST.get('payment_method')
            payment_amount = order.TotalAmount
            payment_date = timezone.now()
            payment = Payment.objects.create(
                OrderID=order,
                PaymentDate=payment_date,
                PaymentAmount=payment_amount,
                PaymentMethod=payment_method
            )
            order.PaymentStatus = 'Paid'
            order.save()
            return redirect('home')
    return render(request, 'store/payment.html')

@login_required
def checkout(request):
    if request.method == 'POST':
        order = Order.objects.filter(UserID=request.user, PaymentStatus='Pending').first()
        if order:
            return redirect('payment')
    return render(request, 'store/checkout.html')

def about(request):
    return render(request, 'store/about.html')