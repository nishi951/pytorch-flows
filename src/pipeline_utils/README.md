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
The cache defines the loading and storing behavior. A `NpzCache` object is
provided to take advantage of the fast read/write of the numpy format.
Furthermore, callbacks can be given (which take the data objects in question, as
well as any runtime variables, which can be passed via the pipeline object) to
control the storing and loading of cache variables.

Various helper functions are also available in `pipeline.conversion` for moving
structures of arrays on and off the GPU.

## Runtime and configuration
Using the `pipeline.PipelineConfig` dataclass as a template, we configure the
pipeline to support `targets` and `reruns`. We further allow the pipeline to be
configured with variables at runtime (e.g. the device indices of GPUs to load
cached data to). All this functionality (i.e. anything related to the runtime
behavior) should be put in the `pipeline.setup` method.

