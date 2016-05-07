import random
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from journal.models import Journal, Entry, HASHER
from sms.emoji import EMOJI, WELCOME_PROMPTS, THANKS_MESSAGES
from sms.client import send_sms, parse_sms


def user_signup(phone_number):
    logger.info("user_signup: " + phone_number)
    journal = Journal.objects.from_phone_number(phone_number)
    if journal is None:
        journal = create_journal(phone_number, send_response=False)
        send_sms(to=phone_number,
                 msg=u"Welcome to emojr.nl!" +
                     u"\n Reply with %(thumbs_up)s to sign up for your own %(sweat_face)s %(journal)s" % EMOJI,
                 )
        return JsonResponse({'message': 'create'})
    elif not journal.confirmed:
        send_sms(to=journal.get_phone(),
                 msg=u"Welcome to emojr.nl!" +
                     u"\n Reply with %(thumbs_up)s to sign up for your own %(sweat_face)s %(journal)s" % EMOJI,
                 )
        return JsonResponse({'message': 'confirm'})
    else:
        return JsonResponse({'message': 'exists'})


def create_journal(phone_number, send_response=True):
    logger.info("create_journal: " + phone_number)
    hashid = HASHER.encode(int(phone_number))
    journal = Journal.objects.create(hashid=hashid, last_updated=datetime.now())
    if send_response:
        send_sms(to=journal.get_phone(),
                 msg=random.choice(WELCOME_PROMPTS) + u"\n"
                     + u"Reply to make your first post. How's it going today?"
                 )
    return JsonResponse({'journal': journal.hashid})


def new_entry(journal, txt, send_response=True):
    entry = Entry.objects.create(txt=txt, journal=journal)
    if send_response:
        send_sms(to=journal.get_phone(),
                 msg=random.choice(THANKS_MESSAGES)
                 )

    return JsonResponse({'journal': entry.journal.hashid,
                         'entry': entry.created_at})


@csrf_exempt
def sms_post(request):
    # try to fake out the request.is_ajax method, so we send twilio better error messages
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

    try:
        (sms_from, sms_body) = parse_sms(request)
        try:
            journal = Journal.objects.from_phone_number(sms_from)
            logger.info("got journal for " + sms_from)
            if journal and journal.confirmed:
                logger.info("new_entry:" + sms_body)
                return new_entry(journal, sms_body)

            else:
                # user needs confirmation step
                # check to see if response is thumbs_up
                if sms_body.startswith(EMOJI['thumbs_up']):
                    logger.info("journal confirmed, user welcome")
                    journal.confirmed = True
                    journal.save()
                    send_sms(to=sms_from,
                             msg=random.choice(WELCOME_PROMPTS) + u"\n" +
                                 u"Welcome to your %(sweat_face)s %(journal)s!" % EMOJI)
                    return JsonResponse({'message': 'welcome',
                                        'journal': journal.hashid})
                else:
                    logger.info("journal not confirmed, user signup")
                    return user_signup(sms_from)

        except Journal.DoesNotExist:
            logger.info("could not get journal for " + sms_from)
            journal = create_journal(sms_from, send_response=False)
            entry = new_entry(journal, sms_body, send_response=False)
            send_sms(to=journal.get_phone(),
                     msg=random.choice(WELCOME_PROMPTS) + u"\n" +
                         u"Welcome to your %(sweat_face)s %(journal)s!" % EMOJI
                     )
            return JsonResponse({'message': 'welcome',
                                 'journal': journal.hashid,
                                 'entry': entry.created_at})

    except Exception, e:
        logger.exception(e)
        import traceback
        return JsonResponse({'traceback': traceback.format_exc()})
