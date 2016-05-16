from emojrnl.emoji import EMOJI

WELCOME_MSG = u"%(fireworks)s%(champagne)s%(party_popper)s" % EMOJI
CONFIRM_MSGS = [EMOJI[m] for m in [
    'thumbs_up',
    'ok_hand',
    'vulcan_salute',
    'dog_face',
    'cat_face',
    'spouting_whale',
    'shamrock',
    'donut',
    'trophy',
    'military_medal',
    'sports_medal',
    'camera_with_flash',
    'balloon'
]]

PROMPT_MSGS = [
    u"how was today %(grey_question)s" % EMOJI,
    u"%(wave)s how's it going?" % EMOJI,
    u"how are you doing %(thinking_face)s" % EMOJI,
]
