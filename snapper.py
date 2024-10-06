import os
from functools import update_wrapper
import joblib
from deepdiff import DeepDiff
from snapdiff.utils import compare_args, compare_kwargs
import logging


# Logger configuration function
def setup_logger(log_to_file=True, log_filename="snapper.log"):
    logger = logging.getLogger("SnapperLogger")
    logger.setLevel(logging.INFO)

    # Create formatter with structured logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"
    )

    # Create console handler or file handler based on the user's choice
    if log_to_file:
        handler = logging.FileHandler(log_filename)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Snapper Class
class Snapper:
    def __init__(self, func, compare_conds=True, log_to_file=True):
        self.func = func
        update_wrapper(self, func)
        self.compare_conds = compare_conds
        self.dump_conds = not compare_conds
        self.snap_dir = "data/snapdiff/snapshots"
        self.func_name = self.func.__name__
        self.snap_file = f"{self.snap_dir}/{self.func_name}.pkl"

        # Setup logger
        self.logger = setup_logger(log_to_file)

    def dump(self, result, *args, **kwargs):
        self.logger.info(f"Dumping snapshot for {self.func_name}")
        joblib.dump((result, args, kwargs), self.snap_file)

    def load(self):
        if os.path.exists(self.snap_file):
            self.logger.info(f"Loading snapshot for {self.snap_file}")
            return joblib.load(self.snap_file)
        else:
            self.logger.warning(f"No snapshot found for {self.func_name}")
            return 0, 0, 0

    def compare_result(self, result, old_result):
        return DeepDiff(result, old_result)

    def __call__(self, *args, **kwargs):
        self.logger.info(
            f"Calling function {self.func_name} with args: {args}, kwargs: {kwargs}"
        )
        result = self.func(*args, **kwargs)

        if self.compare_conds:
            old_result, old_args, old_kwargs = self.load()
            if old_result == 0 and old_args == 0 and old_kwargs == 0:
                self.logger.info("No snapshot found, nothing to compare.")

        if self.dump_conds:
            self.dump(result, *args, **kwargs)

        if self.compare_conds:
            if compare_args(args, old_args):
                self.logger.info("Arguments have changed.")
            if compare_kwargs(kwargs, old_kwargs):
                self.logger.info("Keyword arguments have changed.")
            res_diff = self.compare_result(result, old_result)
            if res_diff:
                self.logger.info(f"Result has changed: {res_diff}")
            else:
                self.logger.info("Result has not changed.")

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
