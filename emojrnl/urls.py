"""emojrnl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
"""
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib import admin

from journal.api import JournalViewSet

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='user-view'),
    url(r'^api/journal/(?P<hashid>[\w]{12})/$', JournalViewSet.as_view(), name='journal-view'),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^sms/', include('sms.urls', namespace='sms')),
]
