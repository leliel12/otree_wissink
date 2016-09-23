
from django.conf import settings
from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


def vars_for_all_templates(page):
    return {
        "params": Constants.params,
        "DEBUG": settings.DEBUG,
        "because_debug": "<small>DEBUG is True</small>"}


# =============================================================================
# VIEWS
# =============================================================================

class InformedConsent(Page):
    timeout_seconds = 15 * 60

    def vars_for_template(self):
        return {"wait": "{}:00 minutes".format(int(self.timeout_seconds/60))}


class Instructions1(Page):
    pass

class Instructions2(Page):
    pass

class Instructions3(Page):
    pass

class Instructions4(Page):
    pass




page_sequence = [
    InformedConsent,
    Instructions1, Instructions2, Instructions3, Instructions4,
]
