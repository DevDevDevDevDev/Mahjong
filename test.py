# -*- coding: utf-8 -*-
import unittest

import tile
import waits


# 为了简化手牌信息输入, 这里使用函数将字符串转换为手牌
# 如 123 234 555 11 22
#    前三个是数牌花色, 分别是 123 各一张, 555 各一张, 3 三张
#    第四个是风牌, 11 表示两个东 (2/3/4 则分别表示南/西/北)
#    最后一个是三元牌, 1/2/3 分别表示中/白/发 (其实对于三元牌来说哪个是哪个无所谓了)
#    如果某个位置是一个横线, 则表示该花色没牌
def str2hand_tiles(s):
    suits = s.split(' ')

    tiles = tile.Tiles()
    for i in xrange(3):
        if suits[i] != '-':
            for s in suits[i]:
                tiles.numerics[i].add_rank(int(s) - 1)

    if suits[3] != '-':
        for s in suits[3]:
            tiles.wind.add_rank(int(s) - 1)

    if suits[4] != '-':
        for s in suits[4]:
            tiles.dragon.add_rank(int(s) - 1)
    return tiles


# 同样为了简化代码, 将字符串变成牌的集合, 各部分与上面的函数意义一致
def str2tile_set(s):
    suits = s.split(' ')
    tiles = set()

    for i in xrange(3):
        if suits[i] != '-':
            for s in suits[i]:
                tiles.add(tile.Tile(i, int(s) - 1))

    if suits[3] != '-':
        for s in suits[3]:
            tiles.add(tile.Tile(tile.WIND_SUIT, int(s) - 1))

    if suits[4] != '-':
        for s in suits[4]:
            tiles.add(tile.Tile(tile.DRAGON_SUIT, int(s) - 1))
    return tiles


NO_TILE = '- - - - -'


class Waits(unittest.TestCase):
    def assertWait(self, hand, waits_):
        self.assertSetEqual(str2tile_set(waits_),
                            waits.waits(str2hand_tiles(hand)))

    def test_13_orphans(self):
        self.assertWait('19 19 1999 123 12', NO_TILE)
        self.assertWait('19 19 199 124 123', '- - - 3 -')
        self.assertWait('19 19 19 1234 123', '19 19 19 1234 123')

    def test_7_pairs(self):
        self.assertWait('11 22 3 1122 1122', '- - 3 - -')
        self.assertWait('112233 111 - 1122 -', '- 1 - 12 -')

    def test_in_one_num_suit(self):
        self.assertWait('1 - - - -', '1 - - - -')
        self.assertWait('1223 - - - -', '2 - - - -')
        self.assertWait('1123 - - - -', '14 - - - -')
        self.assertWait('1233 - - - -', '3 - - - -')
        self.assertWait('2355 - - - -', '14 - - - -')
        self.assertWait('1234 - - - -', '14 - - - -')
        self.assertWait('2345699 - - - -', '147 - - - -')
        self.assertWait('2345678 - - - -', '258 - - - -')
        self.assertWait('2233 - - - -', '23 - - - -')
        self.assertWait('2333 - - - -', '124 - - - -')
        self.assertWait('2233445566 - - - -', '2356 - - - -')
        self.assertWait('2233445566678 - - - -', '23569 - - - -')
        self.assertWait('1112345677889 - - - -', '235689 - - - -')
        self.assertWait('2223333444456 - - - -', '1234567 - - - -')
        self.assertWait('2223456777999 - - - -', '12345678 - - - -')
        self.assertWait('1112345678999 - - - -', '123456789 - - - -')

    def test_in_two_num_suits(self):
        self.assertWait('11 11 - - -', '1 1 - - -')
        self.assertWait('12233 11 - - -', '14 - - - -')
        self.assertWait('11 23 - - -', '- 14 - - -')
        self.assertWait('11 13 - - -', '- 2 - - -')
        self.assertWait('23456 11 - - -', '147 - - - -')
        self.assertWait('11123 11123 - - -', '14 14 - - -')
        self.assertWait('23 13 - - -', NO_TILE)
        self.assertWait('11 11234567 - 111 -', '1 1 - - -')
        self.assertWait('11 11123456 - 111 -', '1 147 - - -')
        self.assertWait('11 11123 - 111222 -', '1 14 - - -')


tiles = str2hand_tiles('1112345678999 - - - -')
print tiles.list_tile()
print (tile.Mahjong() - tiles).list_tiles()