from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('user_network/', views.retrieve_user, name='retrieve_user'),
    path('new_members/', views.new_members, name='new_members'),
    path('user_points/', views.get_user_points, name='get_user_points'),
    path('referralstats/', views.referral_stats, name='referral_stats'),
    path('products/', views.get_products, name='get_products'),
    path('order/', views.create_order, name='create_order'),
    path('orders/', views.get_orders, name='get_orders'),
    path('transaction/', views.create_transaction, name='create_transaction'),
    path('transactions/<int:user_id>/', views.get_transactions, name='get_transactions'),
    path('userpoint/', views.create_user_point, name='create_user_point'),
    path('userpoint/<int:user_id>/', views.update_user_point, name='update_user_point'),
    path('profile/<int:user_id>/', views.get_profile_data, name='get_profile_data'),
]
