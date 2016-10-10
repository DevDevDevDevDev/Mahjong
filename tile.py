# -*- coding: utf-8 -*-
# 牌
import copy
from itertools import combinations


class Tile(object):
    def __init__(self, suit, rank):
        self.suit = suit  # 花色: 用 0, 1, 2, 3, 4 表示
        # 其中 0-2 是数牌 3 是风牌 4 是三元牌
        self.rank = rank  # 数值: 对于数牌范围是 0-8 风牌范围 0-3 三元牌范围 0-2

    def __eq__(self, rhs):
        return self.suit == rhs.suit and self.rank == rhs.rank

    # 为了能让这东西被放进 set
    def __hash__(self):
        return hash(self.suit) * hash(self.rank)

    # 直观显示
    def __repr__(self):
        return (self.suit, self.rank + 1).__repr__()

    def int(self):
        return self.suit * 10 + self.rank + 1


# 一个花色里的牌
class TilesSuite(object):
    def __init__(self, count, suit, tile_count=0):
        # 这个数字表示个数
        # 比如手牌是 2 个二万 3 个三万, 那么这个数组会是 [0, 2, 3, 0, 0, 0, 0, 0, 0]
        self.rank_count = [tile_count] * count
        self.suit = suit

    def count(self, rank):
        return self.rank_count[rank]

    # 摸上来一张牌
    def add_rank(self, rank):
        self.rank_count[rank] += 1

    # 打出一张牌
    def remove_rank(self, rank):
        self.rank_count[rank] -= 1

    def copy_rank(self):
        return self.rank_count[:]

    # 去掉所有为 0 的项目, 返回一个元素结构为
    #    (牌, 数量)
    # 元组的列表
    def list_tiles(self):
        return [(Tile(self.suit, i), e)
                for i, e in enumerate(self.rank_count) if e != 0]

    # 这个花色下总共有几张牌
    def total(self):
        return sum(self.rank_count)

    def __sub__(self, other):
        assert self.suit == other.suit
        assert len(self.rank_count) == len(other.rank_count)
        result = copy.deepcopy(self)
        for i, v in enumerate(other.rank_count):
            result.rank_count[i] -= v
        return result

    def __add__(self, other):
        assert self.suit == other.suit
        assert len(self.rank_count) == len(other.rank_count)
        result = copy.deepcopy(self)
        for i, v in enumerate(other.rank_count):
            result.rank_count[i] += v
        return result


WIND_SUIT = 3  # 如之前提到的, 风牌的花色值为 3
DRAGON_SUIT = 4  # 三元牌的花色值为 4


class Tiles(object):
    def __init__(self):
        # 三种数牌个数量分布
        self.numerics = [TilesSuite(9, i) for i in xrange(3)]
        # 风牌的数量分布
        self.wind = TilesSuite(4, WIND_SUIT)
        # 三元牌的数量分布
        self.dragon = TilesSuite(3, DRAGON_SUIT)

    def total(self):
        return (sum([self.numerics[i].total() for i in xrange(3)]) +
                self.wind.total() + self.dragon.total())

    def list_tiles(self):
        return (sum([self.numerics[i].list_tiles() for i in xrange(3)], []) +
                self.wind.list_tiles() + self.dragon.list_tiles())

    def list_tile(self):
        tile_list = []
        for t in self.list_tiles():
            tile_list.extend([t[0].int()] * t[1])
        return tile_list

    def combinations(self, n):
        return combinations(self.list_tile(), n)

    def __sub__(self, other):
        assert len(self.numerics) == 3 and len(other.numerics) == 3
        result = Tiles()
        for i in range(3):
            result.numerics[i] = self.numerics[i] - other.numerics[i]
        result.wind = self.wind - other.wind
        result.dragon = self.dragon - other.dragon
        return result

    def __add__(self, other):
        assert len(self.numerics) == 3 and len(other.numerics) == 3
        result = Tiles()
        for i in range(3):
            result.numerics = self.numerics + other.numerics
        result.wind = self.wind + other.wind
        result.dragon = self.dragon + other.dragon
        return result


# 桌牌
class Mahjong(Tiles):
    def __init__(self):
        # 三种数牌个数量分布
        self.numerics = [TilesSuite(9, i, 4) for i in xrange(3)]
        # 风牌的数量分布
        self.wind = TilesSuite(4, WIND_SUIT)
        # 三元牌的数量分布
        self.dragon = TilesSuite(3, DRAGON_SUIT)
