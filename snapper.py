import os
from functools import update_wrapper
import joblib
from deepdiff import DeepDiff
from snapdiff.utils import compare_args, compare_kwargs


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

    def compare_result(self, result, old_result):
        return DeepDiff(result, old_result)

    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        if self.compare_conds:
            old_result, old_args, old_kwargs = self.load()
            if old_result == 0 and old_args == 0 and old_kwargs == 0:
                print("No snapshot found")

        if self.dump_conds:
            self.dump(result, *args, **kwargs)

        if self.compare_conds:
            if not compare_args(args, old_args):
                print("Arguments have changed")
            if not compare_kwargs(kwargs, old_kwargs):
                print("Keyword arguments have changed")
            res_diff = self.compare_result(result, old_result)
            if res_diff:
                print("Result has changed", res_diff)
            else:
                print("Result has not changed")

        return result

    def __repr__(self):
        return self.func.__repr__()


def snapper(compare_conds=True):
    def decorator(func):
        return Snapper(func, compare_conds)

    return decorator


@snapper(compare_conds=True)
def example_function(a, b):
    c = a + b
    d = c + 2
    return d


example_function(1, 2)
