from django.db import models
from django.utils import timezone
from decimal import Decimal



class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=20)
    user_referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Referral(models.Model):
    referrer = models.ForeignKey(User, related_name='referrals_made', on_delete=models.CASCADE)
    referee = models.ForeignKey(User, related_name='referrals_received', on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=20)
    isActive = models.BooleanField(default=False)  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MonthlyPurchase(models.Model):
    user = models.ForeignKey(User, related_name='monthly_purchase', on_delete=models.CASCADE)
    user_purchase = models.PositiveIntegerField(default=0)
    referral_purchase = models.PositiveIntegerField(default=0)
    group_purchase = models.PositiveIntegerField(default=0)  # Sum of user and referral purchases
    cumulative_purchase = models.PositiveIntegerField(default=0)  # Track the cumulative purchase
    cumulative_points = models.PositiveIntegerField(default=0)  # Points calculated as cumulative purchase / 1.5
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Store current commission percentage
    month = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_group_purchase(self):
        # Update the group purchase as user_purchase + referral_purchase
        self.group_purchase = self.user_purchase + self.referral_purchase
        self.save()

    # def update_cumulative_purchase_and_commission(self):
    #     # Set minimum thresholds for each commission percentage
    #     thresholds = {
    #         Decimal('12.00'): {'user_min': 100, 'referral_min': 24300},
    #         Decimal('9.00'): {'user_min': 100, 'referral_min': 8100},
    #         Decimal('6.00'): {'user_min': 100, 'referral_min': 900},
    #         Decimal('3.00'): {'user_min': 100, 'referral_min': 300},
    #     }

    #     # Determine the new commission percentage based on user and referral purchases
    #     previous_commission_percentage = self.commission_percentage
    #     commission_percentage = Decimal('0.00')

    #     # Check for each threshold starting from the highest percentage
    #     for percentage, values in sorted(thresholds.items(), reverse=True):
    #         if self.user_purchase >= values['user_min'] and self.referral_purchase >= values['referral_min']:
    #             commission_percentage = percentage
    #             break

    #     # Update cumulative purchase and points based on commission percentage
    #     if commission_percentage > previous_commission_percentage:
    #         # If commission level increased, add current group purchase to the previous cumulative purchase
    #         self.cumulative_purchase += self.group_purchase
    #     elif commission_percentage == Decimal('3.00'):
    #         # If at the base level (3%), cumulative is simply the group purchase
    #         self.cumulative_purchase = self.group_purchase

    #     # Update cumulative points
    #     self.cumulative_points = self.cumulative_purchase / Decimal('1.5')

    #     # Store the updated commission percentage
    #     self.commission_percentage = commission_percentage
    #     self.save()

    def update_cumulative_purchase_and_commission(self):
        # Set minimum thresholds for each commission percentage
        thresholds = {
            Decimal('12.00'): {'user_min': 100, 'referral_min': 24300},
            Decimal('9.00'): {'user_min': 100, 'referral_min': 8100},
            Decimal('6.00'): {'user_min': 100, 'referral_min': 900},
            Decimal('3.00'): {'user_min': 100, 'referral_min': 300},
        }

        # Determine the new commission percentage based on user and referral purchases
        previous_commission_percentage = self.commission_percentage
        commission_percentage = Decimal('0.00')

        # Check for each threshold starting from the highest percentage
        for percentage, values in sorted(thresholds.items(), reverse=True):
            if self.user_purchase >= values['user_min'] and self.referral_purchase >= values['referral_min']:
                commission_percentage = percentage
                break

        # Update cumulative purchase and points based on commission percentage
        if commission_percentage > previous_commission_percentage:
            # If commission percentage increased, set group purchase to cumulative purchase
            self.group_purchase = self.cumulative_purchase

        # Always set cumulative purchase to group purchase for each commission level
        self.cumulative_purchase = self.group_purchase

        # Update cumulative points
        self.cumulative_points = self.cumulative_purchase // Decimal('1.5')

        # Store the updated commission percentage
        self.commission_percentage = commission_percentage
        self.save()

    

class CommissionHistory(models.Model):
    user = models.ForeignKey(User, related_name='commission_history', on_delete=models.CASCADE)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    cumulative_purchase = models.PositiveIntegerField(default=0)  # Store the cumulative purchase when commission triggered
    cumulative_points = models.PositiveIntegerField(default=0)
    earned_at = models.DateTimeField(auto_now_add=True)
    month = models.DateField(default=timezone.now)
    commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)

      # New fields
    user_total_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # User's total purchase at the time of transaction
    referral_total_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Referral's total purchase at the time of transaction
    order_total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total amount of the order

    def __str__(self):
        return f"{self.user.email} - {self.commission_percentage}% Commission Earned"


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=1024, blank=True, null=True)  # Added image_url field


    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    items_in_stock = models.PositiveIntegerField(default=1)
    #sku = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=1024, blank=True, null=True)  # Added image_url field
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)  # Added SubCategory ForeignKey
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    #tags = models.ManyToManyField('Tag', blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=255, blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

      # Address fields
    address_line_1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='order_details', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_details', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Statements(models.Model):
    user = models.ForeignKey(User, related_name='statements', on_delete=models.CASCADE)
    user_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Tracks the user's purchases
    referral_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Tracks the referral's purchases
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Stores the commission percentage
    commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Stores the earned commission

    created_at = models.DateTimeField(auto_now_add=True)  # Record creation time
    updated_at = models.DateTimeField(auto_now=True)  # Record updated time

    def __str__(self):
        return f"Statement for {self.user.email}"

   

class OrderTracking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed Delivery'),
    ]

    order = models.OneToOneField(Order, related_name='tracking', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    last_update = models.DateTimeField(auto_now=True)



class UserPoint(models.Model):
    user = models.OneToOneField(User, related_name='user_points', on_delete=models.CASCADE)
    points = models.PositiveIntegerField()
    referral_points = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Ewallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ewallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_commission(self, commission_amount):
        self.balance += commission_amount
        self.save()

    def __str__(self):
        return f"{self.user.username}'s eWallet - Balance: {self.balance}"

class Transactions(models.Model):
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"
    
class Payout_Transaction(models.Model):
    user = models.ForeignKey(User, related_name='payout_transactions', on_delete=models.CASCADE)
    points_redeemed = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)