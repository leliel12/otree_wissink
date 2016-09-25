
import random



from django.views.decorators.http import require_POST

from django.conf import settings
from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


# =============================================================================
# FUNCTIONS
# =============================================================================

def vars_for_all_templates(page):
    return {
        "p": Constants.p,
        "warning_time": 2,
        "kick_time": 5,
        "DEBUG": settings.DEBUG,
        "because_debug": "<small>DEBUG is True</small>"}


# =============================================================================
# COMMON VIEWS
# =============================================================================

@require_POST
def kick_player(request):
    session_code = request.POST["session"]
    player_id = request.POST["player"]
    import ipdb; ipdb.set_trace()


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


class PhasesDescription(Page):
    pass


class ComprehensionCheck(Page):

    form_model = models.Player
    form_fields = [
        "cq{}".format(idx)
        for idx in range(len(Constants.comprehension_questions))]

    def error_message(self, values):
        msg = []
        for k, v in values.items():
            idx = int(k.replace("cq", ""))
            q = Constants.comprehension_questions[idx]
            if not q.is_correct(v):
                msg.append("{} are incorrect".format(q.question))
        return msg


class PossitionAssignment(Page):
    pass


class WaitPossitionAssignment(WaitPage):

    title_text = "Possition Assignment"
    body_text = "Wait until all asignment are done"

    def after_all_players_arrive(self):
        players = [p for p in self.group.get_players() if not p.kicked]
        random.shuffle(players)
        while players:
            if len(players) >= 3:
                players.pop().position = Constants.pA
                players.pop().position = Constants.pB
                players.pop().position = Constants.pC
            else:
                break
        for player in players:
            player.position = Constants.leftOver


page_sequence = [
    InformedConsent,
    Instructions1, Instructions2, Instructions3, Instructions4,
    PhasesDescription, ComprehensionCheck,
    PossitionAssignment, WaitPossitionAssignment
]
