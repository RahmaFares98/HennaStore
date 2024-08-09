from django.contrib import admin
from .models import *
from django.contrib.admin import SimpleListFilter

# Custom action to mark orders as shipped
@admin.action(description='Mark selected orders as shipped')
def make_shipped(modeladmin, request, queryset):
    queryset.update(PaymentStatus='shipped')

# Custom filter for payment status
class PaymentStatusFilter(SimpleListFilter):
    title = 'payment status'
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('failed', 'Failed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'paid':
            return queryset.filter(PaymentStatus='paid')
        if self.value() == 'pending':
            return queryset.filter(PaymentStatus='pending')
        if self.value() == 'failed':
            return queryset.filter(PaymentStatus='failed')

# Registering the User model with custom admin options
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)

# Registering the Dress model with custom admin options
@admin.register(Dress)
class DressAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Category', 'Price', 'StockQuantity', 'Created_at')
    search_fields = ('Name', 'Category')
    list_filter = ('Category',)
    ordering = ('-Created_at',)

# Registering the Order model with custom admin options, including custom filters and actions
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'UserID', 'OrderDate', 'TotalAmount', 'PaymentStatus')
    search_fields = ('UserID__username', 'PaymentStatus')
    list_filter = (PaymentStatusFilter,)
    ordering = ('-OrderDate',)
    actions = [make_shipped]

# Registering the OrderItem model with custom admin options
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('OrderID', 'DressID', 'Quantity', 'Price')
    search_fields = ('OrderID__id', 'DressID__Name')
    ordering = ('OrderID',)

# Registering the Payment model with custom admin options
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('OrderID', 'PaymentDate', 'PaymentAmount', 'PaymentMethod')
    search_fields = ('OrderID__id', 'PaymentMethod')
    list_filter = ('PaymentMethod',)
    ordering = ('-PaymentDate',)

# Registering the Review model with custom admin options
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('UserID', 'DressID', 'Rating', 'ReviewDate')
    search_fields = ('UserID__username', 'DressID__Name')
    list_filter = ('Rating',)
    ordering = ('-ReviewDate',)



# Customizing the admin site's appearance
admin.site.site_header = "Henna Store Admin"
admin.site.site_title = "Henna Store Admin Portal"
admin.site.index_title = "Welcome to Henna Store Administration"
