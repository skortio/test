from django.urls import path, re_path

from django_ses.views import DashboardView

app_name='django_ses'
urlpatterns = [
    re_path(r'^$', DashboardView.as_view(), name='django_ses_stats'),
    #path('', DashboardView.as_view(), name='django_ses_stats'),
]
