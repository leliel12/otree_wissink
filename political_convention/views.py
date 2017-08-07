
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
        "because_debug": "<small>DEBUG is True</small>"}


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
        if self.subsession.round_number == 1 or Constants.p.random_assignment_to_different_bargaining_partners_between_games:
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
            for g in group_matrix:
                if len(g) != 3:
                    for p in g:
                        p.left_over = True
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


# =============================================================================
# CYCLE
# =============================================================================

class Bargaining(Page):
    warning_time = "seconds_before_idle_warning_game_1"
    kick_time = "seconds_before_booted_from_study_after_warning"
    template_name = "political_convention/Bargaining.html"
    bargain_number = None

    form_model = models.Player
    form_fields = [
        "sugest_coalition_with",
        "offer_player_A", "offer_player_B", "offer_player_C"]

    def is_displayed(self):
        if self.player.kicked_or_left_over():
            return False
        return not bool(self.group.coalition_selected)

    def vars_for_template(self):
        return {"bargain_number": self.bargain_number}


class WaitForBargaing(WaitPage):
    title_text = "Wait For all Players Proposals"
    body_text = "Wait until all players are done with their coalition proposals"

    warning_time = None
    kick_time = None
    bargain_number = None

    def is_displayed(self):
        if self.player.kicked_or_left_over():
            return False
        return not bool(self.group.coalition_selected)


class CoalitionSelection(Page):
    warning_time = "seconds_before_idle_warning_game_1"
    kick_time = "seconds_before_booted_from_study_after_warning"
    template_name = "political_convention/CoalitionSelection.html"
    bargain_number = None

    form_model = models.Player
    form_fields = ["coalition_selected"]

    def is_displayed(self):
        if self.player.kicked_or_left_over():
            return False
        return not bool(self.group.coalition_selected)

    def vars_for_template(self):
        sugestions = dict()
        for p in self.group.get_players():
            scw = p.sugest_coalition_with
            if scw and self.player.position in p.sugest_coalition_with:
                s = (scw, p.offer_resume(), p.id)
                skey = s[:-1]
                sugestions[skey] = s
        return {"sugestions": sorted(sugestions.values()), "bargain_number": self.bargain_number}


class WaitForCoalitionSelection(WaitPage):
    title_text = "Wait For all Players Proposals"
    body_text = "Wait until all players are done with their coalition proposals"
    repeat_number = None

    warning_time = None
    kick_time = None

    def is_displayed(self):
        if self.player.kicked_or_left_over():
            return False
        return not bool(self.group.coalition_selected)

    def after_all_players_arrive(self):
        self.group.select_coalition(self.bargain_number)
        self.group.set_payoff()


class FailCoalition(Page):

    warning_time = "seconds_before_idle_warning_game_1"
    kick_time = "seconds_before_booted_from_study_after_warning"
    template_name = "political_convention/FailCoalition.html"
    bargain_number = None

    def is_displayed(self):
        if self.player.kicked_or_left_over():
            return False
        elif self.bargain_number == Constants.p.maximun_number_of_bargaining_rounds_possible:
            return False
        return not bool(self.group.coalition_selected)

    def vars_for_template(self):
        sugestions = self.group.selection_resume()
        return {"sugestions": sugestions}

    def before_next_page(self):
        if self.bargain_number != Constants.p.maximun_number_of_bargaining_rounds_possible:
            self.group.clear_fields()


to_cicle = (
    Bargaining,
    WaitForBargaing,
    CoalitionSelection,
    WaitForCoalitionSelection,
    FailCoalition
)
cicle = []
for idx in range(Constants.p.maximun_number_of_bargaining_rounds_possible):
    contents = {"bargain_number": idx + 1}
    cicle.extend(
        type("{}{}".format(cls.__name__, idx), (cls,), contents) for cls in to_cicle)

globals().update({cls.__name__: cls for cls in cicle})
del to_cicle

# =============================================================================
# END CYCLE
# =============================================================================

class Result(Page):

    warning_time = "seconds_before_idle_warning_game_1"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def vars_for_template(self):
        sugestions = self.group.selection_resume()
        return {"sugestions": sugestions}

    def is_displayed(self):
        return not self.player.kicked_or_left_over()


class Resume(Page):

    warning_time = "seconds_before_idle_warning_game_1"
    kick_time = "seconds_before_booted_from_study_after_warning"

    def is_displayed(self):
        return not self.player.kicked_or_left_over()


class LeftOver(Page):
    warning_time = None
    kick_time = None

    def is_displayed(self):
        return self.player.left_over and not self.player.kicked


class Kicked(Page):
    warning_time = None
    kick_time = None

    def is_displayed(self):
        return (
            self.player.kicked and
            self.subsession.round_number == Constants.num_rounds)


# =============================================================================
# SEQUENCE
# =============================================================================

page_sequence = [
    InformedConsent,
    Instructions1, Instructions2, Instructions3, Instructions4,
    PhasesDescription, ComprehensionCheck,

    PossitionAssignment,
    WaitPossitionAssignment,
    PositionAssignmentResult
] + cicle + [
    Result,
    Resume,
    LeftOver,
    Kicked
]
