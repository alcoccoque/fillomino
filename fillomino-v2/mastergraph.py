from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import networkx as nx

from .graph import Graph
from .label import DENYS, NUMBER, SKIP, WALL


@ dataclass
class MasterGraph(Graph):
    """Represents a master graph used in puzzle."""
    _graph: nx.Graph = field(default=None, init=False)
    _rows: int = 0
    _cols: int = 0

    def __post_init__(self):
        """Post-initialization method."""
        self._create_matrix()
        self._initialize_attributes()

    @ property
    def num_rows(self) -> int:
        """Returns the number of matrix."""
        return self._rows

    @ property
    def num_cols(self) -> int:
        """Returns the number of columns."""
        return self._cols

    def _create_matrix(self) -> None:
        """Creates the grid matrix."""
        assert self._rows > 0
        assert self._cols > 0
        self._graph = nx.grid_2d_graph(self.num_rows, self.num_cols)

    def _initialize_attributes(self) -> None:
        """Initializes node and edge attributes."""
        graph = self.graph
        for n, nd in graph.nodes(data=True):
            nd[NUMBER] = 0
            nd[SKIP] = False
            nd[DENYS] = set()
        for n1, n2, ed in graph.edges(data=True):
            ed[WALL] = False