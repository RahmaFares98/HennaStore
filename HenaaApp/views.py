from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect  # Ensure CSRF protection is in place
from django.shortcuts import render
from .forms import ReviewForm
from django.db.utils import IntegrityError
from .models import *
from django.views import View
from . import models
import stripe
from django.conf import settings
from .forms import *
from .payment_gateway import process_payment  # Custom payment gateway integration
from django.contrib import messages
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def home(request):
    user_id = request.session.get ('user_id')  # Fetch the user_id from the session if it exists
    users = User.objects.all()  # Fetch the user_id from the session if it exists
    dresses = Dress.objects.all()
    is_admin = request.session.get('is_admin',False)  # Fetch the is_admin status, default to False if not set

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
        'users':users,
        'is_admin': is_admin,  # Pass the is_admin status to the template

    }
    
    return render(request, 'store/home.html', context)



# Initialize Stripe with your secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_view(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    
    user_id = request.session['user_id']
    try:
        order = Order.objects.get(UserID_id=user_id, PaymentStatus='Pending')
    except Order.DoesNotExist:
        return redirect('cart_empty')
    
    if request.method == 'POST':
        # Handle form submission and payment processing here
        pass
    else:
        # Create a Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(order.TotalAmount * 100),  # Stripe expects the amount in cents
            currency='usd',
            metadata={'order_id': order.id}
        )

        return render(request, 'store/checkout.html', {
            'order': order,
            'order_items': order.orderitem_set.all(),
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'client_secret': intent.client_secret
        })

def checkout_view(request):
    # Check if 'user_id' is in the session
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login')

    # Fetch the user's current order using an appropriate field (e.g., PaymentStatus)
    try:
        order = Order.objects.get(UserID_id=user_id, PaymentStatus='pending')  # Adjust this based on your model
    except Order.DoesNotExist:
        return redirect('cart_empty')  # Redirect to a page that shows the cart is empty

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Process the payment with the cleaned data
            payment_status = process_payment(order, form.cleaned_data)
            if payment_status['status'] == 'success':
                order.PaymentStatus = 'completed'  # Mark order as completed
                order.save()
                return redirect('payment_success')
            else:
                return render(request, 'store/checkout.html', {'order': order, 'form': form, 'error': payment_status['message']})
    else:
        form = PaymentForm()

    return render(request, 'store/checkout.html', {'order': order, 'order_items': order.orderitem_set.all(), 'form': form})



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
            # Store user_id and is_admin in the session
            request.session['user_id'] = user.id
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
            request.session['is_admin'] = user.is_admin
            
            # Check if the user is an admin
            if user.is_admin:
                is_admin = True
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                return redirect('/')  # Redirect to home page for normal users
            
        else:
            messages.error(request, "Invalid username or password")
            return redirect('/login')
    
    return render(request, 'store/login.html')


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

def cart(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)

        # Initialize order and order_items
        order = None
        order_items = []

        # Fetch the current pending order
        try:
            order = Order.objects.get(UserID=user, PaymentStatus='Pending')
            order_items = order.orderitem_set.all()
        except Order.DoesNotExist:
            pass  # If no pending order, order_items remains empty and order is None

        return render(request, 'store/cart.html', {'order_items': order_items, 'order': order})

def add_to_cart(request, dress_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)
        dress = get_object_or_404(Dress, pk=dress_id)

        # Get or create the order with PaymentStatus 'Pending'
        order, created = Order.objects.get_or_create(
            UserID=user, 
            PaymentStatus='Pending', 
            defaults={'TotalAmount': 0, 'Processed_by': user}
        )

        # Get or create the order item
        order_item, created = OrderItem.objects.get_or_create(
            OrderID=order, 
            DressID=dress, 
            defaults={'Quantity': 1, 'Price': dress.Price}
        )
        
        if not created:
            # If the item already exists in the order, increment the quantity
            order_item.Quantity += 1
            order_item.save()
        
        # Update the total amount in the order
        order.TotalAmount += dress.Price
        order.save()

        # Debugging: Print order details to ensure correct creation
        print(f"Order ID: {order.id}, Total Amount: {order.TotalAmount}, Items: {order.orderitem_set.count()}")

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


def dress_list(request):
    query = request.GET.get('q')
    if query:
        results = Dress.objects.filter(Name__icontains=query)  # Adjust the filter as per your model fields
    else:
        results = Dress.objects.all()  # Show all dresses if no search term
    
    return render(request, 'home.html', {'results': results, 'query': query})
def product_detail(request, dress_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)
        dress = get_object_or_404(Dress, id=dress_id)
        reviews = Review.objects.filter(DressID=dress).order_by('-ReviewDate')
        review_form = ReviewForm()
        selected_size = request.POST.get('size', None)

        # Assuming `available_sizes` is a CharField with comma-separated sizes
        available_sizes = dress.Size.split(',')  # Example: "S,M,L" -> ['S', 'M', 'L']

        context = {
            'dress': dress,
            'reviews': reviews,
            'form': review_form,
            'user_id': user_id,
            'selected_size': selected_size,
            'available_sizes': available_sizes,  # Add available sizes to the context
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
# def admin_product_delete_view(request, product_id):
#     product = get_object_or_404(Dress, id=product_id)
#     product.delete()
    
#     messages.success(request, 'Product deleted successfully!')
#     return redirect('admin_products')
def admin_product_delete_view(request, product_id):
    if request.method == 'POST':
        try:
            dress = get_object_or_404(Dress, id=product_id)
            dress.delete()
            return JsonResponse({'success': True})  # Ensure this returns {'success': True}
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})  # Ensure the error is returned correctly
    return JsonResponse({'success': False, 'error': 'Invalid request method'})  # Check if it's not a POST request

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

def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_orders.html', {'order': order})

def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect('admin_orders')  # Redirect to the list of orders after deletion
    return redirect('admin_order_detail', order_id=order_id)  # Redirect back to the order detail page if not POST



def process_payment(request):
    if 'user_id' not in request.session:
        logger.debug("User not logged in. Redirecting to login.")
        return redirect('/login')
    
    user_id = request.session['user_id']
    try:
        order = Order.objects.get(UserID=user_id, PaymentStatus='Pending')
    except Order.DoesNotExist:
        logger.debug("No pending order found. Redirecting to cart.")
        messages.error(request, "No pending order found.")
        return redirect('cart')  # Redirect to cart if no pending order

    if request.method == 'POST':
        payment_data = request.POST
        payment_successful = True  # Replace with actual payment gateway logic
        
        if payment_successful:
            logger.debug("Payment successful. Updating order status.")
            order.PaymentStatus = 'Paid'
            order.save()

            messages.success(request, "Payment successful!")
            return redirect('payment_success')  # Assuming you have a success page
        else:
            logger.debug("Payment failed. Redirecting to checkout.")
            messages.error(request, "Payment failed. Please try again.")
            return redirect('checkout')  # Redirect back to checkout on failure

    return render(request, 'store/checkout.html', {'order': order})



def payment_success(request):
    return render(request, 'store/payment_success.html')