from django.db import models
import re
import bcrypt
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


class UserManager(models.Manager):
    def basic_register(self, postData): # function for registration 
        errors = {}
        if len(postData['username']) < 2:# validated first name
            errors["username"] = "username should be at least 2 characters"## as list ""if satament
        #validated format of mail and unique email used
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):             
            errors['email'] = "Invalid email address!"
        if User.objects.filter(email=postData['email']).exists():
            errors['email_used'] = "Email already in use!"
        # validated pass to be greater than 8 char and match with confirm pass 
        if len(postData['password']) < 8:
            errors["password"] = "Password should be at least 8 characters"
        if postData['password'] != postData['confirm_pw']:
            errors["confirm_pw"] = "Passwords are not match "
        return errors
    
    def basic_login(self, postData):# function for login 
            errors = {}
            try:
                user = User.objects.get(email=postData['username'])
            except ObjectDoesNotExist:
                errors['username'] = "username not found."
                return errors
            if not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
                errors['password'] = "Invalid password."
            return errors


class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=225)
    password = models.CharField(max_length=150)
    confirm_pw=models.CharField(max_length=150)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

def create_user(POST):
    password = POST['password']
    return User.objects.create(
        username=POST['username'],
        email=POST['email'],
        password= bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        # confirm_pw=POST['password']
        )
def get_user(session):
    return User.objects.get(id=session['user_id'])


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


