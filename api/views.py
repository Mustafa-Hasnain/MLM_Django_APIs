from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Referral, Product,Order, OrderDetail, Transaction, UserPoint, OTP
from .serializers import UserSerializer, ReferralSerializer, ProductSerializer, OrderSerializer, TransactionSerializer, UserPointSerializer
import random
import string
from django.core.mail import send_mail
from django.db.models.functions import TruncMonth
from django.db.models import Count
from twilio.rest import Client
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



@api_view(['POST'])
def register_user(request):
    data = request.data
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    phone_no = data.get('phone_no')
    referral_code = data.get('referral_code', None)
    
    # Generate user's referral code
    user_referral_code = generate_referral_code(phone_no)

    user_serializer = UserSerializer(data={
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'phone_no': phone_no,
        'user_referral_code': user_referral_code
    })

    if user_serializer.is_valid():
        user = user_serializer.save()
        
        if referral_code:
            referrer = User.objects.filter(user_referral_code=referral_code).first()
            if not referrer:
                return Response({'error': 'Referral code not found'}, status=status.HTTP_404_NOT_FOUND)
            
            Referral.objects.create(referrer=referrer, referee=user, referral_code=referral_code)
        
        # Uncomment the line below to send a welcome email
        # send_welcome_email(email, first_name, user_referral_code)
        
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def send_otp(request):
    referral_code = request.data.get('referral_code')
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')

    # Check if referral code exists
    if not User.objects.filter(user_referral_code=referral_code).exists():
        return Response({'message': 'Invalid referral code, please try again.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email and phone number are already registered
    if User.objects.filter(email=email).exists() or User.objects.filter(phone_no=phone_number).exists():
        return Response({'message': 'Email and phone number already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate a 4-digit OTP
    otp = str(random.randint(1000, 9999))

    # Save OTP associated with the phone number
    OTP.objects.update_or_create(phone_number=phone_number, email=email, defaults={'otp': otp})

    # Send OTP using Twilio
    try:
        sender_email = "bigybags@gmail.com"
        sender_password = "ewpfolvcpyuddgwn"
        subject = "Your OTP Code"
        body = f"Your OTP code is {otp}"

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Set up the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use the appropriate SMTP server and port
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
    except Exception as e:
        return Response({'message': f'Failed to send OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    # Check if the email and OTP combination exists in the OTP table
    otp_entry = OTP.objects.filter(email=email, otp=otp).last()

    if otp_entry:
        return Response({'message': 'PIN verified successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid PIN entered.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Retrieve user based on email and password
    user = get_object_or_404(User, email=email, password=password)
    
    # Return the user ID in the response
    return Response({
        'message': 'Login successful',
        'user_id': user.id
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def retrieve_user(request):
    user_id = request.query_params.get('id')
    user = get_object_or_404(User, id=user_id)
    
    # Get the user's referrals
    referrals = Referral.objects.filter(referrer=user)

    # Serialize user data
    user_data = UserSerializer(user).data
    user_points = UserPoint.objects.filter(user=user).first()  # Assuming there's only one UserPoints entry per user
    user_points_data = UserPointSerializer(user_points).data if user_points else None

    
    # Custom serialization to include referees_points
    referrals_data = []
    for referral in referrals:
        referee_points = UserPoint.objects.filter(user=referral.referee).values('points').first()
        referral_data = ReferralSerializer(referral).data
        referral_data['referee_points'] = referee_points['points'] if referee_points else 0
        referrals_data.append(referral_data)

    # Return the combined data
    return Response({'user': user_data, 'referrals': referrals_data,'user_points':user_points_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def new_members(request):
    user_id = request.query_params.get('user_id')
    user = get_object_or_404(User, id=user_id)
    
    # Get the user's referrals (new members)
    referrals = Referral.objects.filter(referrer=user)
    
    # Prepare referees' data
    referees_data = []
    for referral in referrals:
        referee = referral.referee
        referee_data = {
            'email': referee.email,
            'date_joined': referee.created_at,
            'first_name': referee.first_name,
            'last_name': referee.last_name,
        }
        referees_data.append(referee_data)

    # Return the data
    return Response({'referees': referees_data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def referral_stats(request):
    user_id = request.query_params.get('user_id')
    referrals = Referral.objects.filter(referrer_id=user_id)\
        .annotate(month=TruncMonth('created_at'))\
        .values('month')\
        .annotate(count=Count('id'))\
        .order_by('month')
    
    data = {entry['month'].strftime('%b %y'): entry['count'] for entry in referrals}

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_products(request):
    product_id = request.query_params.get('id', None)
    if product_id:
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
    else:
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_order(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_orders(request):
    user_id = request.query_params.get('user_id')
    if user_id:
        orders = Order.objects.filter(user_id=user_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    return Response('ID Error',status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_transaction(request):
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_transactions(request, user_id):
    transactions = Transaction.objects.filter(user_id=user_id)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_user_point(request):
    serializer = UserPointSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_user_point(request, user_id):
    user_point = UserPoint.objects.filter(user_id=user_id).first()
    if not user_point:
        return Response({'error': 'User points not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserPointSerializer(user_point, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user_points(request):
    user_id = request.query_params.get('user_id')
    
    if user_id:
        # If a user ID is provided, get the points for that specific user
        user_points = UserPoint.objects.filter(user_id=user_id).first()
    else:
        # If no user ID is provided, return the first record in the table
        user_points = UserPoint.objects.first()
    
    if user_points:
        # Serialize the single UserPoint object
        user_points_data = UserPointSerializer(user_points).data
    else:
        # Return an empty JSON object if no UserPoint record is found
        user_points_data = {}

    return Response(user_points_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_profile_data(request, user_id):
    try:
        # Get the user data
        user = User.objects.get(id=user_id)
        user_serializer = UserSerializer(user)

        # Get the number of referrals made by this user
        referrals_count = Referral.objects.filter(referrer=user).count()

        # Get the user points data
        user_points = UserPoint.objects.get(user=user)
        user_points_serializer = UserPointSerializer(user_points)

        # Combine the data
        profile_data = {
            'user': user_serializer.data,
            'referrals_count': referrals_count,
            'user_points': user_points_serializer.data
        }

        return Response(profile_data)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except UserPoint.DoesNotExist:
        return Response({'error': 'UserPoints not found for this user'}, status=404)

def generate_referral_code(phone_no):
    last_digits = phone_no[-4:]
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{last_digits}{random_chars}"

# def send_welcome_email(email, first_name, user_referral_code):
#     referral_link = f'http://localhost:8000?ref={user_referral_code}'
#     send_mail(
#         'Welcome to Quickmilk!',
#         f'Welcome to Quickmilk, {first_name}! Use your referral link: {referral_link} to invite others.',
#         'your_email@example.com',
#         [email],
#         fail_silently=False,
#     )
