#!/usr/bin/env python
# -*- coding: utf-8 -*-

import attr

from six.moves import configparser

SECTION = "political_convention"


# =============================================================================
# VALIDATORS
# =============================================================================

def gt0(instance, attribute, value):
    if not value  > 0:
        msg = "'{}' must be > 0. Found {}".format(attribute.name, value)
        raise ValueError(msg)


def ge0(instance, attribute, value):
    if not value  >= 0:
        msg = "'{}' must be >= 0. Found {}".format(attribute.name, value)
        raise ValueError(msg)


def outcome(instance, attribute, value):
    if not instance.negative_points:
        if value < 0:
            msg = "'negative_points' is disabled so '{}' must be >= 0. Found {}".format(attribute.name, value)
            raise ValueError(msg)


def answer(instance, attribute, value):
    if value >= len(instance.choices):
        msg = "answer out of range"
        raise ValueError(msg)


# =============================================================================
# CONVERSION
# =============================================================================

def to_bool(val):
    return val.lower() in ("yes", "true", "on")


# =============================================================================
# CLASS
# =============================================================================

@attr.s(frozen=True, repr=False)
class Params(object):
    path = attr.ib(convert=str)
    number_of_games = attr.ib(convert=int, validator=gt0)
    enable_warning_and_kick = attr.ib(convert=to_bool)
    enable_instructions = attr.ib(convert=to_bool)

    seconds_before_idle_warning_instruction = attr.ib(convert=int, validator=ge0)
    seconds_before_warning_too_long_on_page_instruction = attr.ib(convert=int, validator=ge0)
    seconds_before_booted_from_study_after_warning = attr.ib(convert=int, validator=ge0)
    seconds_before_idle_warning_game_1 = attr.ib(convert=int, validator=ge0)
    seconds_before_warning_too_long_game_1 = attr.ib(convert=int, validator=ge0)
    seconds_before_idle_warning_other_games = attr.ib(convert=int, validator=ge0)
    seconds_before_warning_too_long_other_games = attr.ib(convert=int, validator=ge0)

    randomization_to_different_positions_between_games = attr.ib(convert=to_bool)
    random_assignment_to_different_bargaining_partners_between_games = attr.ib(convert=to_bool)
    negative_points = attr.ib(convert=to_bool)

    total_sum_of_outcomes = attr.ib(convert=int, validator=outcome)
    starting_points_for_each_game_player_A = attr.ib(convert=int, validator=outcome)
    starting_points_for_each_game_player_B = attr.ib(convert=int, validator=outcome)
    starting_points_for_each_game_player_C = attr.ib(convert=int, validator=outcome)

    votes_player_A = attr.ib(convert=int, validator=ge0)
    votes_player_B = attr.ib(convert=int, validator=ge0)
    votes_player_C = attr.ib(convert=int, validator=ge0)
    votes_necessary_for_coalition = attr.ib(convert=int, validator=ge0)

    coalition_before_formation_step_II = attr.ib(convert=to_bool)
    maximun_number_of_bargaining_rounds_possible = attr.ib(convert=int)

    payoff_to_player_A_when_maximum_number_of_bargaining_rounds_is_reached = attr.ib(convert=int)
    payoff_to_player_B_when_maximum_number_of_bargaining_rounds_is_reached = attr.ib(convert=int)
    payoff_to_player_C_when_maximum_number_of_bargaining_rounds_is_reached = attr.ib(convert=int)

    possibility_A_to_propose_an_AB_coalition = attr.ib(convert=to_bool)
    possibility_A_to_propose_an_AC_coalition = attr.ib(convert=to_bool)
    possibility_A_to_propose_an_ABC_coalition = attr.ib(convert=to_bool)
    possibility_B_to_propose_an_AB_coalition = attr.ib(convert=to_bool)
    possibility_B_to_propose_an_BC_coalition = attr.ib(convert=to_bool)
    possibility_B_to_propose_an_ABC_coalition = attr.ib(convert=to_bool)
    possibility_C_to_propose_an_BC_coalition = attr.ib(convert=to_bool)
    possibility_C_to_propose_an_AC_coalition = attr.ib(convert=to_bool)
    possibility_C_to_propose_an_ABC_coalition = attr.ib(convert=to_bool)

    possibility_to_give_A_money_in_an_AB_coalition = attr.ib(convert=to_bool)
    possibility_to_give_A_money_in_an_AC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_A_money_in_an_BC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_A_money_in_an_ABC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_B_money_in_an_AB_coalition = attr.ib(convert=to_bool)
    possibility_to_give_B_money_in_an_AC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_B_money_in_an_BC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_B_money_in_an_ABC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_C_money_in_an_AB_coalition = attr.ib(convert=to_bool)
    possibility_to_give_C_money_in_an_AC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_C_money_in_an_BC_coalition = attr.ib(convert=to_bool)
    possibility_to_give_C_money_in_an_ABC_coalition = attr.ib(convert=to_bool)

    def __repr__(self):
        return "<Params '{}'>".format(self.path)

    @property
    def AB_coalition_votes(self):
        return self.votes_player_A + self.votes_player_B

    @property
    def BC_coalition_votes(self):
        return self.votes_player_B + self.votes_player_C

    @property
    def AC_coalition_votes(self):
        return self.votes_player_A + self.votes_player_C

    @property
    def ABC_coalition_votes(self):
        return self.votes_player_A + self.votes_player_B + self.votes_player_C

    @property
    def AB_coalition_posibility(self):
        return (
            self.possibility_A_to_propose_an_AB_coalition or
            self.possibility_B_to_propose_an_AB_coalition)

    @property
    def AC_coalition_posibility(self):
        return (
            self.possibility_A_to_propose_an_AC_coalition or
            self.possibility_C_to_propose_an_AC_coalition)

    @property
    def BC_coalition_posibility(self):
        return (
            self.possibility_B_to_propose_an_BC_coalition or
            self.possibility_C_to_propose_an_BC_coalition)

    @property
    def ABC_coalition_posibility(self):
        return (
            self.possibility_A_to_propose_an_ABC_coalition or
            self.possibility_B_to_propose_an_ABC_coalition or
            self.possibility_C_to_propose_an_ABC_coalition)

    def get(self, k, d=None):
        asdict = attr.asdict(self)
        return asdict.get(k, d)


@attr.s(frozen=True)
class ComprehensionQuestion(object):
    question = attr.ib(convert=str)
    choices = attr.ib(convert=tuple)
    answer = attr.ib(convert=int, validator=answer)

    @property
    def max_length(self):
        return max(map(len, self.choices))

    def is_correct(self, a):
        return self.choices[self.answer] == a


# =============================================================================
# FUNCTIONS
# =============================================================================

def parse_argsfiles(*paths):
    kwargs = {}
    for path in paths:
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(path)
        kwargs.update({
            option: config.get(SECTION, option)
            for option in config.options(SECTION)})
    return Params(path=paths, **kwargs)
