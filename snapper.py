from functools import wraps
import yaml
import os
import json

from functools import update_wrapper
import os
import joblib
from difflib import Differ


class Snapper:
    def __init__(self, func, compare_conds=True):
        self.func = func
        update_wrapper(self, func)
        self.compare_conds = compare_conds
        self.dump_conds = not compare_conds
        self.snap_dir = "data/snapper/snapshots"
        self.func_name = self.func.__name__
        self.snap_file = f"{self.snap_dir}/{self.func_name}.pkl"

    def dump(
        self,
        result,
        *args,
        **kwargs,
    ):
        print(f"Dumping snapshot for {self.func_name}")
        snap_shot = f"{self.snap_dir}/{self.func_name}.pkl"
        joblib.dump((result, args, kwargs), snap_shot)

    def load(self):
        snap_shot = f"{self.snap_dir}/{self.func_name}.pkl"
        if os.path.exists(snap_shot):
            return joblib.load(snap_shot)
        else:
            print(f"No snapshot found for {self.func_name}")
            return 0, 0, 0

    def compare_args(self, args, old_args):
        new_args = set(args)
        old_args = set(old_args)
        added_args = new_args - old_args
        removed_args = old_args - new_args
        if added_args:
            print(f"Added positional arguments : {added_args}")
        if removed_args:
            print(f"Removed positional arguments: {removed_args}")
        for arg, old_arg in zip(args, old_args):
            if arg != old_arg:
                return False
        return True

    def compare_kwargs(self, kwargs, old_kwargs):
        new_kws = set(kwargs.keys())
        old_kws = set(old_kwargs.keys())
        added_kws = new_kws - old_kws
        removed_kws = old_kws - new_kws

        if added_kws:
            print(f"Added keyword arguments : {added_kws}")

        if removed_kws:
            print(f"Removed keyword arguments: {removed_kws}")

        for key, value in kwargs.items():
            if key not in old_kwargs:
                return False
            else:
                if value != old_kwargs[key]:
                    return False
        return True

    def compare_result(self, result, old_result):
        return Differ().compare(result, old_result)

    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        if self.compare_conds:
            old_result, old_args, old_kwargs = self.load()
            if old_result == 0 and old_args == 0 and old_kwargs == 0:
                print("No snapshot found")

        if self.dump_conds:
            self.dump(result, *args, **kwargs)

        if self.compare_conds:
            if not self.compare_args(args, old_args):
                print("Arguments have changed")
            if not self.compare_kwargs(kwargs, old_kwargs):
                print("Keyword arguments have changed")
            if not self.compare_result(result, old_result):
                print("Result has changed")
            else:
                print("Result has not changed")

        return result

    def __repr__(self):
        return self.func.__repr__()


def snapper(compare_conds=True):
    def decorator(func):
        return Snapper(func, compare_conds)

    return decorator


# Example usage of the Snapper decorator
@snapper(compare_conds=True)
def example_function(a, b):
    c = a + b
    d = c + 2
    return d


example_function(1, 2)  # Call the function with arguments
