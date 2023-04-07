from dataclasses import dataclass, field
from enum import Enum, auto
import functools
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable, Optional, List, Type, Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from .cache import hash_data

class NodeState(Enum):
    DEFAULT = auto()
    SKIP = auto()
    RERUN = auto()


class Node:
    def __init__(self,
                 func: Callable,
                 name: Optional[str] = None,
                 cache: Optional[Any] = None,
                 state: NodeState = NodeState.DEFAULT,
                 ignore_args: Optional[list] = None,
                 device_idx: Optional[int] = None,
                 verbose: bool = False,

    ):
        self.func = func
        self.name = name or self.func.__name__
        functools.update_wrapper(self, func) # https://github.com/GrahamDumpleton/wrapt/blob/develop/blog/01-how-you-implemented-your-python-decorator-is-wrong.md
        self.cache = cache
        self.state = state
        self.ignore_args = ignore_args or [] # Ignore for the purpose of caching
        self.device_idx = device_idx
        self.verbose = verbose

    def get_key(self, *args, **kwargs):
        bound_args = inspect.signature(self.func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        args_dict = bound_args.arguments
        if 'self' in args_dict:
            args_dict.pop('self')

        for k in self.ignore_args:
            if k in args_dict:
                args_dict.pop(k)
        # Add source code
        func_src = inspect.getsource(self.func)
        return f'{self.func.__name__}({hash_data([func_src, args_dict])})'

    def __call__(self, *args, **kwargs):
        if self.state == NodeState.SKIP:
            return None

        if self.cache:
            key = self.get_key(*args, **kwargs)
            if self.verbose:
                print(f'> key: {key}')
            output = None
            if self.state == NodeState.RERUN:
                output = self.func(*args, **kwargs)
            else:
                # Try to load from the cache
                if self.verbose:
                    print(f'Loading cached output of {self.func.__name__}')
                    if hasattr(self.cache, 'filepath'):
                        print(f'> Attempting load from {self.cache.filepath}')
                output = self.cache.load(
                    key=key,
                    device_idx=self.device_idx
                )
                if output is not None:
                    if self.verbose:
                        print('> Load succeeded.')
                    return output
                if self.verbose:
                    print('> Load failed, recomputing...')
                output = self.func(*args, **kwargs)
            # Add to the cache
            self.cache.store(
                key=key,
                data=output
            )

            return output
        return self.func(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}(' \
            + f'func={self.func.__name__}, ' \
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
            return self._add(func, deps, **node_kwargs)
        return wrapper

    def _add(self, func, deps, **node_kwargs):
        node = Node(func, **node_kwargs)
        self.add_node(node, deps)
        return node

    def add_node(
            self,
            node: Node,
            deps: List[Node],
        ):

        self.graph.add_node(node.name, node=node)
        for dep in deps:
            assert isinstance(dep, Node), f'dep {dep} must be a node'
            self.graph.add_edge(dep.name, node.name)
        return node

    def configure_deps(self, targets, reruns):
        """
        targets: list of nodes whose outputs we want (None = all nodes)
        reruns: list of nodes to force rerun
        """
        assert nx.is_directed_acyclic_graph(self.graph)
        if len(targets) != 0:
            all_ancestors = set()
            for target in targets:
                all_ancestors.update(nx.ancestors(self.graph, target))
                all_ancestors.add(target)

            for node in self.graph.nodes:
                if node not in all_ancestors:
                    self.graph.nodes[node]['node'].state = NodeState.SKIP

            rungraph = self.graph.subgraph(all_ancestors)
        else:
            rungraph = self.graph

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

    def set_cache_dir(self, cache_dir: Path):
        def configure(node):
            if node.cache is not None:
                node.cache.cache_dir = cache_dir
            return node
        self.configure_nodes(func=configure)

    def set_verbose(self, verbose: bool):
        def configure(node):
            node.verbose = verbose
            return node
        self.configure_nodes(func=configure)

    def set_device_idx(self, device_idx: int):
        def configure(node):
            node.device_idx = device_idx
            return node
        self.configure_nodes(func=configure)

    def configure_nodes(self, func, nodes=None):
        """
        func: inplace function to apply to seleted node objects
        nodes: function to decide to configure the node or not
        (None = all nodes)
        """
        for node in self.graph.nodes:
            if ((nodes is None)
                 or (nodes is not None and node in nodes)):
                node_obj = self.graph.nodes[node]['node']
                self.graph.nodes[node]['node'] = \
                    func(node_obj)

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
            shortest_paths[root]['to_root'] = 0
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
