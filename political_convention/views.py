
import random
import itertools as it

from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse

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
        "warning_time": Constants.p.get(page.warning_time),
        "kick_time": Constants.p.get(page.kick_time),
        "DEBUG": settings.DEBUG,
        "because_debug": "<small>DEBUG is True</small>",
        "kick_warning": False}


# =============================================================================
# COMMON VIEWS
# =============================================================================

@require_POST
def kick_player(request):
    session_code = request.POST["session"]
    player_id = request.POST["player"]
    secret_key = request.POST["secret_key"]
    player = models.Player.objects.filter(
        session__code=session_code).get(id=player_id)
    if player and player.secret_key == secret_key:
        for p in player.participant.get_players():
            p.kicked = True
            p.save()
        return JsonResponse({"kicked": True})
    return JsonResponse({"kicked": False})


# =============================================================================
# VIEWS
# =============================================================================

class InformedConsent(Page):
    timeout_seconds = 15 * 60
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked

    def vars_for_template(self):
        return {"wait": "{}:00 minutes".format(int(self.timeout_seconds/60))}


class Instructions1(Page):
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked


class Instructions2(Page):
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked


class Instructions3(Page):
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked


class Instructions4(Page):
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked


class PhasesDescription(Page):
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked


class ComprehensionCheck(Page):
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    form_model = models.Player
    form_fields = [
        "cq{}".format(idx)
        for idx in range(len(Constants.comprehension_questions))]

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked

    def error_message(self, values):
        msg = []
        for k, v in values.items():
            idx = int(k.replace("cq", ""))
            q = Constants.comprehension_questions[idx]
            if not q.is_correct(v):
                msg.append("{} are incorrect".format(q.question))
        return msg


class PossitionAssignment(Page):
    warning_time = "seconds_before_idle_warning_instruction"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return self.subsession.round_number == 1 and not self.player.kicked


class WaitPossitionAssignment(WaitPage):
    title_text = "Possition Assignment"
    body_text = "Wait until all asignment are done"
    wait_for_all_groups = True

    warning_time = None
    kick_time = None

    def after_all_players_arrive(self):
        pas, pbs, pcs, kicked = self.subsession.players_by_position()

        random.shuffle(pas)
        random.shuffle(pbs)
        random.shuffle(pcs)
        group_matrix = []
        for a, b, c in it.zip_longest(pas, pbs, pcs):
            row = []
            if a:
                row.append(a)
            if b:
                row.append(b)
            if c:
                row.append(c)
            if row:
                group_matrix.append(row)
        if kicked:
            group_matrix.append(kicked)
        self.subsession.set_group_matrix(group_matrix)


class PositionAssignmentResult(Page):
    warning_time = "seconds_before_idle_warning_game_1"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def vars_for_template(self):
        others = self.player.get_others_in_group()
        others.sort(key=lambda p: p.position)
        return {"others": others}

    def is_displayed(self):
        return (
            self.subsession.round_number == 1 and not
            self.player.kicked_or_left_over())


class Bargaining(Page):
    warning_time = "seconds_before_idle_warning_game_1"
    kick_time = "seconds_before_booted_from_study_after_warning"

    form_model = models.Player
    form_fields = ["coalition_with"]

    #~ def vars_for_template(self):
        #~ position




class Kicked(Page):
    warning_time = None
    kick_time = None

    def is_displayed(self):
        return self.player.kicked


page_sequence = [
    #~ InformedConsent,
    #~ Instructions1, Instructions2, Instructions3, Instructions4,
    #~ PhasesDescription, ComprehensionCheck,

    #~ PossitionAssignment,
    WaitPossitionAssignment,
    #~ PositionAssignmentResult,

    Bargaining,

    Kicked
]
