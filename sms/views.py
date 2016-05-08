import random
from twilio import twiml
from datetime import datetime
import logging

from django_twilio.decorators import twilio_view
from django_twilio.request import decompose
from django.conf import settings
from django.http import JsonResponse

from journal.models import Journal, Entry, HASHER
from sms.emoji import EMOJI, WELCOME_PROMPTS, THANKS_MESSAGES

logger = logging.getLogger(__name__)


def user_signup(request, phone_number):
    logger.info("user_signup: " + phone_number)
    if Journal.objects.from_phone_number(phone_number) is None:
        journal = create_journal(phone_number, send_response=False)
        sms_response = twiml.Response()
        sms_response.message(msg=u"Welcome to emojr.nl!" +
                             u"\n Reply with %(thumbs_up)s to sign up for your own %(sweat_face)s %(journal)s" % EMOJI,
                             to=phone_number,
                             sender=settings.TWILIO_NUMBER)
        return JsonResponse({'created': journal.hashid})
    else:
        return JsonResponse({'exists': phone_number})


def create_journal(phone_number, send_response=True):
    logger.info("create_journal: " + phone_number)
    hashid = HASHER.encode(int(phone_number))
    journal = Journal.objects.create(hashid=hashid, last_updated=datetime.now())

    if send_response:
        response = twiml.Response()
        response.message(msg=random.choice(WELCOME_PROMPTS) + u"\nReply to make your first post. How's it going today?",
                         to=journal.get_phone(),
                         sender=settings.TWILIO_NUMBER)
        return response
    else:
        return journal


def new_entry(journal, txt, send_response=True):
    entry = Entry.objects.create(txt=txt, journal=journal)

    if send_response:
        response = twiml.Response()
        response.message(msg=random.choice(THANKS_MESSAGES),
                         to=journal.get_phone(),
                         sender=settings.TWILIO_NUMBER)
        return response
    else:
        return entry


@twilio_view
def sms_entry(request):
    # try to fake out the request.is_ajax method, so we send twilio better error messages
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

    try:
        response = twiml.Response()
        twilio_request = decompose(request)
        try:
            journal = Journal.objects.from_phone_number(twilio_request.from_)
            logger.info("got journal for " + twilio_request.from_)
            if journal.confirmed:
                logger.info("new_entry:" + twilio_request.body)
                return new_entry(journal, twilio_request.body)

            else:
                # user needs confirmation step
                # check to see if response is thumbs_up
                if twilio_request.body.startswith(EMOJI['thumbs_up']):
                    logger.info("journal confirmed, user welcome")
                    journal.confirmed = True
                    journal.save()
                    response.message(msg=random.choice(WELCOME_PROMPTS) +
                                 u"\nWelcome to your %(sweat_face)s %(journal)s!" % EMOJI,
                             to=journal.get_phone(),
                             sender=settings.TWILIO_NUMBER)
                    return response
                else:
                    logger.info("journal not confirmed, user signup")
                    return user_signup(request, journal.get_phone())

        except Journal.DoesNotExist:
            logger.info("could not get journal for " + twilio_request.from_)
            create_journal(twilio_request.from_, send_response=False)
            new_entry(journal, twilio_request.body, send_response=False)
            response.message(msg=random.choice(WELCOME_PROMPTS) +
                                 u"\nWelcome to your %(sweat_face)s %(journal)s!" % EMOJI,
                             to=journal.get_phone(),
                             sender=settings.TWILIO_NUMBER)
            return response

    except Exception, e:
        logger.exception(e)
        import traceback
        return JsonResponse({'traceback': traceback.format_exc()})
