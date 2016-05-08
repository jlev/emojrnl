from django.conf.urls import url

from sms.views import user_signup, sms_entry

urlpatterns = [
    url(r'^signup/(?P<phone_number>[\d]{10,14})/?$', user_signup),
    url(r'^entry/$', sms_entry),
]
