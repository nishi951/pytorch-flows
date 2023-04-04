# Pipeline Utils
This package contains functions for establishing a pipeline of functions where
each function's output can be cached and loaded from the cache to avoid
recomputation.

See `test/test_pipeline.py` for an example of how to use these functions.

## Creating a pipeline
To create a pipeline, use the `pipeline.DataPipeline` class. Recommended usage
is to create the pipeline once for each script.

## Adding nodes to the pipeline
Once the pipeline has been created, we use `pipeline.add` decorator to add nodes
to the pipeline. Doing this creates and configures a node for the function.

## Nodes
Nodes are relatively simple - they consist of a function to be called, a cache
object to store previously computed stuff, and a state that defines the runtime
behavior according to whether the function is needed or not.

## Cache
The cache defines the loading and storing behavior. 

Cache types:
- `NpzCache`: Uses `np.savez_compressed` and `np.load` as backend.
  - Good for when
- `PklCache`: Uses `cPickle` or `pickle` as backend.

Various helper functions are also available in `pipeline.conversion` for moving
structures of arrays on and off the GPU.

Conversion supports the following nested structures:
- dictionaries
- tuples
- dataclasses

However, it does not support general nesting of objects (e.g. pytorch modules).

### Hashing
When determining if an array has been 

### Saving and Loading CuPy/Torch arrays from GPU



