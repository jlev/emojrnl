from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from datetime import timedelta
from journal.models import Journal, Entry, Streak
from journal import tasks
import logging
logger = logging.getLogger(__name__)


schedule_reminder = Signal(providing_args=['hashid', ])
schedule_stop = Signal(providing_args=['hashid', ])


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


@receiver(schedule_reminder, sender=Journal)
def set_reminder_schedule(hashid, **kwargs):
    logger.info('set_reminder_schedule: %s' % hashid)
    tasks.schedule_daily_prompt(hashid)


@receiver(schedule_stop, sender=Journal)
def stop_reminder_schedule(hashid, **kwargs):
    logger.info('stop_reminder_schedule: %s' % hashid)
    tasks.schedule_stop(hashid)
