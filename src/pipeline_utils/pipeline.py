from dataclasses import dataclass, field
from enum import Enum, auto
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Optional, List, Type, Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from .conversion import Np2Torch, Np2Cupy


class NodeState(Enum):
    DEFAULT = auto()
    SKIP = auto()
    RERUN = auto()


class Node:
    def __init__(self,
                 func: Callable,
                 cache: Optional[Any] = None,
                 state: NodeState = NodeState.DEFAULT,
                 device_idx: Optional[int] = None

    ):
        self.func = func
        self.cache = cache
        self.state = state
        self.device_idx = device_idx

    def __call__(self, *args, **kwargs):
        if self.state == NodeState.SKIP:
            return None

        if self.cache:
            output = None
            if self.state == NodeState.RERUN:
                output = self.func(*args, **kwargs)
            else:
                # Try to load from the cache
                output = self.cache.load(
                    data=(self.func, args, kwargs),
                    device_idx=self.device_idx
                )
                if output is not None:
                    return output

                output = self.func(*args, **kwargs)
            # Add to the cache
            self.cache.store(
                data=(self.func, args, kwargs, output),
            )

            return output
        return self.func(*args, **kwargs)

    @property
    def name(self):
        return self.func.__name__

    def __repr__(self):
        return f'{self.__class__.__name__}(' \
            + f'func={self.name}, ' \
            + f'cache={self.cache}, ' \
            + f'state={self.state}' \
            + ')'



@dataclass
class PipelineConfig:
    targets: list[str] = field(default_factory=list)
    reruns: list[str] = field(default_factory=list)


class DataPipeline:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add(self, deps, **node_kwargs):
        """Decorator version"""
        def wrapper(func):
            node = Node(func, **node_kwargs)
            self.add_node(node, deps)
            return node
        return wrapper

    def add_node(
            self,
            node: Node,
            deps: List[Node],
        ):

        self.graph.add_node(node.name, node=node)
        for dep in deps:
            self.graph.add_edge(dep.name, node.name)

        return node

    def configure_deps(self, targets, reruns):
        """
        targets: list of nodes whose outputs we want (None = all nodes)
        reruns: list of nodes to force rerun
        """
        assert nx.is_directed_acyclic_graph(self.graph)
        if len(targets) == 0 :
            return

        all_ancestors = set()
        for target in targets:
            all_ancestors.update(nx.ancestors(self.graph, target))
            all_ancestors.add(target)

        for node in self.graph.nodes:
            if node not in all_ancestors:
                self.graph.nodes[node]['node'].state = NodeState.SKIP

        rungraph = self.graph.subgraph(all_ancestors)
        for rerun in reruns:
            if rerun in rungraph:
                self.graph.nodes[rerun]['node'].state = NodeState.RERUN
                # Set all descendants to rerun
                for descendant in nx.descendants(rungraph, rerun):
                    self.graph.nodes[descendant]['node'].state = NodeState.RERUN
            else:
                print(
                    f'Warning: Requested rerun for unnecessary node {rerun} for targets {targets}'
                )

        return rungraph

    def configure_nodes(self, func, nodes=None):
        """
        func: function to apply to seleted node objects
        nodes: function to decide to configure the node or not
        (None = all nodes)
        """
        for node in self.graph.nodes:
            if nodes and node in nodes:
                node_obj = self.graph.nodes[node]['node']
                self.graph.nodes[node]['node'] = func(node_obj)

    def set_global_cache_dir(self, cache_dir: Path):
        """Convenience function for setting the cache dirs of all nodes"""
        for node in self.graph.nodes:
            cache = self.graph.nodes[node]['node'].cache
            if cache:
                cache.cache_dir = cache_dir


    def visualize(self):
        """Visualize pipeline as a multipartite networkx graph"""
        # Compute partition as the minimum distance to a "root" node
        roots = [node for node, d in self.graph.in_degree() if d == 0]
        shortest_paths = {node: {'to_root': np.Inf} for node in self.graph.nodes}
        for root in roots:
            shortest_to_root = nx.single_source_shortest_path_length(self.graph, root)
            for node, dist in shortest_to_root.items():
                if dist < shortest_paths[node]['to_root']:
                    shortest_paths[node]['to_root']= dist
            shortest_paths[root]['to_root'] =0
        nx.set_node_attributes(self.graph, shortest_paths)
        pos = nx.multipartite_layout(
            self.graph,
            subset_key='to_root',
        )

        # Color
        def status_cmap(node):
            if node.state == NodeState.DEFAULT:
                return 'blue'
            elif node.state == NodeState.RERUN:
                return 'red'
            elif node.state == NodeState.SKIP:
                return 'white'
            else:
                return 'black'

        node_color = [status_cmap(node) for _, node in self.graph.nodes(data='node')]

        nx.draw_networkx(
            self.graph,
            pos=pos,
            node_color=node_color,

        )
        plt.show()
