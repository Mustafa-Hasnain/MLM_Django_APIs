# tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Referral

@shared_task
def deactivate_inactive_referrals():
    one_month_ago = timezone.now() - timedelta(days=30)
    referrals_to_deactivate = Referral.objects.filter(updated_at__lt=one_month_ago, isActive=True)

    for referral in referrals_to_deactivate:
        referral.isActive = False
        referral.save()
