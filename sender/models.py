from datetime import datetime
from django.db import models


def upload_path(instance, filename):
    return filename


class UploadFile(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(verbose_name="", max_length=64)
    path = models.FileField(upload_to=upload_path)
    create_ts = models.DateTimeField(default=datetime.now)
    rq = None

    def save(self, *args, **kwargs):
        UploadFile.rq = kwargs.pop("request")
        print(UploadFile.rq)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Email Html Template'
        db_table = 'email_template'

    def __str__(self):
        return ''


class UserSummary(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    level = models.IntegerField()
    fake_level = models.IntegerField()
    vip_level = models.IntegerField()
    vvip = models.IntegerField()
    total_purchase = models.FloatField()
    max_purchase_price = models.IntegerField()
    last_active_time = models.DateTimeField()
    email = models.CharField(max_length=64)
    ext = models.TextField()

    class Meta:
        verbose_name = 'User Summary'
        db_table = 'user_summary'

    def __str__(self):
        return ''

class UnsubscribeUsers(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    email = models.CharField(max_length=64)
    reason = models.CharField(max_length=256)
    ext = models.TextField()

    class Meta:
        verbose_name = 'Unsubscribe Users'
        db_table = 'unsubscribe_users'

    def __str__(self):
        return ''


class SendingQueue(models.Model):
    id = models.AutoField(primary_key=True)
    from_email = models.CharField(max_length=256)
    subject = models.CharField(max_length=128)
    content_title = models.CharField(max_length=128)
    html_str = models.TextField()
    conditions = models.TextField()
    csv_users = models.TextField()
    start_ts = models.DateTimeField()

    ext = models.TextField()
    class Meta:
        verbose_name = 'Sending Queue'
        db_table = 'sending_queue'

    def __str__(self):
        return ''


class SendResult(models.Model):
    id = models.AutoField(primary_key=True)
    send_id = models.IntegerField()
    content_title = models.CharField(max_length=128)
    status = models.IntegerField(default=0)
    delivery = models.IntegerField(default=0)
    sent = models.IntegerField(default=0)
    opened = models.IntegerField(default=0)
    clicked = models.IntegerField(default=0)
    bounce = models.IntegerField(default=0)
    complaint = models.IntegerField(default=0)
    start_ts = models.DateTimeField()
    finish_ts = models.DateTimeField()
    last_update_ts = models.DateTimeField()

    ext = models.TextField()

    class Meta:
        verbose_name = 'Send Result'
        db_table = 'send_result'

    def __str__(self):
        return ''


class SendUserInfo(models.Model):
    id = models.AutoField(primary_key=True)
    send_key = models.CharField(max_length=32)
    delivery = models.IntegerField(default=0)
    sent = models.IntegerField(default=0)
    opened = models.IntegerField(default=0)
    clicked = models.IntegerField(default=0)
    bounce = models.IntegerField(default=0)
    complaint = models.IntegerField(default=0)
    last_update_ts = models.DateTimeField()

    ext = models.TextField()

    class Meta:
        verbose_name = 'Send User Info'
        db_table = 'send_user_info'

    def __str__(self):
        return ''


class BounceUserEmail(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=64)
    bounce_type =  models.IntegerField(default=0)
    create_ts = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = 'Bounce User Email'
        db_table = 'bounce_user_email'

    def __str__(self):
        return ''


class DeliveryUser(models.Model):
    id = models.AutoField(primary_key=True)
    send_id = models.IntegerField()
    user_id = models.IntegerField()

    class Meta:
        verbose_name = 'Delivery User'
        db_table = 'delivery_user'

    def __str__(self):
        return ''


class CsvUsers(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    email = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'Csv Users'
        db_table = 'csv_users'

    def __str__(self):
        return ''


class Segment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    conditions = models.TextField()
    csv_users = models.TextField()
    gm_name = models.CharField(max_length=32)
    ext = models.TextField()

    class Meta:
        verbose_name = 'Segment'
        db_table = 'segment'

    def __str__(self):
        return ''


class SesTemplate(models.Model):
    id = models.IntegerField(primary_key=True)
    template_name = models.CharField(max_length=128, unique=True)
    subject_part = models.CharField(max_length=256)
    template_type = models.IntegerField()
    create_ts = models.DateTimeField(default=datetime.now)
    last_update_ts = models.DateTimeField(default=datetime.now)
    gm_name = models.CharField(max_length=32)

    class Meta:
        verbose_name = 'Ses Html Template'
        db_table = 'ses_template'

    def __str__(self):
        return ''
