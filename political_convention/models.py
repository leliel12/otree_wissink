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

from jsonfield import JSONField

from . import utils


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    p_paths = settings.POLITICAL_CONVENTION_PARAMS_PATH
    p = utils.parse_argsfiles(*p_paths)

    name_in_url = 'political_convention'
    players_per_group = None
    num_rounds = p.number_of_games

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
        if self.round_number == 1:
            positions = it.cycle(Constants.positions)
            players = self.get_players()
            random.shuffle(players)
            for player in players:
                player.participant.vars["secret_key"] = str(uuid.uuid4())
                player.position = next(positions)
        else:
            positions = it.cycle(Constants.positions)
            players = self.get_players()
            random.shuffle(players)
            for player in players:
                if Constants.p.randomization_to_different_positions_between_games:
                    player.position = next(positions)
                else:
                    player.position = player.in_round(1).position

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
    last_bargain_number = models.IntegerField()

    def get_players(self):
        players = super(Group, self).get_players()
        players.sort(key=lambda p: p.position)
        return players

    def select_coalition(self, bargain_number):
        votes, total_votes = {}, 0
        for player in self.get_players():
            player.save_sugestion(bargain_number)
            cs = player.coalition_selected
            votes[cs] = votes.setdefault(cs, 0) + player.votes()
            total_votes += player.votes()

        # remove all coalitions below the threshold
        threshold = Constants.p.votes_necessary_for_coalition
        votes_filtered = {k: v for k, v in votes.items() if v >= threshold }

        # now sort by votes
        if votes_filtered:
            votes_list = list(votes_filtered.items())
            votes_list.sort(key=lambda e: e[1])
            coalition_candidate, candidate_votes = votes_list[0]

            ctext = Player.objects.get(id=coalition_candidate).sugest_coalition_with
            if len(ctext) != 3 or candidate_votes == total_votes:
                self.coalition_selected = coalition_candidate

        self.last_bargain_number = bargain_number

    def clear_fields(self):
        for player in self.get_players():
            player.offer_player_A = None
            player.offer_player_B = None
            player.offer_player_C = None

    def set_payoff(self):
        if self.coalition_selected:
            sugestor = self.coalition_sugestor()
            payoffs = {
                Constants.pA: sugestor.offer_player_A,
                Constants.pB: sugestor.offer_player_B,
                Constants.pC: sugestor.offer_player_C}
            for player in self.get_players():
                player.payoff = payoffs.get(player.position, None)

    def coalition_sugestor(self):
        return Player.objects.get(id=self.coalition_selected)

    def selection_resume(self):
        sugestions = {}
        for p in self.get_players():
            skey = (p.sugest_coalition_with, p.offer_resume())
            if skey in sugestions:
                sugested_by = sugestions[skey]["sugested_by"] + [p]
            else:
                sugested_by = [p]
            sugestions[skey] = {
                "sugested_by": sugested_by,
                "coalition": p.sugest_coalition_with,
                "payoff_a": p.offer_player_A,
                "payoff_b": p.offer_player_B,
                "payoff_c": p.offer_player_C,
                "selected_by": p.who_votes_me(),
                "selected": self.coalition_selected == p.id
            }
        sugestions = [sg for _, sg in sorted(sugestions.items())]
        return sugestions


# =============================================================================
# PLAYER
# =============================================================================

class Player(BasePlayer):

    kicked = models.BooleanField()
    left_over = models.BooleanField()
    position = models.CharField(max_length=10, choices=Constants.positions)
    sugest_coalition_with = models.CharField(max_length=3)
    offer_player_A = models.CurrencyField()
    offer_player_B = models.CurrencyField()
    offer_player_C = models.CurrencyField()

    # this store the id of the creator of the coalition
    coalition_selected = models.IntegerField()

    def save_sugestion(self, bargain_number):
        for pt in "ABC":
            fname_from = "offer_player_{}".format(pt)
            value = getattr(self, fname_from)
            fname_dest = "offer_player_{}_bargain_{}".format(pt, bargain_number)
            setattr(self, fname_dest, value)

        sugestor = self.coalition_sugestor()
        fname_dest = "coalition_selected_bargain_{}".format(bargain_number)
        setattr(self, fname_dest, sugestor.sugest_coalition_with)

        fname_dest = "coalition_selected_resume_bargain_{}".format(bargain_number)
        setattr(self, fname_dest, sugestor.offer_resume())
        self.save()

    def coalition_sugestor(self):
        return Player.objects.get(id=self.coalition_selected)

    def get_others_in_group(self):
        others = super(Player, self).get_others_in_group()
        others.sort(key=lambda p: p.position)
        return others

    def offer_resume(self):
        offers = (self.offer_player_A, self.offer_player_B, self.offer_player_C)
        offers = [o for o in offers if o is not None]
        offers_int = map(int, offers)
        offers_str = map(str, offers_int)
        return "-".join(offers_str)

    def kicked_or_left_over(self):
        return self.kicked or self.left_over

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


# =============================================================================
# DYNAMIX FIELDS
# =============================================================================

for idx, cq in enumerate(Constants.comprehension_questions):
    field = models.CharField(
        max_length=cq.max_length, verbose_name=cq.question,
        choices=cq.choices, widget=widgets.RadioSelectHorizontal())
    Player.add_to_class("cq{}".format(idx), field)

for idx in range(Constants.p.maximun_number_of_bargaining_rounds_possible):
    rnd = idx + 1
    Player.add_to_class(
        "offer_player_A_bargain_{}".format(rnd), models.CurrencyField())
    Player.add_to_class(
        "offer_player_B_bargain_{}".format(rnd), models.CurrencyField())
    Player.add_to_class(
        "offer_player_C_bargain_{}".format(rnd), models.CurrencyField())
    Player.add_to_class(
        "coalition_selected_bargain_{}".format(rnd), models.CharField(max_length=3))
    Player.add_to_class(
        "coalition_selected_resume_bargain_{}".format(rnd), models.CharField(max_length=20))
