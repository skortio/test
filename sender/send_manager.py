
import time

from datetime import datetime, date
from .mail_conf import *
from sender.models import *
from .singleton import Singleton


def to_str(d):
    if isinstance(d, (datetime, date)):
        return d.strftime('%Y/%m/%d %H:%M:%S')
    return d


class SendManager(metaclass=Singleton):
    def __init__(self):
        self.users_email = {}
        self.unsubscribe_users = {}
        self.sending_list = []
        self.send_results = []
        self.bounce_map = {}


    def get_users_email(self):
        if not self.users_email:
            self.update_user_email()
        return self.users_email
    
    def check_unsunbscribe(self, uid):
        return self.unsubscribe_users.get(uid)

    def check_is_bounce_email(self, email):
        return self.bounce_map.get(email)
    
    def add_bounce_email(self, email):
        if email in self.bounce_map:
            return False
        self.bounce_map[email] = 1
        return True
    
    def get_send_info(self):
        return self.sending_list, self.send_results
    
    def update_user_email(self):
        email = {}
        for i in range(QUERY_GROUP):
            m = i*QUERY_ONE_TIME+1
            n = (i+1)*QUERY_ONE_TIME
            users = UserSummary.objects.using(VEGAS_RO).filter(id__range=[m, n]).values('user_id', 'email', 'vip_level', 'level', 'total_purchase', 'last_active_time')
            if not users:
                break
            for u in users:
                email[u['user_id']] = {
                    "email": u['email'],
                    "level": u['level'],
                    "vip_level": u['vip_level'],
                    "total_purchase": u['total_purchase'],
                    "last_active": to_str(u['last_active_time']),
                    "last_active_time": u['last_active_time'],
                }
            time.sleep(1)
        self.users_email = email
        users = {}
        unsub_users = UnsubscribeUsers.objects.using(PRODUCT_RO).values('user_id').all()
        for u in unsub_users:
            users[u['user_id']] = 1
        self.unsubscribe_users = users

        bounces = {}
        bounce_list = BounceUserEmail.objects.using(PRODUCT_RO).values('email').all()
        for b in bounce_list:
            bounces[b['email']] = 1
        self.bounce_map = bounces

        print("update email suc")

    def update_sending(self):
        sending = []
        queue = SendingQueue.objects.using(PRODUCT).values('id', 'from_email','content_title','conditions','start_ts', 'html_str').all()
        for q in queue:
            sending.append({
                "id": q["id"],
                "from_email": q["from_email"],
                "content_title": q["content_title"],
                "conditions": q["conditions"],
                "html_str": q['html_str'],
                "start_ts": to_str(q["start_ts"]),
                "start_time": q["start_ts"],
                
            })
        self.sending_list = sending
        results = []
        send_result = SendResult.objects.using(PRODUCT_RO).values("send_id", "content_title", "status", "delivery", "sent", "bounce", "opened", "clicked", "start_ts", "finish_ts", "last_update_ts").all()
        for r in send_result:
            results.append({
                "send_id": r["send_id"],
                "content_title": r["content_title"],
                "status": r["status"],
                "delivery": r["delivery"],
                "sent": r["sent"],
                "bounce": r["bounce"],
                "opened": r["opened"],
                "clicked": r["clicked"],
                "start_ts": to_str(r["start_ts"]),
                "finish_ts": to_str(r["finish_ts"]),
                "last_update_ts": to_str(r["last_update_ts"]),
            })
        self.send_results = results

        print("update send suc")
