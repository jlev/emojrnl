from __future__ import unicode_literals

from django.apps import AppConfig


class JournalConfig(AppConfig):
    name = 'journal'

    def ready(self):
        import journal.signals
