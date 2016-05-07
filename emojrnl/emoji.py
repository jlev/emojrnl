from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

from emoji.unicode_codes import EMOJI_ALIAS_UNICODE

EMOJI = {k.replace(':', ''): v for k, v in EMOJI_ALIAS_UNICODE.items()}
# convert :alias: style to simpler dict keys
logger.info('Powered by %d emoji' % len(EMOJI.keys()))

# define our own aliases
EMOJI[u'thumbs_up'] = EMOJI[u'thumbs_up_sign']
EMOJI[u'champagne'] = EMOJI[u'bottle_with_popping_cork']
EMOJI[u'donut'] = EMOJI[u'doughnut']
EMOJI[u'vulcan_salute'] = u"\U0001F596"
EMOJI[u'emojrnl'] = u"%(sweat_smile)s%(notebook)s" % EMOJI
