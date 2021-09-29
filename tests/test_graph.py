#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>
from __future__ import annotations

import fillomino as fo
import pytest
from fillomino.label import AK_DENYS, AK_NUMBER, AK_SKIP, AK_WALL


class Test_graph(object):
    """graphクラスのテスト
    """

    def test_default_constructor(self):
        """デフォルトコンストラクタのテスト
        """
        g = fo.graph()
        assert g._graph is None
        assert g.G is None

    def test_set_numbers_1(self):
        """set_numbersのテスト1
        """
        g = fo.graph()
        with pytest.raises(AssertionError) as e:
            g.set_numbers(None)
            assert e.type == AssertionError

    def test_set_numbers_2(self):
        """set_numbersのテスト2
        """
        mg = fo.master_graph(2, 3)
        mg.set_numbers([
            [1, 2, 3],
            [11, 12, 13]])
        L = fo.AK_NUMBER
        assert mg.G.nodes[0, 0][L] == 1
        assert mg.G.nodes[0, 1][L] == 2
        assert mg.G.nodes[0, 2][L] == 3
        assert mg.G.nodes[1, 0][L] == 11
        assert mg.G.nodes[1, 1][L] == 12
        assert mg.G.nodes[1, 2][L] == 13

    def test_set_numbers_3(self):
        """set_numbersのテスト3
        """
        mg = fo.master_graph(2, 3)
        mg.G.remove_node((1, 1))
        mg.set_numbers([
            [1, 2, 3],
            [11, 12, 13]])
        L = fo.AK_NUMBER
        assert mg.G.nodes[0, 0][L] == 1
        assert mg.G.nodes[0, 1][L] == 2
        assert mg.G.nodes[0, 2][L] == 3
        assert mg.G.nodes[1, 0][L] == 11
        assert mg.G.has_node((1, 1)) is False
        assert mg.G.nodes[1, 2][L] == 13

    def test_get_nodes_by_num_wo_skip_1(self):
        mg = fo.master_graph(2, 3)
        mg.set_numbers([
            [1, 0, 0],
            [0, 1, 0]])
        # 返り値
        assert mg.get_nodes_by_num_wo_skip(1) == [(0, 0), (1, 1)]
        # スキップフラグ
        mg.check_puzzled_out_subgraph()
        assert mg.get_nodes_by_num_wo_skip(1) == []

    def test_check_puzzled_out_subgraph_1(self):
        """check_puzzled_out_subgraphのテスト
        """
        mg = fo.master_graph(2, 3)
        mg.set_numbers([
            [1, 0, 0],
            [0, 1, 0]])
        # 返り値
        assert mg.check_puzzled_out_subgraph()
        # スキップフラグ
        assert mg.G.nodes[0, 0][AK_SKIP]
        assert not mg.G.nodes[0, 1][AK_SKIP]
        assert not mg.G.nodes[0, 2][AK_SKIP]
        assert not mg.G.nodes[1, 0][AK_SKIP]
        assert mg.G.nodes[1, 1][AK_SKIP]
        assert not mg.G.nodes[1, 2][AK_SKIP]
        # 拒否リスト
        assert 1 not in mg.G.nodes[0, 0][AK_DENYS]
        assert 1 in mg.G.nodes[0, 1][AK_DENYS]
        assert 1 not in mg.G.nodes[0, 2][AK_DENYS]
        assert 1 in mg.G.nodes[1, 0][AK_DENYS]
        assert 1 not in mg.G.nodes[1, 1][AK_DENYS]
        assert 1 in mg.G.nodes[1, 2][AK_DENYS]
        # 壁
        assert mg.G.edges[(0, 0), (0, 1)][AK_WALL]
        assert not mg.G.edges[(0, 1), (0, 2)][AK_WALL]
        assert mg.G.edges[(0, 0), (1, 0)][AK_WALL]
        assert mg.G.edges[(0, 1), (1, 1)][AK_WALL]
        assert not mg.G.edges[(0, 2), (1, 2)][AK_WALL]
        assert mg.G.edges[(1, 0), (1, 1)][AK_WALL]
        assert mg.G.edges[(1, 1), (1, 2)][AK_WALL]
        # 返り値(2度目)
        assert not mg.check_puzzled_out_subgraph()

    def test_get_leaves(self):
        mg = fo.master_graph(3, 3)
        mg.set_numbers([
            [0, 0, 2],
            [0, 0, 2],
            [3, 4, 0]])
        # 返り値
        assert mg.check_puzzled_out_subgraph()
        assert mg.check_other_number_wall()
        assert not mg.check_same_number_around_zero()
        foSGwo = fo.graph(mg.get_subgraph_wo_puzzled_out_and_wall_edges())
        assert foSGwo.get_leaves() == [(2, 0), (2, 2)]

    def test_get_nodes_from_leaf(self):
        mg = fo.master_graph(3, 3)
        mg.set_numbers([
            [0, 0, 2],
            [0, 0, 2],
            [3, 4, 0]])
        # 返り値
        assert mg.check_puzzled_out_subgraph()
        assert mg.check_other_number_wall()
        assert not mg.check_same_number_around_zero()
        foSGwo = fo.graph(mg.get_subgraph_wo_puzzled_out_and_wall_edges())
        assert foSGwo.get_leaves() == [(2, 0), (2, 2)]
        assert foSGwo.get_nodes_from_leaf((2, 0)) == [(2, 0), (1, 0)]
        assert foSGwo.get_nodes_from_leaf((2, 2)) == [(2, 2), (2, 1), (1, 1)]

    def test_check_leaf_graphs_1(self):
        """check_leaf_graphsのテスト
        """
        mg = fo.master_graph(3, 3)
        mg.set_numbers([
            [0, 0, 2],
            [0, 0, 2],
            [3, 4, 0]])
        # 返り値
        assert mg.check_puzzled_out_subgraph()
        assert mg.check_other_number_wall()
        assert not mg.check_same_number_around_zero()
        assert mg.check_leaf_graphs()
        assert mg.G.nodes[1, 0][AK_NUMBER] == 3
        assert mg.G.nodes[1, 1][AK_NUMBER] == 4

    def test_check_leaf_graphs_2(self):
        """check_leaf_graphsのテスト
        """
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [3, 3],
            [3, 0]])
        # 返り値
        assert mg.check_puzzled_out_subgraph()
        assert not mg.check_other_number_wall()
        assert not mg.check_same_number_around_zero()
        assert mg.check_leaf_graphs()
        assert mg.G.nodes[1, 1][AK_NUMBER] == 1

    def test_upload(self):
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [0, 1],
            [0, 2],
        ])
        mg.check_puzzled_out_subgraph()
        mg.check_other_number_wall()
        tg = fo.master_graph(2, 2)
        mg.upload(tg)
        assert tg.nodes[0, 0][AK_NUMBER] == 0
        assert tg.nodes[0, 1][AK_NUMBER] == 1
        assert tg.nodes[1, 0][AK_NUMBER] == 0
        assert tg.nodes[1, 1][AK_NUMBER] == 2
        assert not tg.nodes[0, 0][AK_SKIP]
        assert tg.nodes[0, 1][AK_SKIP]
        assert not tg.nodes[1, 0][AK_SKIP]
        assert not tg.nodes[1, 1][AK_SKIP]
        assert tg.nodes[0, 0][AK_DENYS] == set([1])
        assert tg.nodes[0, 1][AK_DENYS] == set()
        assert tg.nodes[1, 0][AK_DENYS] == set()
        assert tg.nodes[1, 1][AK_DENYS] == set()

    def test_download(self):
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [0, 1],
            [0, 2],
        ])
        mg.check_puzzled_out_subgraph()
        mg.check_other_number_wall()
        tg = fo.master_graph(2, 2)
        tg.download(mg)
        assert tg.nodes[0, 0][AK_NUMBER] == 0
        assert tg.nodes[0, 1][AK_NUMBER] == 1
        assert tg.nodes[1, 0][AK_NUMBER] == 0
        assert tg.nodes[1, 1][AK_NUMBER] == 2
        assert not tg.nodes[0, 0][AK_SKIP]
        assert tg.nodes[0, 1][AK_SKIP]
        assert not tg.nodes[1, 0][AK_SKIP]
        assert not tg.nodes[1, 1][AK_SKIP]
        assert tg.nodes[0, 0][AK_DENYS] == set([1])
        assert tg.nodes[0, 1][AK_DENYS] == set()
        assert tg.nodes[1, 0][AK_DENYS] == set()
        assert tg.nodes[1, 1][AK_DENYS] == set()

    def test_is_neighbor(self):
        mg = fo.master_graph(2, 2)
        mg.set_numbers([
            [0, 1],
            [0, 2],
        ])
        assert fo.graph.is_neighbor(mg.G, (0, 0), (0, 1))
        assert fo.graph.is_neighbor(mg.G, (0, 0), (1, 0))
        assert fo.graph.is_neighbor(mg.G, (0, 1), (1, 1))
        assert fo.graph.is_neighbor(mg.G, (1, 0), (1, 1))
        assert not fo.graph.is_neighbor(mg.G, (0, 0), (1, 1))
        assert not fo.graph.is_neighbor(mg.G, (0, 1), (1, 0))
