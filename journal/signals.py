from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from journal.models import Entry, Streak


@receiver(post_save, sender=Entry)
def mark_streaks(sender, **kwargs):
    entry = kwargs['instance']
    today = entry.created_at.date()
    yesterday = today + timedelta(-1)
    journal = entry.journal

    yesterday_entries = Entry.objects.filter(journal=journal, created_at__date=yesterday)
    if yesterday_entries.count() > 0:
        try:
            streak = Streak.objects.get(journal=journal, date_end=yesterday)
        except Streak.DoesNotExist:
            streak = Streak(journal=journal, date_start=yesterday)
        finally:
            streak.date_end = today
            streak.save()
