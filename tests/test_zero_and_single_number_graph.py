#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>
from __future__ import annotations

import fillomino as fo
from fillomino.label import AK_NUMBER
# from matplotlib import pyplot as plt


class Test_zero_and_single_number_graph(object):

    def test_validate_1(self):
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [0, 0],
            [0, 0],
        ])
        zsg = fo.zero_and_single_number_graph(mg.G)
        assert zsg.validate()

    def test_validate_2(self):
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [2, 2],
            [0, 0],
        ])
        zsg = fo.zero_and_single_number_graph(mg.G)
        assert zsg.validate()

    def test_validate_3(self):
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [0, 1],
            [0, 2],
        ])
        zsg = fo.zero_and_single_number_graph(mg.G)
        assert not zsg.validate()

    def test_upload(self):
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [0, 1],
            [0, 2],
        ])
        tg = fo.master_graph(2, 2)
        zsg = fo.zero_and_single_number_graph(mg.G)
        zsg.upload(tg)
        assert tg.nodes[0, 0][AK_NUMBER] == 0
        assert tg.nodes[0, 1][AK_NUMBER] == 1
        assert tg.nodes[1, 0][AK_NUMBER] == 0
        assert tg.nodes[1, 1][AK_NUMBER] == 2

    def test_solve_1(self):
        """docstring
        """
        mg = fo.master_graph(4, 4)
        mg.set_numbers([
            [0, 4, 4, 4],
            [6, 0, 0, 4],
            [6, 3, 0, 0],
            [0, 3, 0, 1], ])
        assert mg.check_puzzled_out_subgraph()
        assert mg.check_other_number_wall()
        assert not mg.check_same_number_around_zero()
        assert not mg.check_leaf_graphs()
        # mg.draw()
        gdic = fo.zero_and_single_number_graph.create(mg)
        zsg = gdic[6][0]
        assert zsg.solve_comb()
        assert zsg.G.nodes[1, 1][AK_NUMBER] == 6
        assert zsg.G.nodes[1, 2][AK_NUMBER] == 6
        # zsg.draw()
        # plt.show()
