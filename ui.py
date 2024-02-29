from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from constants import *
from solver2 import FieldState, PuzzleSolver


@dataclass
class Graph:
    graph: nx.Graph = None

    def set_numbers(self, numbers: List[List[int]]) -> None:
        """Sets numbers to the graph."""
        for node, data in self.graph.nodes(data=True):
            m, n = node
            if len(numbers) > m and len(numbers[m]) > n:
                data[NUMBER] = numbers[m][n]

    def set_attributes(self) -> None:
        """Sets various attributes for plotting."""
        for _, nd in self.graph.nodes(data=True):
            n = nd[NUMBER]
            nd[LABEL] = n
            nd[COLOR] = (0.94,) * 3 if n == 0 else self._calculate_color(n)
        for n1, n2, ed in self.graph.edges(data=True):
            if ed[WALL]:
                ed[LABEL] = "x"
                ed[COLOR] = (0.95,) * 3
                ed[WIDTH] = 1
            else:
                self._set_edge_color_and_width(n1, n2, ed)

    @staticmethod
    def _calculate_color(n: int) -> Tuple[float, float, float]:
        """Calculates color based on the number."""
        r = ((n & 0b001) | ((n >> 3) & 0b001)) * 0.12 + 0.54
        g = (((n >> 1) & 0b001) | ((n >> 4) & 0b001)) * 0.12 + 0.54
        b = (((n >> 2) & 0b001) | ((n >> 5) & 0b001)) * 0.12 + 0.54
        return r, g, b

    def _set_edge_color_and_width(
        self, n1: Tuple[int, int], n2: Tuple[int, int], ed: Dict[str, any]
    ) -> None:
        """Sets color and width for edges."""
        if (
            self.graph.nodes[n1][NUMBER] != 0
            and self.graph.nodes[n1][NUMBER] == self.graph.nodes[n2][NUMBER]
        ):
            ed[COLOR] = self.graph.nodes[n1][COLOR]
            ed[WIDTH] = 6
        else:
            ed[COLOR] = "maroon"
            ed[WIDTH] = 1

    def draw(self, figsize: Tuple[int, int] = (10, 10)) -> None:
        """Draws the graph."""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        ax.invert_yaxis()
        self.set_attributes()
        pos = {(x, y): (y, x) for x, y in self.graph.nodes()}
        nlabels = nx.get_node_attributes(self.graph, LABEL)
        ncolors = list(nx.get_node_attributes(self.graph, COLOR).values())
        ecolors = list(nx.get_edge_attributes(self.graph, COLOR).values())
        widths = list(nx.get_edge_attributes(self.graph, WIDTH).values())
        nx.draw(
            self.graph,
            pos,
            ax,
            labels=nlabels,
            node_color=ncolors,
            edge_color=ecolors,
            with_labels=True,
            node_size=600,
            width=widths,
        )
        elabels = nx.get_edge_attributes(self.graph, LABEL)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=elabels, font_size=6)
        plt.axis("on")
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)


@dataclass
class MasterGraph(Graph):
    """Represents a master graph used in the puzzle."""

    _graph: nx.Graph = field(default=None, init=False)
    _rows: int = 0
    _cols: int = 0

    def __post_init__(self):
        """Post-initialization method."""
        self._create_matrix()
        self._initialize_attributes()

    def _create_matrix(self) -> None:
        """Creates the grid matrix."""
        assert self._rows > 0 and self._cols > 0
        self.graph = nx.grid_2d_graph(self._rows, self._cols)

    def _initialize_attributes(self) -> None:
        """Initializes node and edge attributes."""
        for n, nd in self.graph.nodes(data=True):
            nd[NUMBER] = 0
            nd[SKIP] = False
            nd[DENY] = set()
        for _, _, ed in self.graph.edges(data=True):
            ed[WALL] = False

    def solve_puzzle(self) -> None:
        """Solves the puzzle using PuzzleSolver."""
        state = FieldState.from_list_to_state(
            [
                [self.graph.nodes[(i, j)][NUMBER] for j in range(self._cols)]
                for i in range(self._rows)
            ]
        )
        solver = PuzzleSolver(state)
        solver.solve()
        solved_matrix = [
            [solver.field_state.get_state((i, j)) for j in range(self._cols)]
            for i in range(self._rows)
        ]
        self.set_numbers(solved_matrix)

    def set_walls_for_neighbors(self) -> None:
        for n1, n2, data in self.graph.edges(data=True):
            if self.graph.nodes[n1][NUMBER] != 0 and self.graph.nodes[n2][NUMBER] != 0:
                if self.graph.nodes[n1][NUMBER] != self.graph.nodes[n2][NUMBER]:
                    data[WALL] = True
