from django.core.management.base import BaseCommand
from api.models import MonthlyPurchase

class Command(BaseCommand):
    help = 'Reset monthly purchases for all users'

    def handle(self, *args, **kwargs):
        for monthly_purchase in MonthlyPurchase.objects.all():
            monthly_purchase.reset_monthly_data()
        self.stdout.write(self.style.SUCCESS('Successfully reset monthly purchases'))
