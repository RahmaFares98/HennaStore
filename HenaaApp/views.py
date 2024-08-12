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
# Initialize Stripe with your secret key
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


##user Action ##

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
            user = create_user(request.POST)

            # Automatically log the user in
            request.session['user_id'] = user.id

            return redirect('/')  # Redirect to the home page
                
    return render(request, 'store/Register.html')


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

##home##

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
    # Handle search functionality
    query = request.GET.get('q')  # Get the search term from the query string
    if query:
        results = Dress.objects.filter(Name__icontains=query)  # Filter the Dress model based on the search term
    else:
        results = []  # If no search term, return an empty list
    context = {
    'grouped_dresses': grouped_dresses,
    'dresses': dresses,
    'user_id': user_id,
    'query': query,
    'results': results,  # These are the filtered results based on the search query
    'users':users,
    'is_admin': is_admin,  # Pass the is_admin status to the template
    }
    return render(request, 'store/home.html', context)


def dress_list(request):
    query = request.GET.get('q')  # Get the search term from the query string
    
    if query:
        results = Dress.objects.filter(Name__icontains=query)  # Filter the Dress model based on the search term
    else:
        results = Dress.objects.all()  # Show all dresses if no search term
    
    # Prepare the context with search results and query
    context = {
        'results': results,
        'query': query,
    }
    
    return render(request, 'store/home.html', context)

def search_detail(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    return redirect(f'/products/{dress_id}/')

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

#About bage #
def about(request):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
    return render(request, 'store/about.html' ,{ 'user_id': user_id,})


#Product Detail Page #
def product_detail(request, dress_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)
        dress = get_object_or_404(Dress, id=dress_id)
        reviews = Review.objects.filter(DressID=dress).order_by('-ReviewDate')
        review_form = ReviewForm()
        selected_size = request.POST.get('Size', None)

        available_sizes = dress.Size.split(',') if dress.Size else []

        if not selected_size and available_sizes:
            selected_size = available_sizes[0]  # Default to the first available size

        context = {
            'dress': dress,
            'reviews': reviews,
            'form': review_form,
            'user_id': user_id,
            'selected_size': selected_size,
            'available_sizes': available_sizes,
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


###admin Pages##
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


def admin_orders_manage(request):
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

def admin_product_delete_view(request, product_id):
    if request.method == 'POST':
        try:
            dress = get_object_or_404(Dress, id=product_id)
            dress.delete()
            return JsonResponse({'success': True})  # Ensure this returns {'success': True}
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})  # Ensure the error is returned correctly
    return JsonResponse({'success': False, 'error': 'Invalid request method'})  # Check if it's not a POST request


def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/admin_orders.html', {'order': order})

def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect('admin_orders')  # Redirect to the list of orders after deletion
    return redirect('admin_order_detail', order_id=order_id)  # Redirect back to the order detail page if not POST


def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('admin_orders')

def admin_orders_view(request):
    orders = Order.objects.all()
    return render(request, 'admin/admin_orders.html', {'orders': orders})


##cart ###
def update_cart(request, item_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)

        # Get the order item and update the quantity
        order_item = get_object_or_404(OrderItem, pk=item_id, OrderID__UserID=user)
        new_quantity = int(request.POST.get('quantity', 1))

        # Update the total amount
        order = order_item.OrderID
        order.TotalAmount -= order_item.Price * order_item.Quantity  # Subtract the current amount
        order_item.Quantity = new_quantity
        order_item.save()
        order.TotalAmount += order_item.Price * new_quantity  # Add the new amount
        order.save()

        return redirect('cart',{'user_id':user_id})

def add_to_cart(request, dress_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)
        dress = get_object_or_404(Dress, pk=dress_id)
        
        # Debugging line
        print(request.POST)

        # Get the selected size from the POST request
        selected_size = request.POST.get('size')

        # Debugging line
        print(f"Selected size: {selected_size}")

        if not selected_size:
            # If no size is selected, redirect back to the dress detail page with an error message
            return redirect('product_detail', dress_id=dress_id)

        # Get or create the order with PaymentStatus 'Pending'
        order, created = Order.objects.get_or_create(
            UserID=user, 
            PaymentStatus='Pending', 
            defaults={'TotalAmount': 0, 'Processed_by': user}
        )

        # Get or create the order item with the selected size
        order_item, created = OrderItem.objects.get_or_create(
            OrderID=order, 
            DressID=dress, 
            size=selected_size,  # Add the selected size here
            defaults={'Quantity': 1, 'Price': dress.Price}
        )
        
        if not created:
            # If the item already exists in the order with the same size, increment the quantity
            order_item.Quantity += 1
            order_item.save()
        
        # Update the total amount in the order
        order.TotalAmount += dress.Price
        order.save()

        # Debugging: Print order details to ensure correct creation
        print(f"Order ID: {order.id}, Total Amount: {order.TotalAmount}, Items: {order.orderitem_set.count()}")

        return redirect('cart')

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

        # Add the range for quantity selection
        quantity_range = range(1, 11)

        # Pass the data to the template
        context = {
            'order_items': order_items,
            'order': order,
            'quantity_range': quantity_range,
            'user_id':user_id
        }

        return render(request, 'store/cart.html', context)

def remove_from_cart(request, item_id):
    if 'user_id' not in request.session:
        return redirect('/login')
    else:
        user_id = request.session['user_id']
        user = get_object_or_404(User, pk=user_id)

        # Get the order item and delete it
        order_item = get_object_or_404(OrderItem, pk=item_id, OrderID__UserID=user)
        order = order_item.OrderID
        order.TotalAmount -= order_item.Price * order_item.Quantity
        order.save()
        order_item.delete()

        return redirect('cart')


### Checkout ##
def checkout_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login')  # Redirect to login if user is not authenticated

    try:
        order = Order.objects.get(UserID_id=user_id, PaymentStatus='pending')  # Adjust this based on your model
    except Order.DoesNotExist:
        return redirect('cart_empty')  # Redirect to a page that shows the cart is empty

    # Create a Stripe Payment Intent
    intent = stripe.PaymentIntent.create(
        amount=int(order.TotalAmount * 100),  # amount in cents
        currency='usd',
        metadata={'order_id': order.id},
    )
    print(f"Stripe Secret Key: {settings.STRIPE_SECRET_KEY}")
    print(f"Stripe Publishable Key: {settings.STRIPE_PUBLISHABLE_KEY}")

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Process the payment with the cleaned data
            payment_status = process_payment(order, form.cleaned_data)
            if payment_status['status'] == 'success':
                order.PaymentStatus = 'completed'  # Mark order as completed
                order.save()
                return redirect('payment_success')  # Redirect to success page
            else:
                # If payment fails, re-render the checkout page with an error message
                return render(request, 'store/checkout.html', {
                    'order': order,
                    'order_items': order.orderitem_set.all(),  # Include order items
                    'form': form,
                    'error': payment_status['message'],
                    'stripe_publishable_key': stripe.api_key,
                    'client_secret': intent.client_secret,
                })
    else:
        form = PaymentForm()  # Initialize an empty payment form

    return render(request, 'store/checkout.html', {
        'order': order,
        'order_items': order.orderitem_set.all(),  # Include order items
        'form': form,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': intent.client_secret,
    })

def process_payment(request):
    if 'user_id' not in request.session:
        logger.debug("User not logged in. Redirecting to login.")
        return redirect('/login')
    
    user_id = request.session['user_id']
    # handle the redirect as you have done
    try:
        order = Order.objects.get(UserID=user_id, PaymentStatus='Pending')
        logger.debug(f"Order found: {order}")
    except Order.DoesNotExist:
    
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