#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>
from __future__ import annotations

from dataclasses import dataclass
from itertools import chain, combinations
from math import comb
from typing import Union

import networkx as nx

from .graph import graph
from .label import AK_DENYS, AK_NUMBER


@dataclass
class zero_and_single_number_graph(graph):
    """0と1種類の数値を持つグラフ
    """

    _num: int = None

    def __post_init__(self):
        self._validated = None
        self.validate()

    @property
    def number(self):
        return self._num

    @classmethod
    def create(cls, origin: Union[nx.Graph, graph]) -> dict[int, list[zero_and_single_number_graph]]:
        """1種類の0以外の数値と0を持つ連結なグラフの辞書を返す

        Args:
            origin (Union[nx.Graph, graph]): 分割元のグラフ

        Raises:
            TypeError: 型が合わない時

        Returns:
            dict[int, list[zero_and_single_number_graph]]: キーが数値で、値がグラフのリストな辞書
        """
        assert origin is not None
        if isinstance(origin, graph):
            foOG = origin
        elif isinstance(origin, nx.Graph):
            foOG = graph(origin)
        else:
            raise TypeError('originが期待する型ではありません')
        result: dict[int, list[cls]] = {}
        # 完了済みの部分と壁を削除
        foSGwo = graph(foOG.get_subgraph_wo_puzzled_out_and_wall_edges())
        if foSGwo.G.number_of_nodes() == 0:
            return result  # ノード数が0なら終了
        # 使用されている数値の一覧を取得
        numlist = foSGwo.get_used_numbers_wo_skip()
        if 0 in numlist:
            numlist.remove(0)  # 0 を削除
        # 数値ごとに作成する
        for num in numlist:
            # 数値が 0 かつ 拒否リストに num が無い
            zero_nodes = [
                n for n, d in foSGwo.nodes.data()
                if d[AK_NUMBER] == 0 and num not in d[AK_DENYS]
            ]
            # 数値が num のノード
            num_nodes = graph.get_nodes_by_num(foSGwo.G, num)
            # サブグラフを作成
            SG: nx.Graph = foSGwo.G.subgraph(sorted(chain(num_nodes, zero_nodes)))
            result[num] = []
            # 連結成分に分ける
            for c in nx.connected_components(SG):
                fog = cls(SG.subgraph(c).copy())
                assert fog.validate()
                # num が入っていないグラフは弾く
                if any([d == num for _, d in fog.nodes.data(AK_NUMBER, 0)]):
                    result[num].append(fog)
        return result

    def validate(self, force: bool = False) -> bool:
        """グラフが正しいか検証する

        Args:
            force (bool, optional): 再計算を強制するか. Defaults to False.

        Returns:
            bool: 正しければTrue
        """
        assert self.G is not None
        if not force and self._validated is not None:
            # forceフラグがなく、計算済みであれば保存済みの結果を返す
            return self._validated
        result = True
        nums_dict = dict(self.G.nodes.data(AK_NUMBER, 0))
        nums = set(nums_dict.values())
        if 0 in nums:  # 0を消す
            nums.remove(0)
        if len(nums) > 1:
            # 集合が2より大きければ複数の数値を持つのでNG
            result = False
            self._num = None
        elif len(nums) == 1:
            # 数値があれば保存する
            self._num = list(nums)[0]
        else:
            # 0 しかない場合
            self._num = 0
        # フラグを保存しておく
        self._validated = result
        return result

    def solve_comb(self) -> bool:
        """1種類の0以外の数値と0を持つ連結なグラフを組み合わせで解く

        Returns:
            bool: 変更があればTrue
        """
        assert self.is_connected
        result = False
        G = self.G
        num_nodes = [
            n for n, d in G.nodes.data()
            if d[AK_NUMBER] != 0
        ]
        zero_nodes = graph.get_nodes_by_num(G, 0)
        assert len(num_nodes) > 0
        assert len(zero_nodes) > 0
        num = G.nodes[num_nodes[0]][AK_NUMBER]
        assert num != 0
        # パターン数え上げ
        all_nodes = list(sorted(chain(num_nodes, zero_nodes)))
        # 組み合わせ数が大きい時は諦める
        if comb(len(all_nodes), num) > 1023:
            return result
        combi_all = combinations(all_nodes, num)
        # 数値の入っていない組み合わせを除外する
        combi_with_num = []
        num_nodes_set = set(num_nodes)
        for ca in combi_all:
            tmp = set(ca) & num_nodes_set
            if len(tmp) > 0:
                combi_with_num.append(ca)
        # 組み合わせが少なすぎる時は諦める
        # if len(combi_with_num) < 3:
        #     return result
        # 連結を選り分け
        combi = []
        for c in combi_with_num:
            Gtmp: nx.Graph = G.subgraph(c)  # グラフ化して
            if nx.is_connected(Gtmp):  # 連結か？
                combi.append(list(c))
        # 組み合わせが少なすぎる時は諦める
        # if len(combi) < 3:
        #     return result
        # 数値ノードを消す
        for c in combi:
            for n in c:
                if n in num_nodes:
                    c.remove(n)
        # 重複を探す
        duplications = set(combi[0])
        for c in combi[1:]:
            duplications &= set(c)
        # 重複箇所に値を設定する
        for n in duplications:
            G.nodes[n][AK_NUMBER] = num
            result = True
        return result

    def solve_4n_2c(self) -> bool:
        """4以上の数値で2連結以上の部分グラフを解く
        """
        result = False
        G = self.G
        num_nodes = graph.get_nodes_by_num(G, self.number)
        num = G.nodes[num_nodes[0]][AK_NUMBER]
        if num < 4:  # 4未満は却下
            return result
        # 数値のみ(0も除く)のグラフ
        foSG = zero_and_single_number_graph(G.subgraph(num_nodes))
        SGs = foSG.get_connected_subgraphs()
        nodes_group = []
        for SG in SGs:
            # 2連結以上
            if SG.number_of_nodes() >= 2:
                nodes_group.append(list(SG.nodes))
        nodes_group_dict = {}
        for ng in nodes_group:
            numcon = len(ng)
            r = num - numcon  # 伸び代
            node_set = set()
            for n in ng:
                spd = nx.single_source_shortest_path(G, n, r)
                for sp in spd.values():
                    node_set.update(sp)
            nodes_group_dict[tuple(ng)] = zero_and_single_number_graph(G.subgraph(node_set))
            result |= nodes_group_dict[tuple(ng)].solve_comb()
            nodes_group_dict[tuple(ng)].upload(G)
        return result
