from __future__ import annotations

from itertools import chain
from typing import Union, List, Dict

import networkx as nx

from .graph import Graph
from .label import DENYS, NUMBER


class ZeroAndSingleNumberGraph(Graph):
    @classmethod
    def create(cls, origin: Union[nx.Graph, Graph]) -> Dict[int, List[ZeroAndSingleNumberGraph]]:
        """Create ZeroAndSingleNumberGraph instances from an origin_graph Graph.

        Args:
            origin (Union[nx.Graph, Graph]): The original Graph.

        Returns:
            Dict[int, List[ZeroAndSingleNumberGraph]]: A dictionary containing lists of ZeroAndSingleNumberGraph instances indexed by number.
        """
        assert origin is not None
        if isinstance(origin, Graph):
            origin_graph = origin
        elif isinstance(origin, nx.Graph):
            origin_graph = Graph(origin)
        else:
            raise TypeError('origin_graph should be of type Graph or nx.Graph')

        result: Dict[int, List[cls]] = {}
        foSGwo = Graph(origin_graph.get_subgraph_wo_puzzled_out_and_wall_edges())

        if foSGwo.graph.number_of_nodes() == 0:
            return result

        # Get list of used numbers without skipping
        numlist = foSGwo.get_used_numbers_wo_skip()
        if 0 in numlist:
            numlist.remove(0)  # Remove 0 from the list

        # Create for each number
        for num in numlist:
            zero_nodes = [
                n for n, d in foSGwo.nodes.data()
                if d[NUMBER] == 0 and num not in d[DENYS]
            ]

            num_nodes = Graph.get_nodes_by_num(foSGwo.graph, num)
            subgraph = foSGwo.graph.subgraph(sorted(chain(num_nodes, zero_nodes)))
            result[num] = []

            for component in nx.connected_components(subgraph):
                fog = cls(subgraph.subgraph(component).copy())
                assert fog.validate()

                if any([d == num for _, d in fog.nodes.data(NUMBER, 0)]):
                    result[num].append(fog)

        return result

    def validate(self) -> bool:
        """Validate the Graph.

        Returns:
            bool: True if the Graph is valid.
        """
        assert self.graph is not None
        result = True
        nums_dict = dict(self.graph.nodes.data(NUMBER, 0))
        nums = set(nums_dict.values())
        if 0 in nums:
            nums.remove(0)

        if len(nums) > 1:
            result = False

        return result
