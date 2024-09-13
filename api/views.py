from django.shortcuts import get_object_or_404
from rest_framework.views import APIView    
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import User, Referral, Product,Order, OrderDetail, UserPoint, OTP, Ewallet, Transactions, Payout_Transaction, OrderTracking, Category, MonthlyPurchase, Statements, SubCategory,CommissionHistory
from .serializers import UserSerializer, ReferralSerializer, ProductSerializer, OrderSerializer, OrderDetailSerializer, UserPointSerializer,EwalletSerializer,TransactionSerializer, PayoutTransactionSerializer, OrderTrackingSerializer, CategorySerializer, MonthlyPurchaseSerializer, StatementsSerializer, SubCategorySerializer, ComissionHistorySerializer
from decimal import Decimal
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
import paypalrestsdk
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from paypalhttp import HttpError
from .paypal import PayPalClient
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import mimetypes
import io
from googleapiclient.http import MediaIoBaseUpload
from paypalrestsdk import Payout, ResourceNotFound
import uuid
from datetime import datetime
from django.utils import timezone
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction








SERVICE_ACCOUNT_FILE = 'analog-context-432718-m9-8085b2892f39.json'
SCOPES = ['https://www.googleapis.com/auth/drive']



paypalrestsdk.configure({
  "mode": "sandbox",  # or "live" for production
  "client_id": "AcfZegwsJHjZkBYFKkSAsNWTRDS3xF_7jjEr-bjMTxROkAj6Nlg1HVXyzIWIFb7Iujtex-uSMM_yTA1H",
  "client_secret": "EBytr5RbE3xIWcirROf1I48hUcp9FP4IlNs-EQff4a3e2jEZ7JQMHqNnvCZKgg5JrLEc_tbZ7qnSQxHy"
})

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
        referee_points = UserPoint.objects.filter(user=referral.referee).values('points','status').first()
        print(referee_points)
        referral_data = ReferralSerializer(referral).data
        referral_data['referee_points'] = referee_points['points'] if referee_points else 0
        referral_data['status'] = referee_points['status']
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

@api_view(['GET'])
def get_categories(request):
    category = Category.objects.all().order_by('-id')
    serializer = CategorySerializer(category, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_subCategories(request):
    subcategory = SubCategory.objects.all()
    serializer = SubCategorySerializer(subcategory, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_statements(request, user_id):
    try:
        current_month_statement = MonthlyPurchase.objects.filter(user_id=user_id).first()
        current_month_statement_serialize = MonthlyPurchaseSerializer(current_month_statement).data
        statements = CommissionHistory.objects.filter(user_id = user_id).all()
        statements_serialize = ComissionHistorySerializer(statements, many=True).data
        return Response(data={"current_month_statement":current_month_statement_serialize,"statements":statements_serialize},status=status.HTTP_200_OK)
    except Exception as e:
        # Handle exceptions and return an error response
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_current_statement(request, user_id):
    try:
        current_month_statement = MonthlyPurchase.objects.filter(user_id=user_id).first()
        current_month_statement_serialize = MonthlyPurchaseSerializer(current_month_statement).data
        return Response(data=current_month_statement_serialize)
    except Exception as e:
        # Handle exceptions and return an error response
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# @api_view(['POST'])
# def create_order(request):
#     serializer = OrderSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_orders(request):
    user_id = request.query_params.get('user_id')
    if user_id:
        orders = Order.objects.filter(user_id=user_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    return Response('ID Error',status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_latest_order(request):
    user_id = request.query_params.get('user_id')
    if user_id:
        order = Order.objects.filter(user_id=user_id).last()
        if not order:
            return Response({'error': 'No order found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    return Response('ID Error',status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_order_tracking(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        tracking = OrderTracking.objects.get(order=order)
        serializer = OrderTrackingSerializer(tracking)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)
    except OrderTracking.DoesNotExist:
        return Response({"error": "Tracking info not available"}, status=404)

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'  # This tells DRF to use 'id' as the URL parameter    


@api_view(['POST'])
def create_transaction(request):
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_transactions(request, user_id):
    transactions = Transactions.objects.filter(user_id=user_id)
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
class EwalletByUserView(generics.RetrieveAPIView):
    queryset = Ewallet.objects.all()
    serializer_class = EwalletSerializer

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(Ewallet, user__id=user_id)

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
    
@api_view(['POST'])
def add_funds(request):
    user_id = request.data.get('user_id')
    amount = request.data.get('amount')

    # Integrate PayPal Payment Process
    # Assuming PayPal SDK is already configured
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": f"{amount}",
                "currency": "USD"
            },
            "description": "Adding funds to eWallet"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:3000/success",
            "cancel_url": "http://localhost:3000/cancel"
        }
    })

    if payment.create():
        # Save the transaction if payment is approved
        ewallet = Ewallet.objects.get(user_id=user_id)
        ewallet.balance += float(amount)
        ewallet.save()

        transaction = Transactions.objects.create(
            user_id=user_id,
            transaction_type='Deposit',
            amount=amount,
            status='Completed'
        )

        return Response({'payment': payment, 'message': 'Funds added successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Error occurred during the payment process.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def make_purchase(request):
    user_id = request.data.get('user_id')
    amount = request.data.get('amount')

    try:
        ewallet = Ewallet.objects.get(user_id=user_id)

        if ewallet.balance < amount:
            return Response({'message': 'Insufficient funds.'}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct the amount from eWallet balance
        ewallet.balance -= amount
        ewallet.save()

        # Record the transaction
        transaction = Transactions.objects.create(
            user_id=user_id,
            transaction_type='Purchase',
            amount=amount,
            status='Completed'
        )

        return Response({'message': 'Purchase successful.'}, status=status.HTTP_200_OK)
    except Ewallet.DoesNotExist:
        return Response({'message': 'Ewallet not found.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def create_order(request):
    user = User.objects.get(id=request.data['user'])  # Replace with actual user logic, like request.user
    serializer = OrderSerializer(data=request.data)
    
    if serializer.is_valid():
        order = serializer.save()

        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response({"error": "Transaction ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if this transaction has already been captured
        if Transactions.objects.filter(transaction_id=transaction_id, status='completed').exists():
            return Response({
                "order_id": order.id,
                "transaction_id": transaction_id,
                "message": "Payment already captured."
            }, status=status.HTTP_200_OK)

        try:
            transaction = Transactions.objects.create(
                user=user,
                order=order,
                transaction_id=transaction_id,
                amount=order.total_amount,
                status='completed'
            )

            return Response({
                "order_id": order.id,
                "transaction_id": transaction.transaction_id,
                "message": "Payment completed successfully."
            }, status=status.HTTP_200_OK)

        except HttpError as error:
            return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_drive_service():
    # Create credentials using service account
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def create_folder(service, folder_name, parent_id=None):
    # Create a folder in Google Drive
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

@api_view(['POST'])
def upload_files(request):
    # Validate required fields
    if 'userId' not in request.data or 'idProof' not in request.FILES or 'addressProof' not in request.FILES:
        return Response({'error': 'userId, idProof, and addressProof are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.data['userId']
    id_proof = request.FILES['idProof']
    address_proof = request.FILES['addressProof']

    try:
        # Initialize Google Drive service
        service = get_drive_service()

        # Create a folder in Google Drive named after the userId
        folder_id = create_folder(service, user_id)

        def upload_file(file):
            # Determine the MIME type
            mime_type, _ = mimetypes.guess_type(file.name)
            if not mime_type:
                mime_type = 'application/octet-stream'

            # Read file content
            file_stream = io.BytesIO(file.read())
            media = MediaIoBaseUpload(file_stream, mimetype=mime_type)

            file_metadata = {
                'name': file.name,
                'parents': [folder_id]
            }
            uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return uploaded_file.get('id')

        # Upload the ID Proof and Address Proof files
        id_proof_id = upload_file(id_proof)
        address_proof_id = upload_file(address_proof)

        # Return the IDs of the uploaded files
        return Response({
            'folderId': folder_id,
            'idProofFileId': id_proof_id,
            'addressProofFileId': address_proof_id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle exceptions and return an error response
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    
# @api_view(['POST'])
# def redeem_points(request):
#     user_id = request.data.get('user_id')
#     points_to_redeem = int(request.data.get('points'))
#     payout_email = request.data.get('paypal_email')

#     # Retrieve user's points based on user_id from the request body
#     try:
#         user = User.objects.get(id=user_id)
#         user_points = user.user_points
#     except User.DoesNotExist:
#         return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
#     except UserPoint.DoesNotExist:
#         return Response({"error": "User has no points."}, status=status.HTTP_400_BAD_REQUEST)

#     # Check if the user has enough points
#     if points_to_redeem > user_points.points:
#         return Response({"error": "Not enough points."}, status=status.HTTP_400_BAD_REQUEST)

#     # Example: 100 points = 1 unit of currency
#     conversion_rate = 0.01
#     amount_to_pay = points_to_redeem * conversion_rate

#     # Generate a unique sender_batch_id using UUID and timestamp
#     unique_batch_id = f"batch_{user_id}_{uuid.uuid4()}_{int(datetime.now().timestamp())}"

#     # Create the PayPal payout
#     payout = Payout({
#         "sender_batch_header": {
#             "sender_batch_id": unique_batch_id,
#             "email_subject": "You have a payout!",
#         },
#         "items": [{
#             "recipient_type": "EMAIL",
#             "amount": {
#                 "value": f"{amount_to_pay:.2f}",
#                 "currency": "USD"
#             },
#             "receiver": payout_email,
#             "note": "Thanks for your patronage!",
#             "sender_item_id": f"item_{user_id}",
#         }]
#     })

#     if payout.create():
#         # Deduct points
#         user_points.points -= points_to_redeem
#         user_points.save()

#         # Save transaction
#         transaction = Payout_Transaction.objects.create(
#             user=user,
#             points_redeemed=points_to_redeem,
#             amount=amount_to_pay,
#             transaction_id=payout.batch_header.payout_batch_id,
#             status='completed'
#         )

#         return Response(PayoutTransactionSerializer(transaction).data, status=status.HTTP_200_OK)
#     else:
#         # Print the error details from the PayPal response
#         error_details = payout.error
#         print("Payout failed:", error_details)
        
#         return Response({
#             "error": "Payout failed.",
#             "details": error_details
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def request_withdrawal(request):
    user_id = request.data.get('user_id')
    withdraw_amount = float(request.data.get('amount'))
    payout_email = request.data.get('paypal_email')

    # Start a transaction to ensure atomicity
    with transaction.atomic():
        try:
            # Retrieve user and eWallet balance
            user = User.objects.get(id=user_id)
            ewallet = user.ewallet

            # Validate the withdrawal amount
            if withdraw_amount <= 0:
                return Response({"error": "Invalid withdrawal amount."}, status=status.HTTP_400_BAD_REQUEST)
            if withdraw_amount > ewallet.balance:
                return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

            # Deduct the amount from eWallet
            original_balance = ewallet.balance
            ewallet.balance -= withdraw_amount
            ewallet.save()

            # Create a payout transaction with 'Pending' status
            transaction_id = f"txn_{user_id}_{uuid.uuid4()}"
            payout_transaction = Payout_Transaction.objects.create(
                user=user,
                points_redeemed=0,  # This can be adjusted based on your points system
                amount=withdraw_amount,
                transaction_id=transaction_id,
                status='pending'
            )

            # Return the created transaction details
            return Response(PayoutTransactionSerializer(payout_transaction).data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        except Ewallet.DoesNotExist:
            return Response({"error": "Ewallet not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Rollback any changes if an error occurs
            transaction.set_rollback(True)
            return Response({"error": f"Error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def transaction_dashboard(request, user_id):
    # Fetch user transactions
    transactions = Transactions.objects.filter(user_id=user_id)
    transactions_data = TransactionSerializer(transactions, many=True).data

    # Fetch user payout transactions
    payout_transactions = Payout_Transaction.objects.filter(user_id=user_id)
    payout_data = PayoutTransactionSerializer(payout_transactions, many=True).data
    # Fetch user points
    try:
        user_points = UserPoint.objects.get(user_id=user_id)
        user_points_data = UserPointSerializer(user_points).data
    except UserPoint.DoesNotExist:
        user_points_data = None

    response_data = {
        "transactions": transactions_data,
        "payout_transactions": payout_data,
        "user_points": user_points_data
    }

    return Response(response_data)

class ResetMonthlyDataView(APIView):
    """
    API endpoint to reset monthly data.
    """
    def post(self, request):
        try:
            # Call the function to reset monthly data
            self.reset_monthly_data()
            return Response({"message": "Monthly data reset completed successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def reset_monthly_data(self):
        # Get the current month
        current_month = timezone.now().month

        # Fetch all MonthlyPurchase records for processing
        monthly_purchases = MonthlyPurchase.objects.all()

        for monthly_purchase in monthly_purchases:
            user = monthly_purchase.user

            # Calculate cumulative commission and store it in history
            if monthly_purchase.cumulative_purchase > 0:
                # Check for the highest commission percentage earned
                commission_percentage = self.get_commission_percentage(monthly_purchase)

                # Create a new CommissionHistory record to store this month's data
                CommissionHistory.objects.create(
                    user=user,
                    commission_percentage=commission_percentage,
                    cumulative_purchase=monthly_purchase.cumulative_purchase,
                    cumulative_points=monthly_purchase.cumulative_points
                )

            # Reset purchases and cumulative points for the new month
            monthly_purchase.user_purchase = 0
            monthly_purchase.referral_purchase = 0
            monthly_purchase.group_purchase = 0
            monthly_purchase.cumulative_points = 0

            # If user reaches a new commission tier, reset cumulative_purchase to 0
            if commission_percentage > Decimal('3.00'):  # If user has exceeded 3%, start fresh for the next tier
                monthly_purchase.cumulative_purchase = 0
            monthly_purchase.save()

    def get_commission_percentage(self, monthly_purchase):
        # Determine the commission percentage based on the rules
        if monthly_purchase.cumulative_purchase >= 34000:
            return Decimal('12.00')
        elif monthly_purchase.cumulative_purchase >= 9600:
            return Decimal('9.00')
        elif monthly_purchase.cumulative_purchase >= 1400:
            return Decimal('6.00')
        elif monthly_purchase.cumulative_purchase >= 400:
            return Decimal('3.00')
        return Decimal('0.00')
    
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter


@api_view(['GET'])
def get_user_and_referrals_purchases(request, user_id):
    try:
        # Get the user
        user = User.objects.get(id=user_id)
        
        # Fetch the user's last 10 purchases
        user_purchases = Order.objects.filter(user=user).order_by('created_at')[:10]
        user_purchase_data = [
            {
                'amount': order.total_amount,
                'date': order.created_at,
                'user': f"{user.first_name} {user.last_name}",
            }
            for order in user_purchases
        ]
        
        # Get all active referrals of the user
        referrals = Referral.objects.filter(referrer=user, isActive=True).values_list('referee', flat=True)
        
        # Fetch the latest 10 purchases across all referrals
        referral_purchases = Order.objects.filter(user__in=referrals).order_by('created_at')[:10]
        referral_purchase_data = [
            {
                'amount': order.total_amount,
                'date': order.created_at,
                'user': f"{order.user.first_name} {order.user.last_name}",
                'referral': True
            }
            for order in referral_purchases
        ]

        # Combine both datasets
        combined_data = {
            'user_purchases': user_purchase_data,
            'referral_purchases': referral_purchase_data
        }
        
        return Response(combined_data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
