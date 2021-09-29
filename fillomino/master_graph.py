#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>
from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx

from .graph import graph
from .label import AK_DENYS, AK_NUMBER, AK_SKIP, AK_WALL


@ dataclass
class master_graph(graph):
    """docstring
    """
    _graph: nx.Graph = field(default=None, init=False)
    _rows: int = 0
    _cols: int = 0

    def __post_init__(self):
        self._create_matrix()
        self._init_attributes()

    @ property
    def rows(self) -> int:
        return self._rows

    @ property
    def cols(self) -> int:
        return self._cols

    def _create_matrix(self) -> None:
        """docstring
        """
        assert self._rows > 0
        assert self._cols > 0
        self._graph = nx.grid_2d_graph(self.rows, self.cols)

    def _init_attributes(self) -> None:
        G = self.G
        # ノード属性の初期値
        for n, nd in G.nodes(data=True):
            nd[AK_NUMBER] = 0
            nd[AK_SKIP] = False
            nd[AK_DENYS] = set()
        # エッジ属性の初期値
        for n1, n2, ed in G.edges(data=True):
            ed[AK_WALL] = False
