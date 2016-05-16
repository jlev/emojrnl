from django_q.models import Schedule
import arrow
import random


def schedule_daily_prompt(hashid):
    # don't use get_or_create, because we don't want to save until we set kwargs
    try:
        s = Schedule.objects.get(func='sms.views.send_prompt', name='%s-prompt' % hashid)
    except Schedule.DoesNotExist:
        s = Schedule(func='sms.views.send_prompt', name='%s-prompt' % hashid)

    s.kwargs = {'hashid': hashid}
    s.schedule_type = Schedule.DAILY  # every day
    hour = 12 + random.randint(3, 5)  # choose random time in afternoon (between 3 and 5 pm)
    minute = random.randint(0, 60)  # randomize minute
    current_time = arrow.now('US/Pacific')  # TODO, schedule in journal local TZ
    s.next_run = current_time.replace(day=current_time.day + 1, hour=hour, minute=minute).datetime

    s.repeats = -1  # repeat forever
    # s.hook = 'journal.shuffle_prompt_time'
    # TODO, re-shuffle prompt time on hook?
    s.save()


def schedule_stop(hashid):
    s = Schedule.objects.filter(func='sms.views.send_prompt', name='%s-prompt' % hashid)
    s.delete()
