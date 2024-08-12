from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('', views.home, name='home'),
    path('dress/<int:dress_id>/detail/', views.search_detail, name='search_detail'),
    path('products/<int:dress_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:dress_id>/', views.add_to_cart, name='add_to_cart'),
    path('profile/', views.user_profile, name='profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/', update_cart, name='update_cart'),
    path('payment/', views.payment, name='payment'), 
    path('about/', views.about, name='about'),  
    path('dress/<int:dress_id>/add_review/', views.add_review, name='add_review'),
    path('admin_dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('admin_users/', admin_users, name='admin_users'),
    path('admin_orders/', admin_orders_manage, name='admin_orders'),
    path('admin_orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin_orders/delete/<int:order_id>/', views.admin_order_delete, name='admin_order_delete'),
    path('admin_dashboard/edit/<int:user_id>/', admin_user_edit_view, name='admin_user_edit'),
    path('admin_dashboard/users/delete/<int:user_id>/', admin_delete_user_view, name='admin_user_delete'),
    path('admin_products/', admin_product_list_view, name='admin_products'),
    path('admin_dashboard/admin_products', admin_product_add_view, name='admin_product_add'),
    path('admin_dashboard/admin_products/edit/<int:product_id>/', admin_product_edit_view, name='admin_product_edit'),
    path('admin_dashboard/admin_products/delete/<int:product_id>/', admin_product_delete_view, name='admin_product_delete'),
    path('search/', dress_list, name='search_dress'),
    path('checkout/', checkout_view, name='checkout'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('admin_orders/', views.admin_orders_view, name='admin_orders'),
    path('admin_orders/delete/<int:order_id>/', views.admin_order_delete, name='admin_order_delete'),


]
