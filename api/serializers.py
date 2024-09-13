from rest_framework import serializers
from .models import User, Referral, Product, Order, OrderDetail, UserPoint, Ewallet, Transactions, Payout_Transaction, OrderTracking, Category, MonthlyPurchase, Statements, SubCategory, CommissionHistory
import uuid
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        # Create the User instance
        user = User.objects.create(**validated_data)
        # Automatically create a UserPoint instance associated with the User
        UserPoint.objects.create(user=user, points=100, status='Executive')
        Ewallet.objects.create(user=user, balance=0.00)
        return user       


class ReferralSerializer(serializers.ModelSerializer):
    referee_name = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = '__all__'
    
    def get_referee_name(self, obj):
        referee = User.objects.get(id=obj.referee.id)
        return f"{referee.first_name} {referee.last_name}"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class MonthlyPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyPurchase
        fields = '__all__'

class StatementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statements
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class ComissionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionHistory
        fields = '__all__'    

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderDetail
        fields = ['product_name','product', 'quantity', 'price']  # Exclude 'order' here

class OrderTrackingSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(source='order.order_details', many=True, read_only=True)

    class Meta:
        model = OrderTracking
        fields = ['status', 'tracking_number', 'shipped_at', 'estimated_delivery', 'delivery_address', 'last_update','order_details']

# class OrderSerializer(serializers.ModelSerializer):
#     order_details = OrderDetailSerializer(many=True)
#     tracking = OrderTrackingSerializer(read_only=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'created_at', 'user', 'total_amount', 'order_details', 'tracking', 'address_line_1', 'city', 'state', 'postal_code', 'country']

#     def create(self, validated_data):
#         order_details_data = validated_data.pop('order_details')
#         order = Order.objects.create(**validated_data)

#         # Update user points
#         user_points = UserPoint.objects.get(user=order.user)
#         user_points.points += order.total_amount
#         user_points.save()

#         referral = Referral.objects.get(referee=order.user)
#         referral.isActive = True
#         referral.updated_at = timezone.now()
#         referral.save()

#         # Check if the user has a referrer
#         referral = Referral.objects.filter(referee=order.user).first()
#         if referral:
#             referrer_points = UserPoint.objects.get(user=referral.referrer)
#             referrer_points.referral_points += order.total_amount  # 100% of order amount
#             referrer_points.save()
#             # Update status based on referral points
#             self.update_status(referrer_points)

#         # Save order details and reduce items_in_stock
#         for detail_data in order_details_data:
#             order_detail = OrderDetail.objects.create(order=order, **detail_data)

#             # Reduce items_in_stock in the Product table
#             product = order_detail.product
#             product.items_in_stock -= order_detail.quantity
#             if product.items_in_stock < 0:
#                 raise serializers.ValidationError(f"Product {product.name} is out of stock.")
#             product.save()
        
#         # Create OrderTracking entry
#         tracking_data = {
#             'order': order,
#             'tracking_number': self.generate_tracking_number(),
#             'delivery_address': 'abc street 123',
#             'estimated_delivery': self.calculate_expected_delivery()
#         }
#         OrderTracking.objects.create(**tracking_data)

#         return order

# class OrderSerializer(serializers.ModelSerializer):
#     order_details = OrderDetailSerializer(many=True)
#     tracking = OrderTrackingSerializer(read_only=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'created_at', 'user', 'total_amount', 'order_details', 'tracking', 'address_line_1', 'city', 'state', 'postal_code', 'country']

#     def create(self, validated_data):
#         order_details_data = validated_data.pop('order_details')
#         order = Order.objects.create(**validated_data)

#         # Update user points
#         user_points = UserPoint.objects.get(user=order.user)
#         user_points.points += order.total_amount
#         user_points.save()

#         # Get or create MonthlyPurchase entry for the user
#         monthly_purchase, created = MonthlyPurchase.objects.get_or_create(user=order.user)
#         monthly_purchase.user_purchase += order.total_amount
#         monthly_purchase.save()

#         # Check if the user has a referrer
#         referral = Referral.objects.filter(referee=order.user).first()
#         if referral:
#             # Update referrer's monthly purchases
#             referrer_monthly_purchase, created = MonthlyPurchase.objects.get_or_create(user=referral.referrer)
#             referrer_monthly_purchase.referral_purchase += order.total_amount
#             referrer_monthly_purchase.save()

#             # Apply commission logic
#             self.apply_commission(referral.referrer, referrer_monthly_purchase)

#             # Add values to Statements for the referrer
#             self.create_statements(order.user,referral.referrer, monthly_purchase, referrer_monthly_purchase)

#         # Save order details and reduce items_in_stock
#         for detail_data in order_details_data:
#             order_detail = OrderDetail.objects.create(order=order, **detail_data)

#             product = order_detail.product
#             product.items_in_stock -= order_detail.quantity
#             if product.items_in_stock < 0:
#                 raise serializers.ValidationError(f"Product {product.name} is out of stock.")
#             product.save()

#         # Create OrderTracking entry
#         tracking_data = {
#             'order': order,
#             'tracking_number': self.generate_tracking_number(),
#             'delivery_address': 'abc street 123',
#             'estimated_delivery': self.calculate_expected_delivery()
#         }
#         OrderTracking.objects.create(**tracking_data)

#         return order

#     def apply_commission(self, referrer, referrer_monthly_purchase):
#         user_purchase = referrer_monthly_purchase.user_purchase
#         referral_purchase = referrer_monthly_purchase.referral_purchase

#         if referral_purchase >= 300:
#             # 3% commission for referral purchases >= 300
#             commission = round(referral_purchase * Decimal('0.03'))
#             referrer_points = UserPoint.objects.get(user=referrer)
#             referrer_points.referral_points += commission
#             referrer_points.save()

#         if user_purchase >= 300 and referral_purchase >= 900:
#             # 6% commission for user purchases >= 300 and referral purchases >= 900
#             commission = round(referral_purchase * Decimal('0.06'))
#             referrer_points = UserPoint.objects.get(user=referrer)
#             referrer_points.referral_points += commission
#             referrer_points.save()

#         if user_purchase >= 100 and referral_purchase >= 8100:
#             # 9% commission for user purchases >= 100 and referral purchases >= 8100
#             commission = round(referral_purchase * Decimal('0.09'))
#             referrer_points = UserPoint.objects.get(user=referrer)
#             referrer_points.referral_points += commission
#             referrer_points.save()

#     def create_statements(self, user, referrer, monthly_purchase, referrer_monthly_purchase):
        
#         Statements.objects.create(
#             user=user,
#             user_purchase=monthly_purchase.user_purchase,
#             referral_purchase=monthly_purchase.referral_purchase,
#             commission_percentage=self.get_commission_percentage(monthly_purchase),
#             commission_earned=self.get_commission_amount(monthly_purchase)
#         )

#         Statements.objects.create(
#             user=referrer,
#             user_purchase=referrer_monthly_purchase.user_purchase,
#             referral_purchase=referrer_monthly_purchase.referral_purchase,
#             commission_percentage=self.get_commission_percentage(referrer_monthly_purchase),
#             commission_earned=self.get_commission_amount(referrer_monthly_purchase)
#         )

#     def get_commission_percentage(self, referrer_monthly_purchase):
#         # Determine the commission percentage based on the rules
#         if referrer_monthly_purchase.referral_purchase >= 8100:
#             return Decimal('9.00')
#         elif referrer_monthly_purchase.user_purchase >= 300 and referrer_monthly_purchase.referral_purchase >= 900:
#             return Decimal('6.00')
#         elif referrer_monthly_purchase.referral_purchase >= 300:
#             return Decimal('3.00')
#         return Decimal('0.00')

#     def get_commission_amount(self, referrer_monthly_purchase):
#         commission_percentage = self.get_commission_percentage(referrer_monthly_purchase)
#         return round(referrer_monthly_purchase.referral_purchase * (commission_percentage / 100))

#     def generate_tracking_number(self):
#         return str(uuid.uuid4())

#     def calculate_expected_delivery(self):
#         return timezone.now() + timedelta(days=7)

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'user', 'total_amount', 'order_details', 'address_line_1', 'city', 'state', 'postal_code', 'country']

    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)

        # Update user points
        user_points = UserPoint.objects.get(user=order.user)
        user_points.points += order.total_amount
        user_points.save()

        # Get or create MonthlyPurchase entry for the user
        monthly_purchase, created = MonthlyPurchase.objects.get_or_create(user=order.user)
        monthly_purchase.user_purchase += order.total_amount
        monthly_purchase.calculate_group_purchase()

        # Apply the updated cumulative purchase and commission logic
        monthly_purchase.update_cumulative_purchase_and_commission()

        # Check if the user has a referrer
        referral = Referral.objects.filter(referee=order.user).first()
        if referral:
            # Update referrer's monthly purchases
            referrer_monthly_purchase, created = MonthlyPurchase.objects.get_or_create(user=referral.referrer)
            referrer_monthly_purchase.referral_purchase += order.total_amount
            referrer_monthly_purchase.calculate_group_purchase()
            referrer_monthly_purchase.update_cumulative_purchase_and_commission()

            # Apply commission for both user and referrer
            self.apply_commission(order, order.user, referral.referrer, monthly_purchase, referrer_monthly_purchase)
        else:
            # If no referrer, create CommissionHistory for the user alone
            CommissionHistory.objects.create(
                user=order.user,
                commission_percentage=monthly_purchase.commission_percentage,
                cumulative_purchase=monthly_purchase.cumulative_purchase,
                cumulative_points=monthly_purchase.cumulative_points,
                commission_earned=0,
                user_total_purchase=monthly_purchase.user_purchase,
                referral_total_purchase=monthly_purchase.referral_purchase,
                order_total_amount=order.total_amount
            )

        # Save order details
        for detail_data in order_details_data:
            order_detail = OrderDetail.objects.create(order=order, **detail_data)

            product = order_detail.product
            product.items_in_stock -= order_detail.quantity
            if product.items_in_stock < 0:
                raise serializers.ValidationError(f"Product {product.name} is out of stock.")
            product.save()

        # Create OrderTracking entry
        tracking_data = {
            'order': order,
            'tracking_number': self.generate_tracking_number(),
            'delivery_address': 'abc street 123',
            'estimated_delivery': self.calculate_expected_delivery()
        }
        OrderTracking.objects.create(**tracking_data)

        return order

    def apply_commission(self, order, user, referrer, monthly_purchase, referrer_monthly_purchase):
        """
        Applies commission for both the user and the referrer based on their purchases.
        """

        # Commission for the user who made the purchase
        user_commission_percentage = monthly_purchase.commission_percentage
        user_cumulative_points = monthly_purchase.cumulative_points
        user_commission_earned = round(user_cumulative_points * (user_commission_percentage / 100), 2)

        CommissionHistory.objects.create(
            user=user,
            commission_percentage=user_commission_percentage,
            cumulative_purchase=monthly_purchase.cumulative_purchase,
            cumulative_points=user_cumulative_points,
            commission_earned=user_commission_earned,
            user_total_purchase=monthly_purchase.user_purchase,
            referral_total_purchase=monthly_purchase.referral_purchase,
            order_total_amount=order.total_amount
        )

        # Commission for the referrer
        referrer_commission_percentage = referrer_monthly_purchase.commission_percentage
        referrer_cumulative_points = referrer_monthly_purchase.cumulative_points
        referrer_commission_earned = round(referrer_cumulative_points * (referrer_commission_percentage / 100), 2)

        CommissionHistory.objects.create(
            user=referrer,
            commission_percentage=referrer_commission_percentage,
            cumulative_purchase=referrer_monthly_purchase.cumulative_purchase,
            cumulative_points=referrer_cumulative_points,
            commission_earned=referrer_commission_earned,
            user_total_purchase=referrer_monthly_purchase.user_purchase,
            referral_total_purchase=referrer_monthly_purchase.referral_purchase,
            order_total_amount=order.total_amount
        )


        # CommissionHistory.objects.create(
        #     user=referrer,
        #     commission_percentage=commission_percentage,
        #     cumulative_purchase=cumulative_purchase,
        #     cumulative_points=cumulative_points,
        #     commission_earned=commission_earned,
        #     user_total_purchase=referrer_monthly_purchase.user_purchase,  # User's total purchase including the current order
        #     referral_total_purchase=referrer_monthly_purchase.referral_purchase,  # Referrer's total purchase
        #     order_total_amount= order.total_amount
        # )

            # Add commission to eWallet
            # ewallet = Ewallet.objects.get(user=referrer)
            # ewallet.add_commission(commission_earned)
            
    def generate_tracking_number(self):
        return str(uuid.uuid4())

    def calculate_expected_delivery(self):
        return timezone.now() + timedelta(days=7)

        
class UserPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoint
        fields = '__all__'

class EwalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ewallet
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'

class PayoutTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout_Transaction
        fields = '__all__'
