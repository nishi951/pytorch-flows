import hashlib
import json
from pathlib import Path
from typing import Callable, Optional, List, Type, Union

import networkx as nx
import numpy as np

class Node:
    def __init__(self,
                 func: Callable,
                 cache: Optional[Callable] = None,
                 force_recompute: bool = False):
        self.func = func
        self.cache = cache
        self.force_recompute = force_recompute

    def __call__(self, *args, **kwargs):
        if self.cache:
            output = None
            if self.force_recompute:
                output = self.func(*args, **kwargs)
            else:
                # Try to load from the cache
                output = self.cache.load(
                    self.func,
                    args,
                    kwargs,
                )
                if output is not None:
                    return output

                output = self.func(*args, **kwargs)
            # Add to the cache
            self.cache.store(
                self.func,
                args,
                kwargs,
                output,
            )

            return output
        else:
            return self.func(*args, **kwargs)

class DataPipeline:
    def __init__(self, force_recompute=None):
        self.graph = nx.DiGraph()
        self.force_recompute = force_recompute or {}


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

        self.graph.add_node(node)
        for dep in deps:
            self.graph.add_edge(dep, node)

        return node

    def compute(self):
        # Compute the outputs for all nodes in the DAG in topological order
        for node in self.topological_sort():
            if node.id in self.force_recompute:
                node.output = None
            if node.output is None:
                node.compute_output()

        # Save the computed outputs to a NumPy .npz file
        cache = {node.id: node.output for node in self.nodes if node.output is not None}
        np.savez_compressed(self.cache_filename, **cache)
