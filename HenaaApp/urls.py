from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:dress_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.user_profile, name='profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('add_to_cart/<int:dress_id>/', views.add_to_cart, name='add_to_cart'),
    path('payment/', views.payment, name='payment'), 
    path('about/', views.about, name='about'),  
]
