import pymysql
pymysql.install_as_MySQLdb()

from django.dispatch import receiver
from django_ses.signals import *


'''
bounce_received = Signal()
complaint_received = Signal()
delivery_received = Signal()
send_received = Signal()
open_received = Signal()
click_received = Signal()

'''


def get_mail_keys(mail_obj):
    send_key, send_info, to_email = None, None, None
    if not mail_obj:
        return send_key, send_info, to_email
    headers = mail_obj['headers']
    if not headers:
        return send_key, send_info, to_email
    
    for v in headers:
        if v['name'] == "send_key":
            send_key, send_info = v['value'], v['value'].split("_")
        if v['name'] == "To":
            to_email = v['value']
    return send_key, send_info, to_email


def update_send(mail_obj, update_key):
    send_key, send_info, to_email =  get_mail_keys(mail_obj)
    if send_key and send_info:
        send_id = int(send_info[0])
        from .send_task_manager import SendTaskManager
        if update_key in ['sent']:
            SendTaskManager().update_signal_cache(send_id, update_key)
        elif update_key in ['delivery']:
            SendTaskManager().update_delivery(send_id, int(send_info[1]))
        elif update_key in ['bounce']:
            SendTaskManager().update_bounce_email(send_id, to_email)
        else:
            SendTaskManager().recieve_user_signal(send_id, send_key, update_key)


@receiver(bounce_received)
def bounce_handler(sender, mail_obj, bounce_obj, raw_message, *args, **kwargs):
    # you can then use the message ID and/or recipient_list(email address) to identify any problematic email messages that you have sent
    message_id = mail_obj['messageId']
    recipient_list = mail_obj['destination']
    update_send(mail_obj, 'bounce')
    print("This is bounce email object")



@receiver(complaint_received)
def complaint_handler(sender, mail_obj, complaint_obj, raw_message,  *args, **kwargs):
    message_id = mail_obj['messageId']
    recipient_list = mail_obj['destination']

    print("This is complaint email object")
    print(mail_obj)



@receiver(delivery_received)
def delivery_handler(sender, mail_obj, delivery_obj, raw_message,  *args, **kwargs):
    message_id = mail_obj['messageId']
    recipient_list = mail_obj['destination']
    update_send(mail_obj, 'delivery')
    print("This is delivery email object")



@receiver(send_received)
def send_handler(sender, mail_obj, raw_message,  *args, **kwargs):
    message_id = mail_obj['messageId']
    recipient_list = mail_obj['destination']
    update_send(mail_obj, 'sent')
    print("This is send email object")



@receiver(open_received)
def open_handler(sender, mail_obj, raw_message, *args, **kwargs):
    message_id = mail_obj['messageId']
    recipient_list = mail_obj['destination']
    update_send(mail_obj, 'opened')
    print("This is open email object")


@receiver(click_received)
def click_handler(sender, mail_obj, raw_message, *args, **kwargs):
    message_id = mail_obj['messageId']
    recipient_list = mail_obj['destination']
    update_send(mail_obj, 'clicked')
    print("This is click email object")
