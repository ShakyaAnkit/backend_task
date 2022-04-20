from celery import shared_task

from django.core.mail import send_mail
from django.utils import timezone
from .models import Account

@shared_task
def wish_birthday():      
    now = timezone.now()
    account_qs = Account.objects.filter(date_of_birth__month=now.month, date_of_birth__day=now.day)
    for account in account_qs:
        send_mail('Happy Birthday !!!!!!!!!!!',
            [account.email])
        return None
