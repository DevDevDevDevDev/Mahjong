# -*- coding: utf-8 -*-
class Group(object):
    pass


class Sequence(Group):
    def __init__(self, suit, starting_rank):
        self.suit = suit
        self.starting_rank = starting_rank


class Triplet(Group):
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank


class NoGroup(object):
    def value(self):
        return None

    def __add__(self, rhs):
        return self

    def append_group(self, group):
        return self


class Groups(list, NoGroup):
    def __init__(self, value=None):
        list.__init__(self, value or [])

    def value(self):
        return self

    def __add__(self, rhs):
        if type(rhs) is NoGroup:
            return NoGroup()
        return Groups(list.__add__(self, rhs))

    def append_group(self, group):
        self.append(group)
        return self