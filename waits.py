# -*- coding: utf-8 -*-
import tile
import group


def waits(tiles):
    return set(_waits_13(tiles) + _waits_7pairs(tiles) + _waits_4groups(tiles))


# 国士 13 面听的全部牌, 容我写死在这里
_13_ORPHANS_WAITS = (
    [tile.Tile(0, 0), tile.Tile(0, 8), tile.Tile(1, 0), tile.Tile(1, 8),
     tile.Tile(2, 0), tile.Tile(2, 8)] +
    [tile.Tile(tile.WIND_SUIT, i) for i in xrange(4)] +
    [tile.Tile(tile.DRAGON_SUIT, i) for i in xrange(3)])


def _waits_13(tiles):
    if tiles.total() != 13:
        return []

    # 将手牌里的 13 种幺九字牌弄出来
    # 组成一个元素结构为
    #    (牌, 数量)
    # 元组的列表, 并对这个列表进行排序, 排序的键是上述元组中的 "数量"
    orphans = sorted(
        [(tile.Tile(s, 0), s.count(0)) for s in tiles.numerics] +
        [(tile.Tile(s, 8), s.count(8)) for s in tiles.numerics] +
        [(tile.Tile(tile.WIND_SUIT, i), tiles.wind.count(i))
         for i in xrange(4)] +
        [(tile.Tile(tile.DRAGON_SUIT, i), tiles.dragon.count(i))
         for i in xrange(3)], key=lambda k: k[1])
    # 如果这个列表开头两项的数量都为 0 (因为排序了所以只要看第二项是不是 0) 肯定不是国士听牌
    if orphans[1][1] == 0:
        return []
    # 而如果第一项的数量就是 1 那么一定就是 13 面听了
    if orphans[0][1] == 1:
        return _13_ORPHANS_WAITS
    # 否则听的牌就是缺的那个
    return [orphans[0][0]]


def _waits_7pairs(tiles):
    if tiles.total() != 13:
        return []
    # 列出当前所有牌以及该牌的数量
    tiles_list = tiles.list_tiles()
    # NOTE: Japanese Mahjong doesn't allow two same pairs in 7-pairs
    #       in that case the predicate should be
    #  7 != len(tiles_list)
    if 7 < len(tiles_list):
        return []

    # 如果数量为奇数的牌恰好 1 个就是七对子听牌
    odds = [t[0] for t in tiles_list if t[1] % 2 == 1]
    return odds if len(odds) == 1 else []


def _waits_4groups(tiles):
    triplets, pairs, singles = _wind_dragon_groups(tiles)
    if pairs and singles:
        return []
    if 1 == len(singles):
        groups = _detect_completed_numeric_groups(tiles)
        return [] if groups is None else [singles[0][0]]
    if 2 == len(pairs):
        groups = _detect_completed_numeric_groups(tiles)
        return [] if groups is None else [pairs[0][0], pairs[1][0]]
    if 1 == len(pairs):
        waits, pair_wait = _detect_numeric_suit_with_two_more(tiles)
        if len(waits) == 0:
            return []
        if pair_wait:
            waits.append(pairs[0][0])
        return waits
    return (_detect_numeric_suit_with_one_more(tiles) +
            _detect_2_numeric_suits_with_2_more(tiles))


def _wind_dragon_groups(tiles):
    tiles_list = tiles.wind.list_tiles() + tiles.dragon.list_tiles()
    if len(tiles_list) == 0:
        return [], [], []
    singles = [t for t in tiles_list if t[1] == 1]
    pairs = [t for t in tiles_list if t[1] == 2]
    triplets = [t for t in tiles_list if t[1] == 3]
    quads = [t for t in tiles_list if t[1] == 4]
    return triplets + quads, pairs, singles + quads


def _detect_completed_numeric_groups(tiles):
    for i in xrange(3):
        if tiles.numerics[i].total() % 3 != 0:
            return None
    return sum([_completed_numeric_groups(i, tiles.numerics[i].copy_rank())
                for i in xrange(3)], group.Groups()).value()


# 找一个花色, 它的数量模 3 余 1
def _detect_numeric_suit_with_one_more(tiles):
    mod_numerics = sorted([(i, tiles.numerics[i].total() % 3)
                           for i in xrange(3)], key=lambda k: -k[1])
    if mod_numerics[0][1] != 1 or mod_numerics[1][1] != 0:
        return []
    suit_one_more = mod_numerics[0][0]
    group_suit_a, group_suit_b = mod_numerics[1][0], mod_numerics[2][0]
    completed_groups = (
        _completed_numeric_groups(
            group_suit_a, tiles.numerics[group_suit_a].copy_rank()) +
        _completed_numeric_groups(
            group_suit_b, tiles.numerics[group_suit_b].copy_rank())
    ).value()

    if completed_groups is None:
        return []

    tiles = tiles.numerics[suit_one_more].copy_rank()
    result = []
    for i, c in enumerate(tiles):
        if c != 0:
            copy_tiles = tiles[:]
            copy_tiles[i] -= 1
            groups = _completed_numeric_groups(suit_one_more, copy_tiles)
            if groups.value() is not None:
                result.append(tile.Tile(suit_one_more, i))

        # 如果某个牌至少有两张, 那么假定该牌是对子
        # 去掉这个对子, 试试剩下的是不是一个搭子或对子加上面子
        if c >= 2:
            copy_tiles = tiles[:]
            copy_tiles[i] -= 2
            result.extend(_numeric_suit_with_two_more(
                suit_one_more, copy_tiles)[0])

    return result


def _detect_numeric_suit_with_two_more(tiles):
    mod_numerics = sorted([(i, tiles.numerics[i].total() % 3)
                           for i in xrange(3)], key=lambda k: -k[1])
    if mod_numerics[0][1] != 2 or mod_numerics[1][1] != 0:
        return [], False
    group_suit_a, group_suit_b = mod_numerics[1][0], mod_numerics[2][0]
    completed_groups = (
        _completed_numeric_groups(
            group_suit_a, tiles.numerics[group_suit_a].copy_rank()) +
        _completed_numeric_groups(
            group_suit_b, tiles.numerics[group_suit_b].copy_rank())
    ).value()

    if completed_groups is None:
        return [], False

    suit_two_more = mod_numerics[0][0]
    return _numeric_suit_with_two_more(
        suit_two_more, tiles.numerics[suit_two_more].copy_rank())


# 找两个花色, 它们各自的牌的数量模 3 都余 2
def _detect_2_numeric_suits_with_2_more(tiles):
    mod_numerics = sorted([(i, tiles.numerics[i].total() % 3)
                           for i in xrange(3)], key=lambda k: -k[1])
    if mod_numerics[0][1] != 2 or mod_numerics[1][1] != 2:
        return []

    group_suit = mod_numerics[2][0]
    completed_groups = _completed_numeric_groups(
        group_suit, tiles.numerics[group_suit].copy_rank()).value()

    if completed_groups is None:
        return []

    # 分别分析这两个花色的牌
    suit_2more_a, suit_2more_b = mod_numerics[0][0], mod_numerics[1][0]
    waits_a, flag_pair_a = _numeric_suit_with_two_more(
        suit_2more_a, tiles.numerics[suit_2more_a].copy_rank())
    waits_b, flag_pair_b = _numeric_suit_with_two_more(
        suit_2more_b, tiles.numerics[suit_2more_b].copy_rank())

    # 那么, 当其中一个花色有对子时, 另一个花色所缺的牌都是听牌
    # 特别地, 如果两个花色都没有对子, 即 flag_pair_a, flag_pair_b 都是 False 时
    # result 会是空集, 此时没有听牌
    result = []
    if flag_pair_a:
        result.extend(waits_b)
    if flag_pair_b:
        result.extend(waits_a)
    return result


def _numeric_suit_with_two_more(suit, tiles):
    result = [tile.Tile(suit, pair_rank) for pair_rank, groups in
              _numeric_groups_with_pair(suit, tiles[:])]
    flag_pair = len(result) != 0

    for starting_rank, groups in _numeric_groups_with_side_waits(
            suit, tiles[:]):
        if starting_rank != 0:
            result.append(tile.Tile(suit, starting_rank - 1))
        if starting_rank != 7:
            result.append(tile.Tile(suit, starting_rank + 2))

    result.extend([
                      tile.Tile(suit, staring_rank + 1)
                      for staring_rank, groups in _numeric_groups_with_middle_waits(
            suit, tiles[:])])

    return result, flag_pair


def _numeric_groups_with_pair(suit, suit_tiles):
    result = []
    for i, c in enumerate(suit_tiles):
        if c >= 2:
            copy_tiles = suit_tiles[:]
            copy_tiles[i] -= 2
            groups = _completed_numeric_groups(suit, copy_tiles)
            if groups.value() is not None:
                result.append((i, groups))
    return result


def _numeric_groups_with_side_waits(suit, suit_tiles):
    result = []
    for i in xrange(8):
        if suit_tiles[i] and suit_tiles[i + 1]:
            copy_tiles = suit_tiles[:]
            copy_tiles[i] -= 1
            copy_tiles[i + 1] -= 1
            groups = _completed_numeric_groups(suit, copy_tiles)
            if groups.value() is not None:
                result.append((i, groups))
    return result


def _numeric_groups_with_middle_waits(suit, suit_tiles):
    result = []
    for i in xrange(7):
        if suit_tiles[i] and suit_tiles[i + 2]:
            copy_tiles = suit_tiles[:]
            copy_tiles[i] -= 1
            copy_tiles[i + 2] -= 1
            groups = _completed_numeric_groups(suit, copy_tiles)
            if groups.value() is not None:
                result.append((i, groups))
    return result


def _completed_numeric_groups(suit, suit_tiles):
    for i, c in enumerate(suit_tiles):
        if c != 0:
            first_rank = i
            break
    else:
        return group.Groups()

    if suit_tiles[first_rank] >= 3:
        tri = group.Triplet(suit, first_rank)
        suit_tiles[first_rank] -= 3
        return _completed_numeric_groups(suit, suit_tiles).append_group(tri)

    if (first_rank > 6 or suit_tiles[first_rank] > suit_tiles[first_rank + 1]
        or suit_tiles[first_rank] > suit_tiles[first_rank + 2]):
        return group.NoGroup()
    seqs = [group.Sequence(suit, first_rank)
            for _ in xrange(suit_tiles[first_rank])]
    suit_tiles[first_rank + 1] -= suit_tiles[first_rank]
    suit_tiles[first_rank + 2] -= suit_tiles[first_rank]
    suit_tiles[first_rank] = 0
    return _completed_numeric_groups(suit, suit_tiles) + seqs
