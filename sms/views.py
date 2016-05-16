import random
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from emojrnl.emoji import EMOJI
from journal.models import Journal, Entry, HASHER
from journal.signals import schedule_reminder, schedule_stop
from sms.client import send_sms, parse_sms
from sms.messages import WELCOME_MSG, CONFIRM_MSGS, PROMPT_MSGS


@csrf_exempt
def user_signup(request, phone_number):
    logger.info("user_signup: %s" % phone_number)
    journal = Journal.objects.from_phone_number(phone_number)
    if journal is None:
        journal = create_journal(phone_number)
        send_sms(to=phone_number,
                 msg=u"Welcome to emojr.nl!\n" +
                     u"Reply with %(thumbs_up)s to sign up for your own %(emojrnl)s" % EMOJI,
                 )
        return JsonResponse({'message': 'create'})
    elif not journal.confirmed:
        send_sms(to=journal.get_phone(),
                 msg=u"Welcome to emojr.nl!\n" +
                     u"Reply with %(thumbs_up)s to sign up for your own %(emojrnl)s" % EMOJI,
                 )
        return JsonResponse({'message': 'confirm'})
    else:
        return JsonResponse({'message': 'exists', 'hashid': journal.hashid})


def create_journal(phone_number, send_response=False):
    logger.info("create_journal: %s" % phone_number)
    hashid = HASHER.encode(int(phone_number))
    journal = Journal.objects.create(hashid=hashid, last_updated=datetime.now())
    if send_response:
        send_sms(to=journal.get_phone(),
                 msg=WELCOME_MSG + u"\n"
                     + u"Reply to make your first post on http://my.emojr.nl/#%s" % journal.hashid
                 )
    return JsonResponse({'journal': journal.hashid})


def new_entry(journal, txt, send_response=False, response_message=None):
    entry = Entry.objects.create(txt=txt, journal=journal)
    logger.info("new_entry: %s" % entry)
    if send_response:
        if not response_message:
            response_message = random.choice(CONFIRM_MSGS)
        send_sms(to=journal.get_phone(),
                 msg=response_message)

    return JsonResponse({'journal': entry.journal.hashid,
                         'entry': entry.created_at})


def send_prompt(hashid):
    journal = Journal.objects.get(hashid=hashid)
    status = send_sms(to=journal.get_phone(),
                      msg=random.choice(PROMPT_MSGS)
                      )
    logger.info("send_prompt: %s, %s" % (journal.hashid, status))
    return status


@csrf_exempt
def sms_post(request):
    # try to fake out the request.is_ajax method, so we send caller better error messages
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

    try:
        (sms_from, sms_body) = parse_sms(request)
        try:
            journal = Journal.objects.from_phone_number(sms_from)
            logger.info("got journal: %s" % sms_from)
            if journal and journal.confirmed:
                # COMMANDS FIRST
                if sms_body.upper() == 'STOP':
                    # stop scheduled prompts
                    logger.info('stop_schedule')
                    schedule_stop.send(sender=Journal, hashid=journal.hashid)
                    send_sms(to=sms_from, msg=u"OK, no more %(emojrnl)s reminders\n%(bow)s." % EMOJI)
                    return JsonResponse({'message': 'schedule_stop',
                                        'journal': journal.hashid})
                else:
                    # DEFAULT, new entry
                    if journal.entry_set.count() == 0:
                        # first post!
                        logger.info("first_post: %s" % journal.hashid)
                        return new_entry(journal, sms_body, send_response=True, response_message=WELCOME_MSG)
                    else:
                        logger.info("new_entry: %s" % sms_body)
                        return new_entry(journal, sms_body, send_response=False)
            else:
                # user needs confirmation step
                # check to see if response is thumbs_up
                if sms_body.startswith(EMOJI['thumbs_up']):
                    logger.info("journal confirmed, user welcome")
                    journal.confirmed = True
                    journal.save()
                    schedule_reminder.send(sender=Journal, hashid=journal.hashid)
                    send_sms(to=sms_from,
                             msg=u"Welcome to your %(emojrnl)s!\n" % EMOJI +
                                 u"Read it at http://my.emojr.nl/#%s" % journal.hashid
                             )
                    send_sms(to=sms_from,
                             msg=u"You'll get reminders every afternoon, reply with emoji to post. " +
                                 u"You can STOP any time.")
                    return JsonResponse({'message': 'welcome',
                                        'journal': journal.hashid})
                else:
                    logger.info("journal not confirmed, user signup")
                    return user_signup(request, sms_from)

        except Journal.DoesNotExist:
            logger.info("could not get journal for %s" % sms_from)
            send_sms(to=sms_from,
                     msg=u"Hi, it's %(emojrnl)s!" % EMOJI +
                         u"Create your own at http://emojr.nl/"
                     )
            return JsonResponse({'message': 'signup'})

    except Exception, e:
        logger.exception(e)
        import traceback
        return JsonResponse({'traceback': traceback.format_exc()})
