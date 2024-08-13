from rest_framework import serializers
from .models import User, Referral, Product, Order, OrderDetail, Transaction, UserPoint

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        # Create the User instance
        user = User.objects.create(**validated_data)
        
        # Automatically create a UserPoint instance associated with the User
        UserPoint.objects.create(user=user, points=100, status='Executive')
        
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

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['product', 'quantity', 'price']  # Exclude 'order' here

class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at','user', 'total_amount',  'order_details']

    def create(self, validated_data):
        order_details_data = validated_data.pop('order_details')
        order = Order.objects.create(**validated_data)
        # Update user points
        user_points = UserPoint.objects.get(user=order.user)
        user_points.points += order.total_amount
        user_points.save()

        # Check if the user has a referrer
        referral = Referral.objects.filter(referee=order.user).first()
        if referral:
            referrer_points = UserPoint.objects.get(user=referral.referrer)
            referrer_points.referral_points += order.total_amount  # 100% of order amount
            referrer_points.save()
            # Update status based on referral points
            self.update_status(referrer_points)

        # Save order details
        for detail_data in order_details_data:
            OrderDetail.objects.create(order=order, **detail_data)

        return order
    
    def update_status(self, user_points):
        # Define status tiers
        status_tiers = [
            (62500, 'Silver'),
            (12500, 'Sr manager'),
            (2500, 'Manager'),
            (500, 'Sr executive'),
            (100, 'Executive')
        ]

        # Update the user's status based on referral points
        for points, status in status_tiers:
            if user_points.referral_points >= points:
                user_points.status = status
                user_points.save()
                break
    

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class UserPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoint
        fields = '__all__'
