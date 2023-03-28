"""Note: generated with help from ChatGPT"""
import json
import hashlib

import numpy as np

class DAG:
    def __init__(self, force_recompute=None, cache_file=None):
        self.nodes = []
        self.edges = []
        self.force_recompute = force_recompute or {}
        self.cache_filename = cache_file or 'cache.npz'

    def add_node(self, func, args=None, kwargs=None, deps=None):
        args = args or ()
        kwargs = kwargs or {}
        deps = deps or []

        for node in self.nodes:
            if node.func == func and node.args == args:
                return node

        node = Node(func, args, kwargs)
        self.nodes.append(node)

        for input_node in deps:
            self.edges.append((input_node, node))

        return node

    def topological_sort(self):
        # Initialize the list of nodes with no incoming edges
        roots = [node for node in self.nodes if not any(node == edge[1] for edge in self.edges)]

        # Initialize the list to store the sorted nodes
        sorted_nodes = []

        # Process each node in the list of roots
        while roots:
            # Pop a root node from the list
            root = roots.pop()

            # Add the node to the sorted list
            sorted_nodes.append(root)

            # Remove outgoing edges from the node
            outgoing_edges = [edge for edge in self.edges if edge[0] == root]
            for edge in outgoing_edges:
                self.edges.remove(edge)

                # If the target node of the edge has no incoming edges, add it to the list of roots
                if not any(edge[1] == next_edge[1] for next_edge in self.edges):
                    roots.append(edge[1])

        # If there are remaining edges, the graph contains a cycle
        if self.edges:
            raise ValueError("DAG contains a cycle")

        # Return the sorted nodes
        return sorted_nodes

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

    def load_cache(self):
        # Load the computed outputs from a NumPy .npz file
        try:
            cache = np.load(self.cache_filename)
        except FileNotFoundError:
            return

        for node in self.nodes:
            if node.id in cache and node.id not in self.force_recompute:
                node.output = cache[node.id]


    def plot(self):
        # Plot the DAG in an ASCII format
        nodes = {node.label: node for node in self.nodes}
        edges = [(src_node.label, dst_node.label) for src_node, dst_node in self.edges]
        sorted_nodes = [node.label for node in self.topological_sort()]
        node_order = {node_label: i for i, node_label in enumerate(sorted_nodes)}
        print(node_order)
        max_depth = max(node_order.values())
        node_width = max(max(len(str(node.label)) for node in self.nodes), 1)
        #output_width = max(max(len(str(node.output)) for node in self.nodes if node.output is not None), 7)
        output_width = 1

        lines = []
        for i in range(max_depth + 1):
            line = []
            for j in range(len(self.nodes)):
                node_label = sorted_nodes[j]
                if node_order[node_label] != i:
                    line.append(' ' * (node_width + output_width + 5))
                else:
                    id_str = str(node_label).ljust(node_width)
                    # if node.output is None:
                    #     output_str = ' ' * output_width
                    # else:
                    #     output_str = str(node.output).ljust(output_width)
                    output_str = '(out)'
                    line.append(f'{id_str} | {output_str}')
            lines.append(' '.join(line))

        for src_node_label, dest_node_label in edges:
            src_idx = sorted_nodes.index(src_node_label)
            dest_idx = sorted_nodes.index(dest_node_label)
            if node_order[src_node_label] >= node_order[dest_node_label]:
                src_idx, dest_idx = dest_idx, src_idx
            line = lines[node_order[src_node_label]]
            start = node_width + output_width + 1 * src_idx
            end = node_width + output_width + 1 * dest_idx + node_width
            line = line[:start] + '-' * (end - start) + line[end:]
            lines[node_order[src_node_label]] = line

        for line in lines:
            print(line)


class Node:
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.output = None

    @property
    def id(self):
        return (self.func.__name__,
                hash_data((self.args, self.kwargs)))

    @property
    def label(self):
        return (self.func.__name__, hash_data((self.args, self.kwargs))[:6])

    def compute_output(self):
        # Compute the output of the node by calling the stored function with the stored arguments
        self.output = self.func(*self.args, **self.kwargs)
        return self.output

    def __repr__(self):
        return f'{self.__class__.__name__}{self.label}'

def hash_data(data):
    data_md5 = hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
    return data_md5
