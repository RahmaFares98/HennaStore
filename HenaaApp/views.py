from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .forms import ReviewForm
from django.db.utils import IntegrityError
from .models import *
from . import models
from django.contrib import messages
from django.http import JsonResponse

def home(request):
    user_id = request.session.get('user_id')  # Fetch the user_id from the session if it exists
    
    dresses = Dress.objects.all()
    modern_dresses = dresses[:6]  # First 6 dresses
    traditional_dresses = dresses[6:]  # Remaining dresses

    grouped_dresses = {
        'modern': [modern_dresses[i:i + 3] for i in range(0, len(modern_dresses), 3)],
        'traditional': [traditional_dresses[i:i + 3] for i in range(0, len(traditional_dresses), 3)]
    }

    context = {
        'grouped_dresses': grouped_dresses,
        'dresses': dresses,
        'user_id': user_id,
    }
    
    return render(request, 'store/home.html', context)
# def product_list(request):
#     dresses = Dress.objects.all()
#     return render(request, 'store/product_list.html', {'dresses': dresses})

def cart(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)  # Fetch the user object using the user_id
        order = Order.objects.filter(UserID=user, PaymentStatus='Pending').first()
        order_items = OrderItem.objects.filter(OrderID=order) if order else []
        return render(request, 'store/cart.html', {'order_items': order_items, 'order': order})
    
def checkout(request):
    if request.method == 'POST':
        order = Order.objects.filter(UserID=request.user, PaymentStatus='Pending').first()
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        if order:
            order.PaymentStatus = 'Paid'
            order.save()
            Payment.objects.create(OrderID=order, PaymentDate=timezone.now(), PaymentAmount=order.TotalAmount, PaymentMethod='Credit Card')
            return redirect('home')
        return render(request, 'store/checkout.html')

def user_profile(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        orders = Order.objects.filter(UserID=request.user)
    return render(request, 'store/user_profile.html', {'orders': orders})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Check for missing fields
        if not username or not password:
            messages.error(request, "Username and password are required")
            return redirect('/login')
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password")
            return redirect('/login')
        
        # Verify password
        if bcrypt.checkpw(password.encode(), user.password.encode()):
            request.session['user_id'] = user.id
            messages.success(request, "Successfully logged in")
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('/login')
    
    return render(request, 'registration/login.html')

def basic_login(postData):  # function for login validation
    errors = {}
    if not postData.get('username') or not postData.get('password'):
        errors['login'] = "Username and password are required"
    return errors

def user_logout(request):
    logout(request)
    request.session.flush()  # Clear the session
    return redirect('/')


def user_register(request):
    if request.method == 'POST':
        errors = User.objects.basic_register(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():   
                messages.error(request, value)    
            return redirect('/register')
        else:
            user = models.create_user(request.POST)
            request.session['user_id'] = user.id
            return redirect('/')
    return render(request, 'store/Register.html')

def add_to_cart(request, dress_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)  # Fetch the user object using the user_id
        dress = get_object_or_404(Dress, pk=dress_id)
        order, created = Order.objects.get_or_create(UserID=user, PaymentStatus='Pending', defaults={'TotalAmount': 0})
        order_item, created = OrderItem.objects.get_or_create(OrderID=order, DressID=dress, defaults={'Quantity': 1, 'Price': dress.Price})
        if not created:
            order_item.Quantity += 1
            order_item.save()
        order.TotalAmount += dress.Price
        order.save()
        return redirect('cart')
    
def payment(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)  # Fetch the user object using the user_id
        if request.method == 'POST':
            order = Order.objects.filter(UserID=user, PaymentStatus='Pending').first()
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

def product_detail(request, dress_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)  # Fetch the user object using the user_id
        dress = get_object_or_404(Dress, id=dress_id)
        reviews = Review.objects.filter(DressID=dress).order_by('-ReviewDate')  # Use the correct field name
        review_form = ReviewForm()

        context = {
            'dress': dress,
            'reviews': reviews,
            'form': review_form,
            'user_id': user_id,

        }
        return render(request, 'store/product_detail.html', context)

def add_review(request, dress_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)  # Fetch the user object using the user_id
        dress = get_object_or_404(Dress, id=dress_id)
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.DressID = dress
                review.UserID = user  # Use the user retrieved from the session
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