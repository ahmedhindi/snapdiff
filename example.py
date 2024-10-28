from snapdiff.utils import (
    load_snapper_config,
    get_state,
    compare_kwargs,
    add_decorator_to_functions,
)


import inspect
import os

a = inspect.getfile(get_state)

# ignore the paths before current directory

a = os.path.relpath(a, start=os.getcwd())

print(a)
