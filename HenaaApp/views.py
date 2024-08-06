from django.shortcuts import render, redirect, get_object_or_404
from .models import Dress, Order, OrderItem, Payment, Review
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .models import * # Replace with your actual model
from .forms import ReviewForm
from django.db.utils import IntegrityError

def home(request):
    dresses = list(Dress.objects.all())
    modern_dresses = dresses[:6]  # First 6 dresses
    traditional_dresses = dresses[6:]  # Remaining dresses
    
    grouped_dresses = {
        'modern': [modern_dresses[i:i + 3] for i in range(0, len(modern_dresses), 3)],
        'traditional': [traditional_dresses[i:i + 3] for i in range(0, len(traditional_dresses), 3)]
    }

    context = {
        'grouped_dresses': grouped_dresses,
        'dresses':Dress.objects.all(),

    }
    return render(request, 'store/home.html', context)

# def product_list(request):
#     dresses = Dress.objects.all()
#     return render(request, 'store/product_list.html', {'dresses': dresses})

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


def search_view(request):
    query = request.GET.get('q', '')
    # Perform your search logic here, e.g., search in the database
    results = [
        {"name": "Yafa Thobe", "Color": "White and Red"},
        {"name": "Bissan Thobe", "Color": "white and Blue"},
    ]
    return JsonResponse({"results": results})

from .forms import ReviewForm

def product_detail(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    reviews = Review.objects.filter(dress=dress).order_by('-created_at')
    review_form = ReviewForm()

    context = {
        'dress': dress,
        'reviews': reviews,
        'form': review_form
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def add_review(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.dress = dress
            review.user = request.user
            review.save()
            return redirect('product_detail', dress_id=dress.id)
    return redirect('product_detail', dress_id=dress.id)


def product_detail(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    reviews = Review.objects.filter(DressID=dress).order_by('-ReviewDate')
    review_form = ReviewForm()

    context = {
        'dress': dress,
        'reviews': reviews,
        'form': review_form
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def add_review(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.DressID = dress
            review.UserID = request.user
            try:
                review.save()
            except IntegrityError:
                # Handle the error as needed
                reviews = Review.objects.filter(DressID=dress).order_by('-ReviewDate')
                return render(request, 'store/product_detail.html', {
                    'dress': dress,
                    'form': form,
                    'reviews': reviews,
                    'error': 'There was a problem with your review submission. Please try again.'
                })
            return redirect('product_detail', dress_id=dress.id)
    return redirect('product_detail', dress_id=dress.id)