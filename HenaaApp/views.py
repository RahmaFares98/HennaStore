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
from django.views import View
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
            
            # Check if the user is an admin
            if user.is_admin:
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                return redirect('/')  # Redirect to home page for normal users
            
        else:
            messages.error(request, "Invalid username or password")
            return redirect('/login')
    
    return render(request, 'store/login.html')

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
            # Create the user as a normal user (non-admin)
            user = models.create_user(
                request.POST
            )

            # Automatically log the user in
            request.session['user_id'] = user.id

            return redirect('/')  # Redirect to the home page
                
    return render(request, 'store/Register.html')

def admin_create_user(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return HttpResponse("You do not have permission to access this page.")

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_admin = request.POST.get('is_admin', False)

        # Create the new user, with admin rights if specified
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_admin=is_admin
        )

        messages.success(request, 'User created successfully!')
        return redirect('admin_dashboard')

    return render(request, 'admin/admin_create_user.html')

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

# def admin_dashboard_view(request):
#     # Check if the user is authenticated
#     if not request.user.is_authenticated:
#         return redirect('login')  # Redirect to the login page if not authenticated
    
#     # Check if the user is an admin (superuser or part of the 'Admin' group)
#     if not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists():
#         return HttpResponse("You are not authorized to view this page.")  # Show a forbidden error
    
#     # Gather data to display on the dashboard
#     context = {
#         'total_users': User.objects.count(),
#         'total_orders': Order.objects.count(),
#         # Add more context variables as needed
#     }
#     return render(request, 'admin/admin_dashboard.html', context)

def admin_dashboard_view(request):
    users = User.objects.all()
    orders = Order.objects.all()
    dresses = Dress.objects.all()

    context = {
        'users': users,
        'orders': orders,
        'dresses': dresses,
    }
    return render(request, 'admin/admin_dashboard.html', context)


def admin_users(request):
        users = User.objects.all()
        context = {'users': users}
        return render(request, 'admin/admin_user.html', context)


def admin_user_edit_view(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_admin = request.POST.get('is_admin')
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('admin_users')  # Redirect to the list of users
    else :
        return render(request, 'admin/admin_user.html')
    
def admin_delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()
        return redirect('admin_users')
    
    elif request.method == 'GET':
        user.delete()
        return redirect('admin_users')



class AdminOrdersView(View):
    def get(self, request):
        orders = Order.objects.all()
        return render(request, 'admin/admin_orders.html', {'orders': orders})
# Product sections: List all products
def admin_product_list_view(request):
    products = Dress.objects.all()
    return render(request, 'admin/admin_products.html', {'products': products})

# Add Product
def admin_product_add_view(request):
    # Check if the user is authenticated and is an admin
    if 'user_id' not in request.session:
        messages.error(request, "You need to log in to access this page.")
        return redirect('login')  # Redirect to login page if the user is not logged in
    
    user = User.objects.get(id=request.session['user_id'])
    if not user.is_admin:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')  # Redirect to home or any other appropriate page

    if request.method == 'POST':
        # Fetch data from the form
        name = request.POST['Name']
        description = request.POST['Description']
        size = request.POST['Size']
        color = request.POST['Color']
        price = request.POST['Price']
        stock_quantity = request.POST['StockQuantity']
        category = request.POST['Category']
        image_url = request.POST['ImageURL']

        # Create a new product entry
        Dress.objects.create(
            Name=name,
            Description=description,
            Size=size,
            Color=color,
            Price=price,
            StockQuantity=stock_quantity,
            Category=category,
            ImageURL=image_url,
            Created_by=user  # Assuming the logged-in user is the creator
        )
        messages.success(request, 'Product added successfully!')
        return redirect('admin_products')  # Redirect to the product list page
    
    return render(request, 'admin/admin_products.html')


# Edit Product
def admin_product_edit_view(request, product_id):
    product = get_object_or_404(Dress, id=product_id)

    if request.method == 'POST':
        product.Name = request.POST['Name']
        product.Description = request.POST['Description']
        product.Size = request.POST['Size']
        product.Color = request.POST['Color']
        product.Price = request.POST['Price']
        product.StockQuantity = request.POST['StockQuantity']
        product.Category = request.POST['Category']
        product.ImageURL = request.POST['ImageURL']

        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_products')

    return render(request, 'admin/admin_products.html', {'product': product})

# Delete Product
def admin_product_delete_view(request, product_id):
    product = get_object_or_404(Dress, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('admin_products')
    
def user_profile(request):
    # Check if the user is logged in by verifying the session
    if 'user_id' not in request.session:
        return redirect('/login')  # Redirect to login page if not authenticated

    # Assuming 'user_id' in session is the ID of the logged-in user
    user_id = request.session['user_id']
    
    # Fetch the user's orders using the correct field name
    orders = Order.objects.filter(UserID=user_id)  # Use 'UserID' as it matches your model
    
    # Fetch the user object using the correct method
    user = User.objects.get(id=user_id)
    
    # Prepare context for the template
    context = {
        'orders': orders,
        'user': user
    }
    
    return render(request, 'store/user_profile.html', context)
