import os
import json
import time

from datetime import datetime, timedelta

from django.core import mail
from email.utils import formataddr

from sender.models import *
from .mail_conf import *
from .send_manager import SendManager
#from asgiref.sync import sync_to_async

import logging
logger = logging.getLogger("django")


def check_user(uid, u, conditio_list, exception_list):
    cond_str = ''
    exc_str = ''
    for k in conditio_list:
        result, logic = check_codition(uid, u, k)
        cond_str = cond_str + str(result) + (" and " if logic == 0 else " or ")
    for j in exception_list:
        result, logic = check_codition(uid, u, j)
        exc_str = exc_str + str(result) + (" and " if logic == 0 else " or ")
    cond = eval(cond_str + "True")
    exc = eval(exc_str + "True")
    final = cond if not exception_list else eval(str(cond) + " and not " + str(exc))
    return final

def check_codition(uid, u, condition):
    now = int(time.time())
    c = condition
    logic = condition[3]
    if c[0] == 1:
        b = int(condition[1])
        u_str = str(uid)[::-1]
        if b >= len(u_str):
            return False, logic
        i = int(u_str[b])
        if i not in condition[2]:
            return False, logic
    elif c[0] == 2:
        if u['vip_level'] < condition[1] or (condition[2] >= 0 and u['vip_level'] > condition[2]):
            return False, logic
    if c[0] == 3:
        if u['level'] < condition[1] or (condition[2] >= 0 and u['level'] > condition[2]):
            return False, logic
    elif c[0] == 4:
        if u['total_purchase'] < condition[1] or (condition[2] >= 0 and u['total_purchase'] > condition[2]):
            return False, logic
    elif c[0] == 5:
        user_act_time = time.mktime(u['last_active_time'].timetuple())
        active_time = now - user_act_time
        if active_time <  condition[1] * 3600 or (condition[2] >= 0 and active_time > condition[2] * 3600):
            return False, logic
        else:
            pass
    elif c[0] == 6:
        if condition[1] == 1 and u['pkg_id'] != 106 or condition[1] == 2 and u['pkg_id'] == 106:
            return False, logic
    return True, logic


def to_num_list(str_list):
    num_list = []
    for str_num in str_list:
        if str_num.isdigit():
            val = int(str_num)
        else:
            val = json.loads(str_num)
        num_list.append(val)

    return num_list


def query_summary(request, is_send):
    emails = []
    start = time.time()
    condition_type_list = request.POST.getlist('condition_type_list', [])
    condition_type_list = to_num_list(condition_type_list)
    except_list = request.POST.getlist('except_condition', [])
    except_list = to_num_list(except_list)

    condition_list = []
    exception_list = []
    ext = {}

    for k in range(len(condition_type_list)):
        item_type = condition_type_list[k]
        if item_type <= 0:
            break

        item_val_str = 'item_val_%d_%d' % (item_type, k)
        item_val_list = request.POST.getlist(item_val_str, [])
        item_val_list = to_num_list(item_val_list)
        if item_type == 15:
            item_val_list.append(1)
        condition = [item_type] + item_val_list

        condition_list.append(condition)
    if except_list:
        for k in range(len(except_list)):
            item_type = except_list[k]
            if item_type <= 0:
                break

            item_val_str = 'item_val_%d_%d' % (item_type, k+5)
            item_val_list = request.POST.getlist(item_val_str, [])
            item_val_list = to_num_list(item_val_list)
            if item_type == 15:
                item_val_list.append(1)
            condition = [item_type] + item_val_list

            exception_list.append(condition)
            ext['except_list'] = exception_list
    if not is_send:
        emails = get_users_by_condition(condition_list, exception_list)
    else:
        build_sending_queue(request, conditions=condition_list, extra=ext)

    ret = {
        'use_time_sec': round(time.time() - start, 3),
        'user_count': len(emails),
        'emails':emails
    }
    return ret


def get_html_from_file(file_name):
    html_str = ''
    file_name = "./sender/upload/%s" % file_name
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            html_str = f.read()
    return html_str


def send_one_email(send_id, subject, from_email, to_email, html_str, uid):
    for e in to_email:
        if SendManager().check_is_bounce_email(e):
            return
    recipient_list = to_email
    html_str = replace_html(html_str, uid, send_id)

    email = mail.EmailMessage(subject, html_str, from_email, recipient_list)
    email.content_subtype = 'html'
    email.extra_headers['send_key'] = ("%s_%s") % (send_id, uid)
    try:
        email.send()
    except Exception as e:
        logger.error("fail to send email %s as err: %s", (to_email, str(e)))


def create_email_template(send_id, subject, from_email, to_email, html_str, uid):
    for e in to_email:
        if SendManager().check_is_bounce_email(e):
            return None
    recipient_list = to_email
    html_str = replace_html(html_str, uid, send_id)

    email = mail.EmailMessage(subject, html_str, from_email, recipient_list)
    email.content_subtype = 'html'
    email.extra_headers['send_key'] = ("%s_%s") % (send_id, uid)
    return email


def build_sending_queue(request, conditions=None, csv_users=None, extra=None):
    html_file = request.FILES.get('html_file', None)
    from_email = request.POST['from']
    from_head = request.POST['from_head']
    subject = request.POST['subject']
    content_title = request.POST.get('content_title', '')
    start_time = request.POST.get('start_time', '')
    from_email = formataddr((from_head, from_email))
    start_ts = None
    limit_start_ts = datetime.now() + timedelta(seconds=10)
    if start_time:
        if start_time.find("T") != -1:
            start_ts = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        else:
            start_ts = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        if start_ts < limit_start_ts:
            start_ts = limit_start_ts
    if not start_ts:
        start_ts = limit_start_ts

    html_template = UploadFile(title=html_file.name, path=html_file)
    html_template.save(request=request, using=PRODUCT)
    create_sending_queue(from_email, subject, html_template.path, start_ts, content_title, conditions=conditions, csv_users=csv_users, ext=extra)
    SendManager().update_sending()


def create_sending_queue(from_email, subject, html_str, start_ts, content_title, conditions=None, csv_users=None, ext=None):
    if conditions is not None:
        conditions = json.dumps(conditions)
    if csv_users is not None:
        csv_users = json.dumps(csv_users)
    if ext:
        ext = json.dumps(ext)
    send = SendingQueue(from_email=from_email, subject=subject, html_str=html_str, start_ts=start_ts, content_title=content_title, conditions=conditions, csv_users=csv_users, ext=ext)
    send.save(using=PRODUCT)
    return send.id


def create_send_result(send_id, content_title, delivery, finish=False):
    send_result = SendResult(send_id=send_id, content_title=content_title, delivery=delivery, start_ts=datetime.now())
    if not send_id:
        send_result.save(using=PRODUCT)
        send_result.send_id = 10000000 + send_result.id
        send_result.status = 0
    if finish:
        send_result.finish_ts = datetime.now()
        send_result.status = -1
    send_result.save(using=PRODUCT)
    return send_result.send_id


def update_send_result(send_id, delivery=0, sent=0, bounce=0, opened=0, clicked=0, finish=False):
    send_result = SendResult.objects.using(PRODUCT).filter(send_id=send_id).first()
    if not send_result:
        return
    if delivery:
        send_result.delivery += delivery
    if sent:
        send_result.sent += sent
    if opened:
        send_result.opened += opened
    if clicked:
        send_result.clicked += clicked
    if bounce:
        send_result.bounce += bounce
    if finish:
        send_result.finish_ts = datetime.now()
        send_result.status = 1
    send_result.last_update_ts = datetime.now()
    send_result.save(using=PRODUCT)


def get_users_by_condition(condition_list, exception_list):
    emails = []
    users_email = SendManager().get_users_email()
    for uid, u in users_email.items():
        if check_user(uid, u, condition_list, exception_list):
            email = u['email']
            unsub_info = SendManager().check_unsubscribe_email(email)
            if not unsub_info:
                emails.append({
                    'user_id': uid,
                    "email": u['email'],
                    "level": u['level'],
                    "vip_level": u['vip_level'],
                    "total_purchase": u['total_purchase'],
                    "last_active_time": u['last_active'],
                    "pkg_id": u["pkg_id"],
                    "pkg_from": u["pkg_from"],
                    "facebook_name": u["facebook_name"],
                })
    return emails


def send_email_condition(send_id, from_email, subject, content_title, html_str, condition_list, except_list):
    send_id = create_send_result(send_id, content_title, 0)
    emails = get_users_by_condition(condition_list, except_list)
    with mail.get_connection(fail_silently=True) as connection:
        email_temps = []
        for email in emails:
            sub = subject.replace("{FB_name}", email["facebook_name"])
            e = create_email_template(send_id, sub, from_email, [email["email"]], html_str, email["user_id"])
            if e:
                email_temps.append(e)
            if len(email_temps) >= ONE_SECOND_COUNT:
                connection.send_messages(email_temps)
                email_temps = []
                time.sleep(1)
        if len(email_temps) > 0:
            connection.send_messages(email_temps)
            email_temps = []
    update_send_result(send_id, finish=True)

    return emails


def send_email_csv_users(send_id, from_email, subject, content_title, html_str, csv_users):
    send_id = create_send_result(send_id, content_title, 0)
    with mail.get_connection(fail_silently=True) as connection:
        email_temps = []
        for row in csv_users:
            email = None
            fb_name = "Hi Dear"
            if isinstance(row, list):
                if not row[0]:
                    continue
                uid = int(row[0])
                email = row[1]
            else:
                uid = int(row)
                users_email = SendManager().get_users_email()
                u = users_email.get(uid)
                if u:
                    email = u['email']
                    fb_name = u['facebook_name']
                else:
                    email = SendManager().get_csv_email(uid)
            if email:
                unsub_info = SendManager().check_unsubscribe_email(email)
                if not unsub_info:
                    sub = subject.replace("{FB_name}", fb_name)
                    e = create_email_template(send_id, sub, from_email, [email], html_str, uid)
                    if e:
                        email_temps.append(e)
                    if len(email_temps) >= ONE_SECOND_COUNT:
                        connection.send_messages(email_temps)
                        email_temps = []
                        time.sleep(1)
        if len(email_temps) > 0:
            connection.send_messages(email_temps)
            email_temps = []
    update_send_result(send_id, finish=True)
    return csv_users


def send_email_by_segments(send_id, from_email, subject, content_title, html_str, ext):
    send_id = create_send_result(send_id, content_title, 0)
    emails = []
    sid1 = ext['seg_1']
    sid2 = ext.get('seg_2', -1)
    seg1 = Segment.objects.using(PRODUCT).filter(id=sid1).first()
    seg2 = Segment.objects.using(PRODUCT).filter(id=sid2).first()
    if seg1.conditions:
        con1 = json.loads(seg1.conditions)
        con2 = []
        if seg2 and seg2.conditions:
            con2 = json.loads(seg2.conditions)
        emails = get_users_by_condition(con1, con2)
    elif seg1.csv_users:
        csv1 = json.loads(seg1.csv_users)
        csv2 = []
        if seg2 and seg2.csv_users:
            csv2 = json.loads(seg2.csv_users)
        users_email = SendManager().get_users_email()
        for uid in csv1:
            if uid not in csv2:
                u = users_email.get(uid)
                if u:
                    emails.append({
                        'user_id': uid,
                        "email": u['email'],
                        'facebook_name': u['facebook_name'],
                    })
    if emails:
        with mail.get_connection(fail_silently=True) as connection:
            email_temps = []
            for email in emails:
                sub = subject.replace("{FB_name}", email["facebook_name"])
                e = create_email_template(send_id, sub, from_email, [email["email"]], html_str, email["user_id"])
                if e:
                    email_temps.append(e)
                if len(email_temps) >= ONE_SECOND_COUNT:
                    connection.send_messages(email_temps)
                    email_temps = []
                    time.sleep(1)
            if len(email_temps) > 0:
                connection.send_messages(email_temps)
                email_temps = []
    update_send_result(send_id, finish=True)

    return emails

def query_send(request):
    start = time.time()
    SendManager().update_sending()
    sending_list, send_results = SendManager().get_send_info()
    ret = {
        'use_time_sec': round(time.time() - start, 3),
        'user_count': 0,
        'sending': sending_list,
        'send_result': send_results
    }

    return ret


def delete_send(request):
    sid = int(request.POST['id'])
    if sid > 0:
        SendingQueue.objects.using(PRODUCT).filter(id=sid).delete()

    return query_send(request)


def send_from_queue(send):
    send_id = send.id
    from_email = send.from_email
    subject = send.subject
    content_title = send.content_title
    html_str = get_html_from_file(send.html_str)
    if not html_str:
        create_send_result(send_id, content_title, 0, finish=True)
        return
    if send.csv_users is not None:
        csv_users = json.loads(send.csv_users)
        return send_email_csv_users(send_id, from_email, subject, content_title, html_str, csv_users)
    if send.conditions is not None:
        condition_list = json.loads(send.conditions)
        except_list = []
        if send.ext:
            ext = json.loads(send.ext)
            except_list = ext.get('except_list', [])
        return send_email_condition(send_id, from_email, subject, content_title, html_str, condition_list, except_list)
    if send.ext:
        ext = json.loads(send.ext)
        if ext.get('seg_1'):
            return send_email_by_segments(send_id, from_email, subject, content_title, html_str, ext)


def query_stat(send_id):
    start = time.time()

    deliverys = []
    delivery_users = DeliveryUser.objects.using(PRODUCT_RO).filter(send_id=send_id).all()
    if not delivery_users:
        ret = {
            'use_time_sec': round(time.time() - start, 3),
            'send_id': send_id,
            'user_count': 0
        }
        return ret

    send_key = '%s_' % send_id
    send_map = {}
    send_users = SendUserInfo.objects.using(PRODUCT_RO).filter(send_key__istartswith=send_key).values('send_key', 'opened', 'clicked').all()
    for send in send_users:
        user_id = int(send['send_key'].split('_')[1])
        send_map[user_id] = {
            'opened' : send['opened'],
            'clicked' : send['clicked'],
        }

    user_count = 0
    for s in delivery_users:
        uid = s.user_id
        deliverys.append({
            "user_id": uid,
            "opened": send_map.get(uid,{}).get('opened', 0),
            "clicked": send_map.get(uid,{}).get('clicked', 0),
        })
    ret = {
        'use_time_sec': round(time.time() - start, 3),
        'user_count': user_count,
        'stat': deliverys
    }

    return ret


def query_unsubscribe_users():
    start = time.time()
    users = UnsubscribeUsers.objects.using(PRODUCT_RO).values("user_id", "email", "reason").order_by('-id')[:100]
    user_count = len(users)
    unsub_users = []
    for u in users:
        unsub_users.append({
            'user_id': u['user_id'],
            'email': u['email'],
            'reason': u['reason'],
        })
    ret = {
        'use_time_sec': round(time.time() - start, 3),
        'user_count': user_count,
        'unsub_users': unsub_users
    }
    return ret


def save_csv_user(csv_users=None):
    if not csv_users:
        return
    create_list = []
    update_list = []
    for uid, email in csv_users:
        uid = int(uid)
        mail = CsvUsers.objects.using(PRODUCT).filter(user_id=uid).first()
        if not mail:
            mail = CsvUsers(user_id=uid, email=email)
            create_list.append(mail)
        else:
            if getattr(mail, 'email') != email:
                setattr(mail, 'email', email)
                update_list.append(mail)
    if create_list:
        CsvUsers.objects.using(PRODUCT).bulk_create(create_list)
    if update_list:
        CsvUsers.objects.using(PRODUCT).bulk_update(update_list, ['user_id','email'])


def query_all_csv_users():
    start = time.time()
    users = CsvUsers.objects.using(PRODUCT_RO).values("user_id", "email").all()
    user_count = len(users)
    csv_users = []
    for u in users:
        csv_users.append({
            'user_id': u['user_id'],
            'email': u['email'],
        })
    ret = {
        'use_time_sec': round(time.time() - start, 3),
        'user_count': user_count,
        'csv_users': csv_users
    }
    return ret


def query_segments(search=''):
    if search:
        segments = Segment.objects.using(PRODUCT_RO).filter(name__icontains=search)
    else:
        segments = Segment.objects.using(PRODUCT_RO).all()
    seg_list = []
    for u in segments:
        seg_list.append({
            'id': u.id,
            'name': u.name,
            'conditions': u.conditions,
            'csv': True if u.csv_users else False,
            'gm_name': u.gm_name,
        })
    ret = {
        'segments': seg_list,
    }
    return ret


def query_summary_by_id(uid):
    users_email = SendManager().get_users_email()
    u = users_email.get(uid)
    summary = None
    if u:
        summary = {
            'uid': uid,
            'email': u['email'],
            "level": u['level'],
            "vip_level": u['vip_level'],
            "total_purchase": u['total_purchase'],
            "last_active_time": u['last_active'],
            "pkg_id": u["pkg_id"],
            "pkg_from": u["pkg_from"],
            "facebook_name": u["facebook_name"],
        }

    return summary


def query_manage_template(template_name=''):
    if template_name:
        manage_template = SesTemplate.objects.using(PRODUCT_RO).filter(template_name=template_name)
    else:
        manage_template = SesTemplate.objects.using(PRODUCT_RO).all()
    manage_template_list = []
    for u in manage_template:
        manage_template_list.append({
            'id': u.id,
            'template_name': u.template_name,
            'subject_part': u.subject_part,
            'template_type': u.template_type,
            'gm_name': u.gm_name,
            'create_ts': u.create_ts,
            'last_update_ts': u.last_update_ts
        })
    ret = {
        'templates': manage_template_list,
    }
    return ret

