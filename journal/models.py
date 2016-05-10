from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from hashids import Hashids
HASHER = Hashids(min_length=12, salt=settings.SECRET_KEY)


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
    view_password = models.CharField(max_length=5)
    objects = HashedPhoneManager()

    def __unicode__(self):
        return self.hashid

    @property
    def num_entries(self):
        return self.entry_set.count()

    def get_phone(self):
        return str(HASHER.decode(self.hashid)[0])

    def get_absolute_url(self):
        return "%s#%s" % (reverse('user-view'), self.hashid)


class Entry(models.Model):
    journal = models.ForeignKey(Journal)
    created_at = models.DateTimeField(auto_now_add=True)
    txt = models.CharField(max_length=3)

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
