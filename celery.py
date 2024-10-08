# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlm_proect.settings')

app = Celery('mlm_proect')

# Using a string here means the worker doesn’t have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'deactivate-inactive-referrals-everyday': {
        'task': 'api.deactivate_inactive_referrals',
        'schedule': crontab(hour=0, minute=0),  # Runs every day at midnight
    },
}
