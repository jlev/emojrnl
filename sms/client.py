import logging
logger = logging.getLogger(__name__)

from django.conf import settings

import plivo
PLIVO = plivo.RestAPI(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)


def send_sms(to, msg):
    if not to.startswith('+'):
        to = '+' + to

    params = {
        'src': settings.PLIVO_NUMBER,
        'dst': to,
        'text': msg
    }
    response = PLIVO.send_message(params)
    logger.info('send_sms: %s, %s' % (params, response))
    return response[0] is 202


def parse_sms(request):
    # TODO, validate request actually comes from Plivo

    params = ()
    if request.method == "POST":
        params = (request.POST.get('From'), request.POST.get('Text').strip())
    elif request.method == "GET":
        params = (request.GET.get('From'), request.GET.get('Text').strip())

    logger.info('parse_sms: %s' % (params,))
    return params
