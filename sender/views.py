import datetime
import time
import csv
import io

from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# users/views.py

#from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login, logout
from jinja2 import Template

from sender.models import UserSummary, UnsubscribeUsers, Segment
from .mail_collector import *
from .models import SendResult
from .send_manager import to_str
from .ses_template import create_ses_template, get_ses_template, update_ses_template, delete_ses_template
from .timer_manager import start_timer

# start_timer()


def normal_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            # 返回登录失败信息
            return HttpResponse('login failed')

    return render(request, 'login.html')


def normal_logout(request):
    logout(request)
    return redirect('/login')


def unsub_user(request):
    if request.method == 'POST':
        reason = request.POST.get("unsubOpt", "")
        if request.POST['otherText']:
            reason = request.POST['otherText']
        user_id = request.POST['user_id']
        email = ''
        if user_id:
            user_email = UserSummary.objects.using(VEGAS_RO).values('email').filter(user_id=user_id).first()
            if user_email:
                email_dict = UnsubscribeUsers.objects.using(PRODUCT).values('email').filter(email=user_email).first()
                if not email_dict:
                    t = UnsubscribeUsers(user_id=user_id, email=user_email, reason=reason)
                    t.save(using=PRODUCT)
                return render(request, 'thank_you.html')
            else:
                return render(request, 'jump_page.html')



def unsubscribe(request, uid):
    context = {
        "unbind_user_id": uid
    }
    return render(request, "unsub_email.html", context=context)


@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='/login/')
def send_email_text(request):
    if request.method == 'POST':
        try:
            subject = request.POST['subject']
            message = request.POST['message']
            from_email = request.POST['from']
            html_message = bool(request.POST.get('html-message', False))
            recipient_list = [request.POST['to']]

            email = EmailMessage(subject, message, from_email, recipient_list)
            if html_message:
                email.content_subtype = 'html'
            email.send()
            return HttpResponse('Email sent :)')
        except KeyError:
            return HttpResponse('Please fill in all fields')
    else:
        return render(request, 'send_email.html')


@login_required(login_url='/login/')
def send_email_html(request):
    if request.method == 'POST':
        try:
            start = time.time()
            to_email = request.POST['to']
            user_id = request.POST.get('user_id', 1)
            csv_users = [[user_id, to_email]]
            build_sending_queue(request, csv_users=csv_users)
            ret = {
                'use_time_sec': round(time.time() - start, 3),
                'user_count': 1,
                'csv_mails':csv_users
            }
            return render(request, "list.html", context=ret)
        except KeyError:
            return HttpResponse('Please fill in all fields')

    else:
        return render(request, 'send_email_file.html')


@login_required(login_url='/login/')
def send_email_batch(request):
    if request.method == 'POST':
        try:
            ret = query_summary(request, True)
            return render(request, 'list.html', ret)
        except KeyError:
            return HttpResponse('Please fill in all fields')
    else:
        return render(request, 'send_email_batch.html')


@login_required(login_url='/login/')
def query_user_info(request):
    if request.method == 'POST':
        #try:
            ret = query_summary(request, False)
            return render(request, 'list.html', ret)
        #except KeyError:
        #    return HttpResponse('Please fill in all fields')
    else:
        return render(request, 'query_user_info.html')


@login_required(login_url='/login/')
def query_user_summary(request):
    if request.method == 'POST':
        uid = int(request.POST['uid'])
        start = time.time()
        summary = query_summary_by_id(uid)
        ret = {
            'use_time_sec': round(time.time() - start, 3),
            'user_count': 1 if summary else 0,
            'summary': summary
        }
        return render(request, 'list.html', ret)
    else:
        return render(request, 'query_send_info.html')


@login_required(login_url='/login/')
def send_email_csv(request):
    if request.method == 'POST':
        start = time.time()
        csv_file = request.FILES.get('csv_file', None)
        file_data = csv_file.read().decode("utf-8-sig")
        rows = csv.DictReader(io.StringIO(file_data), delimiter=',')
        count = 0
        csv_users = []
        ids = []
        for row in rows:
            if not row["id"]:
                break
            ids.append(row["id"])
            csv_users.append([row["id"], row["email"]])
        build_sending_queue(request, csv_users=ids)
        save_csv_user(csv_users)
        SendManager().update_csv()
        ret = {
            'use_time_sec': round(time.time() - start, 3),
            'user_count': count,
            'csv_mails': ids,
        }
        return render(request, "list.html", context=ret)
    else:
        return render(request, 'send_email_csv.html')


@login_required(login_url='/login/')
def query_send_info(request):
    if request.method == 'POST':
        try:
            ret = query_send(request)
            #print(ret)
            return render(request, 'list.html', ret)
        except KeyError:
            return HttpResponse('Please fill in all fields')
    else:
        return render(request, 'query_send_info.html')


@login_required(login_url='/login/')
def delete_sending(request):
    if request.method == 'POST':
        try:
            ret = delete_send(request)
            return render(request, 'list.html', ret)
        except KeyError:
            return HttpResponse('Please fill in all fields')
    else:
        return render(request, 'query_send_info.html')


@login_required(login_url='/login/')
def delete_unsub_users(request):
    if request.method == 'POST':
        try:
            sid = request.POST['email']
            if sid:
                UnsubscribeUsers.objects.using(PRODUCT).filter(email=sid).delete()
            ret = query_unsubscribe_users()
            return render(request, 'list.html', ret)
        except KeyError:
            return HttpResponse('Please fill in all fields')
    else:
        return render(request, 'query_send_info.html')

@login_required(login_url='/login/')
def show_sending(request):
    if request.method == 'POST':
        try:
            sid = int(request.POST['id'])
            if sid > 0:
                send = SendingQueue.objects.using(PRODUCT_RO).filter(id=sid).first()
                if send:
                    html_str = get_html_from_file(send.html_str)
                    return HttpResponse(html_str)
            return render(request, 'query_send_info.html')
        except KeyError:
            return HttpResponse('Please fill in all fields')
    else:
        return render(request, 'query_send_info.html')


@login_required(login_url='/login/')
def query_send_stat(request):
    if request.method == 'POST':
        send_id = request.POST['send_id']
        # if not isinstance(send_id, int):
        #     return HttpResponse('Please fill in a number')
        ret = query_stat(send_id)
        if 'stat' in ret:
            return download_stat_csv(ret['stat'], send_id)
        return render(request, 'query_send_stat.html')
    else:
        return render(request, 'query_send_stat.html')


#@login_required(login_url='/login/')
def download_stat_csv(stat, send_id):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    file_name = "dragon_sender_stat_%s.csv" % send_id
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    writer = csv.writer(response)
    writer.writerow(['user_id', 'opened', 'clicked'])
    for u in stat:
        writer.writerow([u['user_id'], u['opened'], u['clicked']])

    return response


def query_unsub_users(request):
    if request.method == 'POST':
        try:
            ret = query_unsubscribe_users()
            return render(request, 'list.html', ret)
        except KeyError:
            return HttpResponse('Error on querying unsubscribe users')
    else:
        return render(request, 'query_send_info.html')

@login_required(login_url='/login/')
def get_unsub_user_by_id(request):
    if request.method == 'POST':
        try:
            start = time.time()
            sid = request.POST.get('user_id', '')
            if sid != '':
                sid = int(sid)
            else:
                sid = 0
            if sid > 0:
                users = UnsubscribeUsers.objects.using(PRODUCT_RO).values("user_id", "email", "reason").filter(user_id=sid)
            else:
                users = UnsubscribeUsers.objects.using(PRODUCT_RO).values("user_id", "email", "reason").order_by('-id')[:100]
            user_count = len(users)
            if user_count > 0:
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
                return render(request, 'list.html', ret)
            return HttpResponse('Error on your user id')
        except KeyError:
            return HttpResponse('Error on get unsub user by id')
    else:
        return render(request, 'query_send_info.html')



@login_required(login_url='/login/')
def query_csv_users(request):
    if request.method == 'POST':
        try:
            ret = query_all_csv_users()
            return render(request, 'list.html', ret)
        except KeyError:
            return HttpResponse('Error on querying csv users')
    else:
        return render(request, 'query_send_info.html')


@login_required(login_url='/login/')
def get_send_result_by_ct(request):
    if request.method == 'POST':
        try:
            content_title = request.POST.get('content_title', '')
            results = []
            if content_title != '':
                send_result = SendResult.objects.using(PRODUCT_RO).values("send_id", "content_title", "status",
                                                                          "delivery", "sent", "bounce", "opened",
                                                                          "clicked", "start_ts", "finish_ts",
                                                                          "last_update_ts").filter(
                    Q(content_title__icontains=content_title))
            else:
                send_result = SendResult.objects.using(PRODUCT_RO).values("send_id", "content_title", "status",
                                                                          "delivery", "sent", "bounce", "opened",
                                                                          "clicked", "start_ts", "finish_ts",
                                                                          "last_update_ts").order_by('id').desc[:100]
            if len(send_result) > 0:
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
                send_results = results[::-1]
                start = time.time()
                SendManager().update_sending()
                sending_list, _ = SendManager().get_send_info()
                ret = {
                    'use_time_sec': round(time.time() - start, 3),
                    'user_count': 0,
                    'sending': sending_list,
                    'send_result': send_results
                }
                return render(request, 'list.html', ret)
            return HttpResponse('Error on content title')
        except KeyError:
            return HttpResponse('Error on get send result by content title')
    else:
        return render(request, 'query_send_info.html')

@login_required(login_url='/login/')
def unsub_users_to_csv(request):
    if request.method == 'POST':
        try:
            users = UnsubscribeUsers.objects.using(PRODUCT_RO).values("user_id", "email", "reason").all()
            unsub_users = []
            for u in users:
                unsub_users.append({
                    'user_id': u['user_id'],
                    'email': u['email'],
                    'reason': u['reason'],
                })
                user_list = []
                email_list = []
                reason_list = []
                try:
                    if unsub_users:
                        for u in unsub_users:
                            user_list.append(u['user_id'])
                            reason_list.append(u['reason'])
                            if u['email'] != '':
                                email = eval(u['email'])
                                if 'email' in email:
                                    email_list.append(email.get('email'))
                                else:
                                    email_list.append('')
                            else:
                                email_list.append('')
                except KeyError:
                    return HttpResponse('Error on unsub users to csv')
                data = {
                    'user': user_list,
                    'email': email_list,
                    'reason': reason_list,
                }
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Unsubscribe_users.csv"'
                writer = csv.writer(response)
                writer.writerow(data.keys())
                for row in zip(*data.values()):
                    writer.writerow(row)
                return response
        except KeyError:
            return HttpResponse('Error on unsub users to csv')
    else:
        return render(request, 'query_send_info.html')


@login_required(login_url='/login/')
def manage_segments(request):
    seg_search = ''
    if request.method == "POST":
        seg_name = request.POST.get('name', '')
        seg_search = request.POST.get('seg_search', '')
        if seg_name:
            try:
                gm_name = request.user.get_username()
                condition_type_list = request.POST.getlist('condition_type_list', [])
                condition_type_list = to_num_list(condition_type_list)
                condition_list = []
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

                csv_users = []
                csv_file = request.FILES.get('csv_file', None)
                if csv_file:
                    file_data = csv_file.read().decode("utf-8-sig")
                    rows = csv.DictReader(io.StringIO(file_data), delimiter=',')
                    for row in rows:
                        csv_users.append(int(row["id"]))
                if condition_list:
                    conditions = json.dumps(condition_list)
                    send = Segment(name=seg_name, conditions=conditions, gm_name=gm_name)
                    send.save(using=PRODUCT)
                elif csv_users:
                    csv_users = json.dumps(csv_users)
                    send = Segment(name=seg_name, csv_users=csv_users, gm_name=gm_name)
                    send.save(using=PRODUCT)
                return redirect('/manage_segments/')
            except KeyError:
                return HttpResponse('fill in all fields!!')

    ret = query_segments(seg_search)
    return render(request, 'manage_segments.html', ret)


@login_required(login_url='/login/')
def delete_segment(request):
    if request.method == 'POST':
        try:
            sid = request.POST['seg_id']
            if sid:
                Segment.objects.using(PRODUCT).filter(id=sid).delete()
        except KeyError:
            return HttpResponse('lack of segment id')
    ret = query_segments()
    return render(request, 'manage_segments.html', ret)


@login_required(login_url='/login/')
def send_email_segment(request):
    if request.method == 'POST':
        select1 = request.POST['select1']
        select2 = request.POST['select2']
        if select1:
            extra = {'seg_1': int(select1)}
            if select2:
                extra['seg_2'] = int(select2)
            build_sending_queue(request, extra=extra)
        return redirect('/query_send_info/')
    else:
        ret = query_segments()
        return render(request, 'send_email_segment.html', ret)


@login_required(login_url='/login/')
def manage_templates(request):
    ret = query_manage_template()
    return render(request, 'manage_template.html', ret)


@login_required(login_url='/login/')
def create_template(request):
    if request.method == "POST":
        template_name = request.POST.get('template_name', '')
        if template_name:
            gm_name = request.user.get_username()
            template_type = request.POST.get('template_type', '')
            subject_part = request.POST.get('subject','')
            html_part = request.FILES.get('html_part', None)
            if html_part:
                create_ts = datetime.datetime.now()
                send = SesTemplate(template_name=template_name,template_type=template_type,subject_part=subject_part,gm_name=gm_name,create_ts=create_ts,last_update_ts=create_ts)
                send.save(using=PRODUCT)
                create_ses_template(template_name, subject_part, template_type, html_part)
            ret = query_manage_template(template_name)
        else:
            ret = query_manage_template()
    else:
        ret = query_manage_template()
    return render(request, 'manage_template.html', ret)


@login_required(login_url='/login/')
def search_template(request):
    if request.method == "POST":
        template_name = request.POST.get('template_name', '')
        if template_name:
            ret = query_manage_template(template_name)
        else:
            ret = query_manage_template()
    else:
        ret = query_manage_template()
    return render(request, 'manage_template.html', ret)


@login_required(login_url='/login/')
def show_html(request):
    if request.method == "POST":
        template_name = request.POST.get('template_name', '')
        response = get_ses_template(template_name)
        template_data = response['Template']

        # 定义渲染模板所需的数据
        context = {
            'subject': template_data['SubjectPart'],
            'html': template_data['HtmlPart'],
        }

        # 加载并渲染模板
        jinja_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
          <title>{{ subject }}</title>
        </head>
        <body>
          {{ html }}
        </body>
        </html>
        """)
        rendered_html = jinja_template.render(context)
        print(rendered_html)


@login_required(login_url='/login/')
def edit_template(request):
    if request.method == "POST":
        template_name = request.POST.get('template_name', '')
        ret = query_manage_template(template_name)
        return render(request, 'edit_template.html', ret)


@login_required(login_url='/login/')
def update_template(request):
    if request.method == "POST":
        template_name = request.POST.get('template_name', '')
        if template_name:
            gm_name = request.user.get_username()
            template_type = request.POST.get('template_type', '')
            subject_part = request.POST.get('subject','')
            html_part = request.FILES.get('html_part', None)
            id = request.POST.get('id', 0)
            if html_part:
                create_ts = datetime.datetime.now()
                send = SesTemplate(id=id,template_name=template_name,template_type=template_type,subject_part=subject_part,gm_name=gm_name,create_ts=create_ts,last_update_ts=create_ts)
                send.save(using=PRODUCT)
                update_ses_template(template_name, subject_part, template_type, html_part)
            ret = query_manage_template(template_name)
        else:
            ret = query_manage_template()
    else:
        ret = query_manage_template()
    return render(request, 'manage_template.html', ret)


@login_required(login_url='/login/')
def delete_template(request):
    if request.method == "POST":
        template_name = request.POST.get('template_name', '')
        if template_name:
            delete_ses_template(template_name)
            SesTemplate.object.using(PRODUCT).filter(template_name=template_name).delete()
    ret = query_manage_template()
    return render(request, 'manage_template.html', ret)