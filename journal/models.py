from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from hashids import Hashids
HASHER = Hashids(min_length=12,
                 alphabet='abcdefghijklmnopqrstuvwxyz',
                 salt=settings.SECRET_KEY)


class HashedPhoneQuerySet(models.QuerySet):
    def from_phone_number(self, phone_number):
        # TODO: parse phone_number to e164
        hashid = HASHER.encode(int(phone_number))
        return self.filter(hashid=hashid).first()
HashedPhoneManager = models.Manager.from_queryset(HashedPhoneQuerySet)


class Journal(models.Model):
    hashid = models.CharField(max_length=12, unique=True, db_index=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField()
    view_password = models.CharField(max_length=5, null=True)
    objects = HashedPhoneManager()

    def __unicode__(self):
        return self.hashid

    @property
    def num_entries(self):
        return self.entry_set.count()

    def longest_streak(self):
        #  do filtering in memory
        #  TODO, use F() query
        if self.streak_set.count():
            return sorted(list(self.streak_set.all()), key=lambda x: x.length, reverse=True)[0]

    def current_streak(self):
        if self.streak_set.count():
            return self.streak_set.filter(date_end=datetime.now().date()).first()

    def get_phone(self):
        return str(HASHER.decode(self.hashid)[0])

    def get_absolute_url(self):
        return "%s#%s" % (reverse('user-view'), self.hashid)


class Entry(models.Model):
    journal = models.ForeignKey(Journal)
    created_at = models.DateTimeField(auto_now_add=True)
    txt = models.CharField(max_length=5)

    def __unicode__(self):
        return "%s - %s" % (self.created_at, self.txt)

    @property
    def hashid(self):
        return self.journal.hashid

    class Meta:
        verbose_name_plural = "entries"
        ordering = ['-created_at']


class Streak(models.Model):
    journal = models.ForeignKey(Journal)
    date_start = models.DateField()
    date_end = models.DateField()

    def __unicode__(self):
        return "%s - %s" % (self.date_start, self.date_end)

    @property
    def length(self):
        return (self.date_end - self.date_start).days + 1
