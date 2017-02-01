#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import itertools as it
import uuid

from django.conf import settings

from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range, safe_json,
)

from otree.db.serializedfields import JSONField

from . import utils


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'political_convention'
    players_per_group = None
    num_rounds = 3

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

    pA, pB, pC, pK, leftOver = "A", "B", "C", "Kicked", "leftOver"
    positions = (pA, pB, pC)


# =============================================================================
# Subsession
# =============================================================================

class Subsession(BaseSubsession):

    def before_session_starts(self):
        positions = it.cycle(Constants.positions)
        if self.round_number == 1:
            participants = [p.participant for p in self.get_players()]
            random.shuffle(participants)
            for participant in participants:
                participant.vars["secret_key"] = str(uuid.uuid4())
                position = next(positions)
                for player in participant.get_players():
                    player.position = position

    def players_by_position(self):
        pas, pbs, pcs, ks = [], [], [], []
        for player in self.get_players():
            if player.kicked:
                ks.append(player)
            elif player.position == Constants.pA:
                pas.append(player)
            elif player.position == Constants.pB:
                pbs.append(player)
            elif player.position == Constants.pC:
                pcs.append(player)
        return pas, pbs, pcs, ks




# =============================================================================
# GROUP
# =============================================================================
class Group(BaseGroup):

    coalition_selected = models.IntegerField()

    def get_players(self):
        players = super(Group, self).get_players()
        players.sort(key=lambda p: p.position)
        return players

    def select_coalition(self):
        votes = {}
        for player in self.get_players():
            cs = player.coalition_selected
            votes[cs] = votes.setdefault(cs, 0) + player.votes()

        # remove all coalitions below the threshold
        threshold = Constants.p.votes_necessary_for_coalition
        votes_filtered = {k: v for k, v in votes.items() if v >= threshold}

        # now sort by votes
        if votes_filtered:
            votes_list = list(votes_filtered.items())
            votes_list.sort(key=lambda e: e[1])
            self.coalition_selected = votes_list[0][0]

    def coalition_sugestor(self):
        return Player.objects.get(id=self.coalition_selected)


# =============================================================================
# PLAYER
# =============================================================================

class Player(BasePlayer):

    kicked = models.BooleanField()
    position = models.CharField(max_length=10, choices=Constants.positions)
    sugest_coalition_with = models.CharField(max_length=3)
    offer_player_A = models.CurrencyField()
    offer_player_B = models.CurrencyField()
    offer_player_C = models.CurrencyField()

    # this store the id of the creator of the coalition
    coalition_selected = models.IntegerField()

    def coalition_sugestor(self):
        return Player.objects.get(id=self.coalition_selected)

    def get_others_in_group(self):
        others = super(Player, self).get_others_in_group()
        others.sort(key=lambda p: p.position)
        return others

    def offer_resume(self):
        offers = (self.offer_player_A, self.offer_player_B, self.offer_player_C)
        offers_int = map(int, offers)
        offers_str = map(str, offers_int)
        return "-".join(offers_str)

    def left_over(self):
        return self.position == Constants.leftOver

    def kicked_or_left_over(self):
        return self.kicked or self.left_over()

    def who_votes_me(self):
        return [p for p in self.group.get_players() if p.coalition_selected == self.id]

    @property
    def secret_key(self):
        return self.participant.vars["secret_key"]

    def possibility_to_give_in_coalitions(self):
        coalitions = [
            "".join(c) for c in it.combinations(Constants.positions, 2)
        ] + ["".join(Constants.positions)]
        allowed = []
        for c in coalitions:
            attr_name = "possibility_to_give_{}_money_in_an_{}_coalition".format(
                self.position, c)
            if getattr(Constants.p, attr_name):
                allowed.append(c)
        return allowed

    def coalitions_allowed(self):
        not_me = [p for p in Constants.positions if p not in self.position]
        not_me.append("".join(not_me))
        allowed = []
        for coalition in not_me:
            key = "".join(sorted(self.position + coalition))
            attr_name = "possibility_{}_to_propose_an_{}_coalition".format(
                self.position, key)
            if getattr(Constants.p, attr_name):
                allowed.append(coalition)
        return [
            (" and ".join(a), "".join(sorted(self.position + a)))
            for a in allowed]

    def votes(self):
        return getattr(Constants.p, "votes_player_{}".format(self.position))

for idx, cq in enumerate(Constants.comprehension_questions):
    Player.add_to_class(
        "cq{}".format(idx), models.CharField(max_length=cq.max_length,
                                             verbose_name=cq.question,
                                             choices=cq.choices,
                                             widget=widgets.RadioSelectHorizontal())
    )

