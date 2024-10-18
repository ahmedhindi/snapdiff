import os
from functools import update_wrapper
import joblib
from deepdiff import DeepDiff
import logging


def setup_logger(log_to_file=True, log_filename="snapper.log"):
    logger = logging.getLogger("SnapperLogger")
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if they already exist
    if not logger.hasHandlers():
        # Create formatter with structured logs
        formatter = logging.Formatter("%(asctime)s - %(message)s")

        # Create console handler or file handler based on the user's choice
        if log_to_file:
            handler = logging.FileHandler(log_filename)
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class Snapper:
    def __init__(self, func, compare_conds=True, log_to_file=True, diff_func=None):
        self.func = func
        self.diff_func = diff_func or DeepDiff
        update_wrapper(self, func)
        self.compare_conds = compare_conds
        self.dump_conds = not compare_conds
        self.snap_dir = "data/snapdiff/snapshots"
        self.func_name = self.func.__name__
        self.snap_file = f"{self.snap_dir}/{self.func_name}.pkl"
        self.logger = setup_logger(log_to_file)

    def dump(self, result, *args, **kwargs):
        joblib.dump((result, args, kwargs), self.snap_file)

    def load(self):
        if os.path.exists(self.snap_file):
            return joblib.load(self.snap_file)
        else:
            self.logger.warning(f"No snapshot found for {self.func_name}")
            return None, None, None

    def diff_logger(self, diff, type):
        if diff:
            self.logger.info(f"{type} has changed: {diff}")
            return 1
        else:
            self.logger.info(f"{type} has not changed.")
            return 0

    def __call__(self, *args, **kwargs):
        self.logger.info(
            f"Calling function {self.func_name} with args: {args}, kwargs: {kwargs}"
        )
        result = self.func(*args, **kwargs)

        if self.compare_conds:
            old_result, old_args, old_kwargs = self.load()
            if old_result is None and old_args is None and old_kwargs is None:
                self.logger.info("No snapshot found, nothing to compare.")

        if self.dump_conds:
            self.dump(result, *args, **kwargs)

        if self.compare_conds:
            args_diff = self.diff_func(args, old_args)
            args_ = self.diff_logger(args_diff, "Args")
            kwargs_diff = self.diff_func(kwargs, old_kwargs)
            kwargs_ = self.diff_logger(kwargs_diff, "Kwargs")
            res_diff = self.diff_func(result, old_result)
            res_ = self.diff_logger(res_diff, "Result")
            if args_ or kwargs_ or res_:
                self.logger.info("Result has not changed.")
        return result

    def __repr__(self):
        return self.func.__repr__()


def snapper(compare_conds=True, diff_func=None):
    def decorator(func):
        return Snapper(func, compare_conds)

    return decorator
