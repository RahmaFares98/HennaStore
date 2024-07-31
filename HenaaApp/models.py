from django.db import models
from django.contrib.auth.models import User

class Dress(models.Model):
    Name = models.CharField(max_length=255)
    Description = models.TextField()
    Size = models.CharField(max_length=10)
    Color = models.CharField(max_length=50)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    StockQuantity = models.IntegerField()
    Category = models.CharField(max_length=100)
    ImageURL = models.URLField(max_length=255)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)
    Created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.Name

class Order(models.Model):
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    OrderDate = models.DateTimeField(auto_now_add=True)
    TotalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    PaymentStatus = models.CharField(max_length=45)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)
    Processed_by = models.IntegerField()

    def __str__(self):
        return f"Order {self.id} by {self.UserID}"

class OrderItem(models.Model):
    OrderID = models.ForeignKey(Order, on_delete=models.CASCADE)
    DressID = models.ForeignKey(Dress, on_delete=models.CASCADE)
    Quantity = models.IntegerField()
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.OrderID}"

class Payment(models.Model):
    OrderID = models.ForeignKey(Order, on_delete=models.CASCADE)
    PaymentDate = models.DateTimeField()
    PaymentAmount = models.DecimalField(max_digits=10, decimal_places=2)
    PaymentMethod = models.CharField(max_length=45)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.OrderID}"

class Review(models.Model):
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    DressID = models.ForeignKey(Dress, on_delete=models.CASCADE)
    Rating = models.IntegerField()
    Comment = models.TextField()
    ReviewDate = models.DateTimeField(auto_now_add=True)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review {self.id} by {self.UserID}"

