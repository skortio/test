from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events


from .send_manager import SendManager
from .send_task_manager import SendTaskManager

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


@register_job(scheduler, "interval", hours=1, id='load_email', replace_existing=True)
def load_email():
    SendManager().update_user_email()


@register_job(scheduler, "interval", hours=1, id='load_sending', replace_existing=True)
def load_sending():
    SendManager().update_sending()


@register_job(scheduler, "interval", seconds=5, id='save_send_signal', replace_existing=True)
def save_send_signal():
    SendTaskManager().save_send_signal()


@register_job(scheduler, "interval", seconds=10, id='save_send_user', replace_existing=True)
def save_send_user():
    SendTaskManager().save_send_user()


@register_job(scheduler, "interval", seconds=20, id='save_bounce_email', replace_existing=True)
def save_bounce_email():
    SendTaskManager().save_bounce_email()

@register_job(scheduler, "interval", seconds=15, id='save_delivery', replace_existing=True)
def save_delivery():
    SendTaskManager().save_delivery()

@register_job(scheduler, "interval", seconds=3, id='check_sending', replace_existing=True)
def check_sending():
    SendTaskManager().on_timer_check_sending()


def start_timer():
    SendManager().update_user_email()
    SendManager().update_sending()
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started!")
