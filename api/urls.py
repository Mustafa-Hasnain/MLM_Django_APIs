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
    path('getCategories/', views.get_categories, name='get_categories'),
    path('getSubCategories/', views.get_subCategories, name='get_subCategories'),
    path('order/', views.create_order, name='create_order'),
    path('order_detail/<int:id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/', views.get_orders, name='get_orders'),
    path('get_latest_order/', views.get_latest_order, name='get_latest_order'),
    path('order_tracking/<int:order_id>/', views.get_order_tracking, name='get_order_tracking'),
    path('transaction/', views.create_transaction, name='create_transaction'),
    path('transactions/<int:user_id>/', views.get_transactions, name='get_transactions'),
    path('userpoint/', views.create_user_point, name='create_user_point'),
    path('userpoint/<int:user_id>/', views.update_user_point, name='update_user_point'),
    path('profile/<int:user_id>/', views.get_profile_data, name='get_profile_data'),
    path('add_funds/', views.add_funds, name='add_funds'),
    path('upload_files/', views.upload_files, name='upload_files'),
    path('redeem_points/',views.redeem_points, name='redeem_points'),
    path('transaction_dashboard/<int:user_id>/', views.transaction_dashboard, name='transaction_dashboard'),
    path('get_user_statements/<int:user_id>/', views.get_user_statements, name='get_user_statements'),
    path('get_current_statement/<int:user_id>/', views.get_current_statement, name='get_current_statement'),
    path('reset-monthly-data/', views.ResetMonthlyDataView.as_view(), name='reset-monthly-data'),
    path('products-search/', views.ProductListView.as_view(), name='product-list'),


]
