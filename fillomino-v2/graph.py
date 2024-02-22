from dataclasses import dataclass
import networkx as nx
from matplotlib import pyplot as plt
from .label import *


@dataclass
class Graph:
    _graph: nx.Graph = None

    @property
    def graph(self) -> nx.Graph:
        return self._graph

    @property
    def nodes(self):
        return self.graph.nodes

    @staticmethod
    def get_nodes_by_num(graph: nx.Graph, num: int) -> list:
        """Returns a list of nodes with a specific number from the graph."""
        result = [
            n for n, d in graph.nodes.data()
            if d[NUMBER] == num
        ]
        return result

    def set_numbers(self, numbers: list[list[int]]) -> None:
        """Sets numbers to the graph.

        Note:
            Skips if the node does not exist.
        """
        assert numbers is not None
        assert self.graph is not None
        for node, data in self.graph.nodes(data=True):
            m, n = node
            if len(numbers) > m and len(numbers[m]) > n:
                data[NUMBER] = numbers[m][n]

    def set_attributes(self) -> None:
        """Sets various attributes for plotting."""
        for _, nd in self.graph.nodes(data=True):
            n = nd[NUMBER]
            nd[LABEL] = n
            # Set color based on the number
            if n == 0:
                nd[COLOR] = (0.94,) * 3
            else:
                n -= 0
                f = 0b1
                r = (n & f) | ((n >> 3) & f)
                g = ((n >> 1) & f) | ((n >> 4) & f)
                b = ((n >> 2) & f) | ((n >> 5) & f)
                multi = 0.12
                bias = 0.9 - multi * 3
                nd[COLOR] = (
                    multi * r + bias % 1,
                    multi * g + bias % 1,
                    multi * b + bias % 1
                )
        # Edges
        for n1, n2, ed in self.graph.edges(data=True):
            # Set wall
            if ed[WALL]:
                ed[LABEL] = 'x'
                ed[COLOR] = (0.95,) * 3
                ed[WIDTH] = 1
            else:
                ed[LABEL] = ''
                if (self.graph.nodes[n1][NUMBER] != 0
                        and self.graph.nodes[n1][NUMBER] == self.graph.nodes[n2][NUMBER]):
                    ed[COLOR] = self.graph.nodes[n1][COLOR]
                    ed[WIDTH] = 6
                else:
                    ed[COLOR] = 'maroon'
                    ed[WIDTH] = 1

    def draw(self, figsize: tuple[float, float] = (10, 10)) -> None:
        """Draws the graph."""
        fig = plt.figure(figsize=figsize)
        # Set minimum/maximum values of node coordinates
        ml, nl = {0}, {0}
        for node in self.graph.nodes():
            ml.add(node[0])
            nl.add(node[1])
        # Set axes and axis ticks
        ax = fig.add_subplot(
            xticks=[x for x in range(min(ml), max(ml) + 1, 1)],
            yticks=[y for y in range(min(nl), max(nl) + 1, 1)],
        )
        # Invert Y-axis
        ax.invert_yaxis()
        graph = self.graph
        pos = {(x, y): (y, x) for x, y in graph.nodes()}
        self.set_attributes()
        nlabels = nx.get_node_attributes(graph, LABEL)
        ncolors = list(nx.get_node_attributes(graph, COLOR).values())
        ecolors = list(nx.get_edge_attributes(graph, COLOR).values())
        widths = list(nx.get_edge_attributes(graph, WIDTH).values())
        nx.draw(
            graph, pos, ax,
            labels=nlabels,
            node_color=ncolors,
            edge_color=ecolors,
            with_labels=True,
            node_size=600,
            width=widths
        )
        elabels = nx.get_edge_attributes(graph, LABEL)
        nx.draw_networkx_edge_labels(
            graph, pos,
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

    def get_used_numbers_wo_skip(self) -> list[int]:
        """Returns a list of used numbers without skip."""
        nums = set()
        for _, d in self.graph.nodes(data=True):
            if not d[SKIP]:
                nums.add(d[NUMBER])
        return sorted(list(nums))


    def get_subgraph_wo_puzzled_out_and_wall_edges(self) -> nx.Graph:
        """Returns a subgraph without completed nodes and wall edges."""
        graph = self.graph
        nbunch = [
            n for n, nd in graph.nodes(data=True)
            if not nd[SKIP]
        ]
        subgraph: nx.Graph = graph.subgraph(nbunch)
        ebunch = [
            (n1, n2) for n1, n2, ed in subgraph.edges(data=True)
            if ed[WALL]
        ]
        result: nx.Graph = subgraph.copy()
        result.remove_edges_from(ebunch)
        return result