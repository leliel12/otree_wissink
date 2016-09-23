#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range, safe_json
)

from . import utils


author = 'Your name here'

doc = """
Your app description
"""




class Constants(BaseConstants):
    name_in_url = 'political_convention'
    players_per_group = None
    num_rounds = 1

    p_path = settings.POLITICAL_CONVENTION_PARAMS_PATH
    p = utils.parse_argsfile(p_path)

    comprehension_questions = [
        utils.ComprehensionQuestion(
            question="choose foo!", choices=("foo", "spam", "eggs"), answer=0),
        utils.ComprehensionQuestion(
            question="choose spam!", choices=("foo", "spam", "eggs"), answer=1),
        utils.ComprehensionQuestion(
            question="choose eggs!", choices=("foo", "spam", "eggs"), answer=2)
    ]

    pA, pB, pC, leftOver = "A", "B", "C", "LeftOver"
    positions = (pA, pB, pC, leftOver)


# =============================================================================
# Subsession
# =============================================================================

class Subsession(BaseSubsession):
    pass


# =============================================================================
# GROUP
# =============================================================================
class Group(BaseGroup):
    pass


# =============================================================================
# PLAYER
# =============================================================================
class Player(BasePlayer):

    kicked = models.BooleanField()
    position = models.CharField(max_length=10, choices=Constants.positions)


for idx, cq in enumerate(Constants.comprehension_questions):
    Player.add_to_class(
        "cq{}".format(idx), models.CharField(max_length=cq.max_length,
                                             verbose_name=cq.question,
                                             choices=cq.choices,
                                             widget=widgets.RadioSelectHorizontal())
    )

