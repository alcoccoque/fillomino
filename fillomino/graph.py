#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

import networkx as nx
from matplotlib import pyplot as plt

from .errors import WrongAnswerError
from .label import (AK_COLOR, AK_DENYS, AK_LABEL, AK_NUMBER, AK_SKIP, AK_WALL,
                    AK_WIDTH)


@dataclass
class graph:
    _graph: nx.Graph = None

    @property
    def G(self) -> nx.Graph:
        return self._graph

    @property
    def nodes(self):
        return self.G.nodes

    @property
    def edges(self):
        return self.G.edges

    @property
    def degree(self):
        return self.G.degree

    @property
    def adj(self):
        return self.G.adj

    @property
    def is_connected(self) -> bool:
        """連結グラフであれば True
        """
        return nx.is_connected(self.G)

    def get_connected_subgraphs(self) -> list[nx.Graph]:
        """連結サブグラフに分割する

        Returns:
            list: 連結サブグラフのリスト
        """
        result = []
        # 連結成分に分ける
        G = self.G
        for c in nx.connected_components(G):
            SG = G.subgraph(c)
            assert nx.is_connected(SG)
            result.append(SG)
        return result

    @staticmethod
    def is_neighbor(G: nx.Graph, node1, node2) -> bool:
        """グラフ G に於いて、node1 と node2 が隣り合っているか返す
        """
        result = True if node1 in G.neighbors(node2) else False
        return result

    @staticmethod
    def get_nodes_by_num(G: nx.Graph, num: int) -> list:
        """グラフから特定の数値を持ったノードのリストを得る
        """
        result = [
            n for n, d in G.nodes.data()
            if d[AK_NUMBER] == num
        ]
        return result

    def get_nodes_by_num_wo_skip(self, num: int) -> list:
        """指定した数値を持つノードのリストを得る

        Notes:
            スキップフラグの立っているノードは無視する
        """
        result = [
            n for n, d in self.G.nodes.data()
            if not d[AK_SKIP] and d[AK_NUMBER] == num
        ]
        return result

    def upload(self, graph_to: Union[nx.Graph, graph]) -> None:
        """このグラフのデータを他のグラフにアップロードする

        Args:
            target_graph (object): アップロード先のグラフ
        """
        if isinstance(graph_to, graph):
            upG = graph_to.G
        elif isinstance(graph_to, nx.Graph):
            upG = graph_to
        for n, d in self.G.nodes.data():
            upG.nodes[n].update(d)

    def download(self, graph_from: Union[nx.Graph, graph]) -> None:
        """他のグラフのデータをこのグラフにダウンロードする

        Args:
            target_graph (object): アップロード先のグラフ
        """
        if isinstance(graph_from, graph):
            dwG = graph_from.G
        elif isinstance(graph_from, nx.Graph):
            dwG = graph_from
        for n, d in dwG.nodes.data():
            self.G.nodes[n].update(d)

    def set_numbers(self, numbers: list[list[int]]) -> None:
        """グラフに数値を設定する

        Note:
            ノードが存在しない場合はスルーする
        """
        assert numbers is not None
        assert self.G is not None
        for node, data in self.G.nodes(data=True):
            m, n = node
            if len(numbers) > m and len(numbers[m]) > n:
                data[AK_NUMBER] = numbers[m][n]

    def set_attributes(self) -> None:
        """描画に備えて各種属性を設定する
        """
        # ノード
        for _, nd in self.G.nodes(data=True):
            # 数値を設定
            n = nd[AK_NUMBER]
            nd[AK_LABEL] = n
            # 数値に応じて色を設定
            if n == 0:
                nd[AK_COLOR] = (0.94,) * 3
            else:
                n -= 0
                f = 0b1
                r = (n & f) | ((n >> 3) & f)
                g = ((n >> 1) & f) | ((n >> 4) & f)
                b = ((n >> 2) & f) | ((n >> 5) & f)
                multi = 0.12
                bias = 0.9 - multi * 3
                nd[AK_COLOR] = (
                    multi * r + bias % 1,
                    multi * g + bias % 1,
                    multi * b + bias % 1
                )
        # エッジ
        for n1, n2, ed in self.G.edges(data=True):
            # 壁を設定
            if ed[AK_WALL]:
                ed[AK_LABEL] = 'x'
                ed[AK_COLOR] = (0.95,) * 3
                ed[AK_WIDTH] = 1
            else:
                ed[AK_LABEL] = ''
                if (self.G.nodes[n1][AK_NUMBER] != 0
                        and self.G.nodes[n1][AK_NUMBER] == self.G.nodes[n2][AK_NUMBER]):
                    ed[AK_COLOR] = self.G.nodes[n1][AK_COLOR]
                    ed[AK_WIDTH] = 6
                else:
                    ed[AK_COLOR] = 'maroon'
                    ed[AK_WIDTH] = 1

    def draw(self, figsize: tuple[float, float] = (10, 10)) -> None:
        """描画する
        """
        fig = plt.figure(figsize=figsize)
        # ノード座標のの最小値/最大値
        ml, nl = set([0]), set([0])
        for node in self.G.nodes():
            ml.add(node[0])
            nl.add(node[1])
        # 軸と軸の数値を設定
        ax = fig.add_subplot(
            xticks=[x for x in range(min(ml), max(ml) + 1, 1)],
            yticks=[y for y in range(min(nl), max(nl) + 1, 1)],
        )
        # Y軸を反転
        ax.invert_yaxis()
        G = self.G
        pos = {(x, y): (y, x) for x, y in G.nodes()}
        self.set_attributes()
        nlabels = nx.get_node_attributes(G, AK_LABEL)
        ncolors = list(nx.get_node_attributes(G, AK_COLOR).values())
        ecolors = list(nx.get_edge_attributes(G, AK_COLOR).values())
        widths = list(nx.get_edge_attributes(G, AK_WIDTH).values())
        nx.draw(
            G, pos, ax,
            labels=nlabels,
            node_color=ncolors,
            edge_color=ecolors,
            with_labels=True,
            node_size=600,
            width=widths
        )
        elabels = nx.get_edge_attributes(G, AK_LABEL)
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=elabels,
            font_size=6
        )
        plt.axis('on')
        ax.tick_params(
            left=True,
            bottom=True,
            labelleft=True,
            labelbottom=True
        )

    def get_used_numbers(self) -> list[int]:
        """使用されている数値の一覧を返す
        """
        nums = set()
        for _, d in self.G.nodes(data=True):
            nums.add(d[AK_NUMBER])
        return sorted(list(nums))

    def get_used_numbers_wo_skip(self) -> list[int]:
        """使用されている数値の一覧を返す
        """
        nums = set()
        for _, d in self.G.nodes(data=True):
            if not d[AK_SKIP]:
                nums.add(d[AK_NUMBER])
        return sorted(list(nums))

    def get_edges_by_node(self, node, data=False) -> list:
        """指定したノードを持つエッジの一覧を返す
        """
        result = [
            e for e in self.G.edges(node, data)
        ]
        return result

    def check_puzzled_out_subgraph(self) -> bool:
        """解答完了したサブグラフをチェックして属性を設定する

        Returns:
            bool: 変更があればTrue
        """
        result = False
        G = self.G
        numlist = self.get_used_numbers_wo_skip()
        if 0 in numlist:
            numlist.remove(0)  # 0 を削除
        for num in numlist:
            nbunch = self.get_nodes_by_num_wo_skip(num)
            if len(nbunch) == 0:
                continue
            SG: nx.Graph = self.G.subgraph(nbunch)
            if num == 1:  # 数値が1の場合
                result = True
                self._set_attr_to_nodes_for_cpos(num, SG.nodes)
            else:  # 数値が1以外の場合
                for n in SG.nodes:
                    # 重複排除のためにスキップフラグの再チェック
                    if G.nodes[n][AK_SKIP]:
                        continue
                    ncc = nx.node_connected_component(SG, n)  # 非連結対策
                    if len(ncc) == num:  # 部分ノード数が数値と同じ
                        result = True
                        self._set_attr_to_nodes_for_cpos(num, ncc)
        return result

    def _set_attr_to_nodes_for_cpos(self, num: int, nodes):
        """check_puzzled_out_subgraphの補助関数
        """
        G = self.G
        for n in nodes:
            G.nodes[n][AK_SKIP] = True  # スキップフラグを立てる
            for n1, n2, ed in self.get_edges_by_node(n, data=True):
                if G.nodes[n1][AK_NUMBER] != G.nodes[n2][AK_NUMBER]:  # 数値が異なれば
                    ed[AK_WALL] = True  # 壁を貼る
                    nei = n2 if n1 == n else n1  # 隣接ノード
                    if G.nodes[nei][AK_NUMBER] == 0:  # 隣の数値が0ならば
                        G.nodes[nei][AK_DENYS].add(num)  # 拒否リストに追加

    def check_other_number_wall(self) -> bool:
        """隣接する数値が異なれば壁を貼る(0は除く)

        Returns:
            bool: 変更があればTrue
        """
        result = False
        nodes = [  # 0より大きい数値を持つノード一覧
            n for n, d in self.G.nodes(data=True)
            if not d[AK_SKIP] and d[AK_NUMBER] > 0
        ]
        G = self.G
        for n in nodes.copy():
            neighs = set(nx.neighbors(G, n))
            neighs &= set(nodes)
            for nei in neighs:
                if (not G.edges[n, nei][AK_WALL]
                        and G.nodes[n][AK_NUMBER] != G.nodes[nei][AK_NUMBER]):
                    G.edges[n, nei][AK_WALL] = True
                    result = True
            nodes.remove(n)
        return result

    def check_same_number_around_zero(self) -> bool:
        """0に隣接する同じ数字のグループの合計値が大きい場合は壁を貼る

        Returns:
            bool: 変更があればTrue
        """
        result = False
        G = self.G
        zero_nodes = self.get_nodes_by_num_wo_skip(0)
        SGwo = self.get_subgraph_wo_zero_nodes_and_wall_edges()
        for zn in zero_nodes:  # 0ノード一覧から
            neighs = set(G.neighbors(zn))
            neighs &= set(SGwo.nodes)
            subneighs = neighs.copy()
            for nei in neighs:  # 隣接ノードをチェック
                n = SGwo.nodes[nei][AK_NUMBER]
                count = len(nx.node_connected_component(SGwo, nei))  # カウント
                subneighs.remove(nei)
                for snei in subneighs:
                    if SGwo.nodes[snei][AK_NUMBER] == n:  # 同じ数値
                        count += len(nx.node_connected_component(SGwo, snei))  # カウント追加
                if count >= n:  # カウントが数値以上なら
                    G.nodes[zn][AK_DENYS].add(n)  # 拒否リストに追加
                    G.edges[zn, nei][AK_WALL] = True  # 壁を貼る
                    for snei in subneighs:  # 他の隣接ノードの
                        if SGwo.nodes[snei][AK_NUMBER] == n:  # 同じ数値に
                            G.edges[zn, snei][AK_WALL] = True  # 壁を貼る
        return result

    def get_subgraph_wo_zero_nodes_and_wall_edges(self) -> nx.Graph:
        """0と1ノードと壁エッジを除いたサブグラフを返す

        Notes:
            スキップフラグの立ったノードも含む
        """
        G = self.G
        nbunch = [
            n for n, nd in G.nodes(data=True)
            if nd[AK_NUMBER] != 0 and nd[AK_NUMBER] != 1
        ]
        SG: nx.Graph = G.subgraph(nbunch)
        ebunch = [
            (n1, n2) for n1, n2, de in SG.edges(data=True)
            if de[AK_WALL]
        ]
        result: nx.Graph = SG.copy()
        result.remove_edges_from(ebunch)
        return result

    def get_subgraph_wo_puzzled_out_and_wall_edges(self) -> nx.Graph:
        """完了済みノードと壁エッジを除いたサブグラフを返す
        """
        G = self.G
        nbunch = [
            n for n, nd in G.nodes(data=True)
            if not nd[AK_SKIP]
        ]
        SG: nx.Graph = G.subgraph(nbunch)
        ebunch = [
            (n1, n2) for n1, n2, ed in SG.edges(data=True)
            if ed[AK_WALL]
        ]
        result: nx.Graph = SG.copy()
        result.remove_edges_from(ebunch)
        return result

    def get_leaves(self) -> list:
        """葉ノード一覧を返す

        Returns:
            list: 葉ノードのリスト

        Notes:
            孤立ノードも含む
        """
        G = self.G
        result = [
            n for n in G.nodes()
            if G.degree[n] <= 1
        ]
        return result

    def get_nodes_from_leaf(self, leaf) -> list:
        """葉ノードから最初の分岐点(deg > 2)までを含むノードを返す
        """
        assert leaf is not None
        G = self.G
        result = [leaf]
        neighs = list(G.neighbors(leaf))
        if len(neighs) < 1:  # 葉ノードのみ
            return result
        old = leaf
        nei = neighs[0]
        result.append(nei)
        while G.degree[nei] == 2:
            neighs = list(G.neighbors(nei))
            old, nei = (nei, neighs[0]) if neighs[1] == old else (nei, neighs[1])
            if nei in result:
                break
            result.append(nei)
        return result

    def check_leaf_graphs(self, G: nx.Graph = None) -> bool:
        """葉ノードグラフを検証する

        Notes:
            後でcheck_puzzled_out_subgraph()やcheck_other_number_wall()を呼び出して
            skipフラグを建てる必要がある。
        """
        result = False
        if G is None:
            G = self.G
        foSGwo = graph(self.get_subgraph_wo_puzzled_out_and_wall_edges())
        leaves = foSGwo.get_leaves()
        for leaf in leaves:  # 葉ノード一覧
            nodes_from_leaf = foSGwo.get_nodes_from_leaf(leaf)
            LG: nx.Graph = foSGwo.G.subgraph(nodes_from_leaf)  # 葉ノードグラフを作成
            # dbgfog = graph(LG)
            # dbgfog.draw()
            # plt.show()
            # ノード数が1なら1確定
            nodesnum = LG.number_of_nodes()
            if nodesnum == 1:
                result = True
                G.nodes[leaf][AK_NUMBER] = 1
                continue
            # ノード数が2以上
            leafnum = LG.nodes[leaf][AK_NUMBER]
            count = 1
            num = leafnum
            old = leaf
            nei = next(LG.neighbors(leaf))
            if leafnum != 0:  # 葉ノードが数値を持つ場合
                while True:
                    neinum = LG.nodes[nei][AK_NUMBER]
                    if neinum == 0:
                        if num - count > 0:
                            result = True
                            G.nodes[nei][AK_NUMBER] = num
                        else:
                            break
                    neighs = list(LG.neighbors(nei))
                    if len(neighs) < 2:
                        break
                    old, nei = (nei, neighs[0]) if neighs[1] == old else (nei, neighs[1])
                    count += 1
            else:  # 葉ノードが0から始まる場合
                while True:
                    neinum = LG.nodes[nei][AK_NUMBER]
                    if neinum != 0:
                        num = neinum
                        if num - count <= 0:
                            break
                        while True:
                            neighs = list(LG.neighbors(nei))
                            if len(neighs) < 2:
                                break
                            old, nei = (nei, neighs[0]) if neighs[1] == old else (nei, neighs[1])
                            count += 1
                            neinum = LG.nodes[nei][AK_NUMBER]
                            if neinum == 0:
                                if num - count > 0:
                                    result = True
                                    G.nodes[nei][AK_NUMBER] = num
                                else:
                                    break
                    else:
                        count += 1
                    neighs = list(LG.neighbors(nei))
                    if len(neighs) < 2:
                        break
                    old, nei = (nei, neighs[0]) if neighs[1] == old else (nei, neighs[1])
        return result

    def check_disconneced_subgraph(self):
        """連結グラフに分割して検証する
        """
        result = False
        G = self.G
        foSGwo = graph(self.get_subgraph_wo_puzzled_out_and_wall_edges())
        SGs = foSGwo.get_connected_subgraphs()
        for SG in SGs:
            node_num = SG.number_of_nodes()
            if node_num <= 2:  # 2以下
                for n, d in SG.nodes.data():  # 各ノード
                    if d[AK_NUMBER] == 0:
                        G.nodes[n][AK_NUMBER] = node_num
                        result = True
                    elif d[AK_NUMBER] != node_num:
                        # ありえない数値なのでエラー
                        raise WrongAnswerError(
                            f'Wrong answer errpr: Expect {node_num}, but {d[AK_NUMBER]}')
        return result

    def check_zero_single_connected_subgrapha(self) -> bool:
        """1種類の0以外の数値と0を持つ連結なグラフに分割して検証する
        """
        result = False
        from .zero_and_single_number_graph import zero_and_single_number_graph
        fogdic = zero_and_single_number_graph.create(self)
        for fogl in fogdic.values():
            for fog in fogl:
                if fog.solve():
                    result = True
                    fog.upload(self)
        return result

    def check_4n_2c(self) -> bool:
        result = False
        from .zero_and_single_number_graph import zero_and_single_number_graph
        fogdic = zero_and_single_number_graph.create(self)
        for num, fogl in fogdic.items():
            if num < 4:
                continue
            for fog in fogl:
                if fog.solve_4n_2c():
                    result = True
                    fog.upload(self)
        return result

    def check_after_check(self) -> bool:
        result = False
        result |= self.check_puzzled_out_subgraph()
        result |= self.check_other_number_wall()
        result |= self.check_same_number_around_zero()
        return result
