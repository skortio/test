
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, re_path, path

from django_ses.views import SESEventWebhookView, handle_bounce
from sender import views

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #re_path(r'^admin/', include(admin.site.urls)),
    path('admin/', admin.site.urls),

    path('login/', views.normal_login, name='login'),
    path('logout/', views.normal_logout, name='logout'),
    re_path('^unsubscribe/([0-9]{1,10})/$', views.unsubscribe, name='unsubscribe'),
    re_path(r'^$', views.index, name='index'),
    re_path(r'^query_user_info/$', views.query_user_info, name='query_user_info'),
    re_path(r'^unsub_user$', views.unsub_user, name='unsub_user'),
    re_path(r'^send_email_text/$', views.send_email_text, name='send_email_text'),
    re_path(r'^send_email_html/$', views.send_email_html, name='send_email_html'),
    re_path(r'^send_email_csv/$', views.send_email_csv, name='send_email_csv'),
    re_path(r'^send_email_batch/$', views.send_email_batch, name='send_email_batch'),
    re_path(r'^query_send_info/$', views.query_send_info, name='query_send_info'),
    re_path(r'^query_send_stat/$', views.query_send_stat, name='query_send_stat'),
    re_path(r'^delete_sending/$', views.delete_sending, name='delete_sending'),
    re_path(r'^show_sending/$', views.show_sending, name='show_sending'),
    re_path(r'^reporting/', include('django_ses.urls', namespace='django_ses')),
    re_path(r'^query_unsub_users/$', views.query_unsub_users, name='query_unsub_users'),
    re_path(r'^query_csv_users/$', views.query_csv_users, name='query_csv_users'),
    re_path(r'^query_user_summary/$', views.query_user_summary, name='query_user_summary'),
    re_path(r'^bounce/', handle_bounce, name='handle_bounce'),       # Deprecated, see SESEventWebhookView.
    re_path(r'^event-webhook/', SESEventWebhookView.as_view(), name='event_webhook'),
    re_path(r'^delete_unsub_users/', views.delete_unsub_users, name='delete_unsub_users'),
    re_path(r'^get_unsub_user_by_id/', views.get_unsub_user_by_id, name='get_unsub_user_by_id'),
    re_path(r'^get_send_result_by_ct/', views.get_send_result_by_ct, name='get_send_result_by_ct'),
    re_path(r'^unsub_users_to_csv/', views.unsub_users_to_csv, name='unsub_users_to_csv'),
    re_path(r'^manage_segments/$', views.manage_segments, name='manage_segments'),
    re_path(r'^send_email_segment/$', views.send_email_segment, name='send_email_segment'),
    re_path(r'^delete_segment/', views.delete_segment, name='delete_segment')
]

urlpatterns += staticfiles_urlpatterns()
