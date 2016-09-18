#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range, safe_json
)

from . import parameters_parser


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'political_convention'
    players_per_group = None
    num_rounds = 1

    params_path = settings.POLITICAL_CONVENTION_PARAMS_PATH
    params = parameters_parser.parse(params_path)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
