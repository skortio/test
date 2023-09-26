
from datetime import datetime

from .mail_conf import *
from sender.models import SendingQueue, SendUserInfo, BounceUserEmail, DeliveryUser
from .singleton import Singleton
from .send_manager import SendManager
from .mail_collector import update_send_result, send_from_queue
import logging
logger = logging.getLogger("django")

USER_UPDATE_FIELDS = ['opened', 'clicked', 'last_update_ts']
class SendTaskManager(metaclass=Singleton):
    def __init__(self):
        self.is_sending = False
        
        # cache data
        self.user_signal = {}
        self.signal_cache = {}
        self.bounce = []
        self.delivery = []

        # saving
        self.saving_signal = {}
        self.saving_user = {}
        self.saving_bounce = []
        self.saving_delivery= []

    def on_timer_check_sending(self):
        print("SendTaskManager in sending email : %s" % (1 if self.is_sending else 0))
        if self.is_sending:
            return
        send_queue, _ = SendManager().get_send_info()
        if not send_queue:
            return
        now = datetime.now() 
        
        self.is_sending = True
        for s in send_queue:
            if now > s['start_time']:
                sid = s['id']
                try:
                    send = SendingQueue.objects.using(PRODUCT).filter(id=sid).first()
                    if send:
                        send_from_queue(send)
                except Exception as e:
                    logger.error('on_timer_check_sending Failed "%s"', e)
                finally:
                    SendingQueue.objects.using(PRODUCT).filter(id=sid).delete()
                    send_queue.remove(s)
                    break
        self.is_sending = False

    def save_send_signal(self):
        print("SendTaskManager saving signal: %s" % (1 if self.saving_signal else 0))
        if self.saving_signal:
            return
        
        self.saving_signal = self.signal_cache
        self.signal_cache = {}
        for send_id, v in self.saving_signal.items():
            try:
                v["send_id"] = int(send_id)
                update_send_result(**v)
            except Exception as e:
                logger.error('save_send_signal Failed "%s"', e)
            finally:
                self.saving_signal = {}
                break
            
    def save_send_user(self):
        print("SendTaskManager saving user: %s" % (1 if self.saving_user else 0))
        if self.saving_bounce:
            return
        
        self.saving_user = self.user_signal
        self.user_signal = {}
        create_list = []
        upate_list = []
        for send_key, v in self.saving_user.items():
            if v["update"] == 2:
                create_list.append(v["item"])
            elif v["update"] == 1:
                upate_list.append(v["item"])
        try:
            if create_list:
                SendUserInfo.objects.using(PRODUCT).bulk_create(create_list, batch_size=1000)
            if upate_list:
                SendUserInfo.objects.using(PRODUCT).bulk_update(upate_list, USER_UPDATE_FIELDS, batch_size=1000)
        except Exception as e:
            logger.error('save_send_user Failed "%s"', e)
        finally:
            self.saving_user = {}

    def save_bounce_email(self):
        print("SendTaskManager saving bounce: %s" % (1 if self.saving_bounce else 0))
        if self.saving_bounce:
            return
        
        self.saving_bounce = self.bounce
        self.bounce = []
        try:
            BounceUserEmail.objects.using(PRODUCT).bulk_create(self.saving_bounce, batch_size=1000)
        except Exception as e:
            logger.error('save_bounce_email Failed "%s"', e)
        finally:
            self.saving_bounce = []

    def save_delivery(self):
        print("SendTaskManager saving delivery: %s" % (1 if self.saving_delivery else 0))
        if self.saving_delivery:
            return
        
        self.saving_delivery = self.delivery
        self.delivery = []
        try:
            DeliveryUser.objects.using(PRODUCT).bulk_create(self.saving_delivery, batch_size=1000)
        except Exception as e:
            logger.error('save_delivery Failed "%s"', e)
        finally:
            self.saving_delivery = []

        
    def update_signal_cache(self, send_id, update_key, count=1):
        if send_id not in self.signal_cache:
            self.signal_cache[send_id] = {update_key: count}
        elif update_key not in self.signal_cache[send_id]:
            self.signal_cache[send_id][update_key] = count
        else:
            self.signal_cache[send_id][update_key] += count
    
    def recieve_user_signal(self, send_id, send_key, update_key):
        update_to_cache = False
        if send_key not in self.user_signal:
            value = 0
            update = 1
            send = SendUserInfo.objects.using(PRODUCT).filter(send_key=send_key).first()
            if not send:
                if self.saving_user and send_key in self.saving_user:
                    send = self.saving_user["item"]
                    self.user_signal[send_key] = { "item" : send, "update": 1}
                else:
                    send = SendUserInfo(send_key=send_key)
                    update = 2
                update_to_cache = True
            else:
                value = getattr(send, update_key)
                if value <= 0:
                    update_to_cache = True
            self.user_signal[send_key] = { "item" : send, "update": update}
        else:
            send = self.user_signal[send_key]["item"]
            value = getattr(send, update_key)
            if value <= 0:
                update_to_cache = True
            if self.user_signal[send_key]['update'] <= 0:
                self.user_signal[send_key]['update'] = 1
        setattr(send, update_key, value+1)
        send.last_update_ts = datetime.now()
        if update_to_cache:
            self.update_signal_cache(send_id, update_key, 1)

    def update_bounce_email(self, send_id, email):
        if SendManager().add_bounce_email(email):
            self.update_signal_cache(send_id, 'bounce', 1)
            self.bounce.append(BounceUserEmail(email=email))

    def update_delivery(self, send_id, user_id):
        self.delivery.append(DeliveryUser(send_id=send_id, user_id=user_id))
        self.update_signal_cache(send_id, 'delivery', 1)
        