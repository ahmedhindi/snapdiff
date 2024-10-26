import os
from functools import update_wrapper
import joblib
from deepdiff import DeepDiff, Delta
import logging
from typing import Dict, Any
from utils import load_snapper_config
from pathlib import Path


def setup_logger(log_to_file: bool = True, log_filename: str = "snapper.log"):
    logger = logging.getLogger("SnapperLogger")
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        formatter = logging.Formatter("%(asctime)s - %(message)s")

        if log_to_file:
            handler = logging.FileHandler(log_filename)
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class Snapper:
    def __init__(
        self,
        func: callable,
        mode: str = "diff",  # diff or snap
        log_to_file: bool = True,
        diff_func: callable = None,
        diff_type: str = "delta",
    ):
        if mode not in {"diff", "snap"}:
            raise ValueError("Invalid mode. Choose between 'snap' or 'diff'.")
        self.func = func
        update_wrapper(self, func)
        self.diff_func = self._set_diff_function()
        self.func_name = self.func.__name__
        self.snap_file = f"{self.snap_dir}/{self.func_name}.pkl"
        self.logger = setup_logger(log_to_file)
        os.makedirs(self.snap_dir, exist_ok=True)

    def _set_snap_path(self):
        self.snap_dir = Path(load_snapper_config()["snap_dir"])
        self.snap_file = self.snap_dir / Path(f"{self.func_name}.pkl")

    def _set_diff_function(self):
        if self.diff_func is None:
            print("using custom diff_func for delta")
            self.diff_func = self.mode
        elif self.diff_type == "delta":
            self.diff_func = Delta
        elif self.diff_type == "diff":
            self.diff_func = DeepDiff

    def dump(self, result, *args, **kwargs) -> None:
        joblib.dump((result, args, kwargs), self.snap_file)

    def load(self) -> Any:
        if os.path.exists(self.snap_file):
            return joblib.load(self.snap_file)
        else:
            self.logger.warning(f"No snapshot found for {self.func_name}")
            return None, None, None

    def diff_logger(self, diff: Dict, type: str) -> int:
        if diff:
            self.logger.info(f"{type} has changed: {diff}")
            return 1
        else:
            self.logger.info(f"{type} has not changed.")
            return 0

    def __call__(self, *args, **kwargs) -> Any:
        self.logger.info(
            f"Calling function {self.func_name} with args: {args}, kwargs: {kwargs}"
        )
        result = self.func(*args, **kwargs)

        if self.mode == "snap":
            self.dump(result, *args, **kwargs)

        elif self.mode == "diff":
            old_result, old_args, old_kwargs = self.load()
            if old_result is None and old_args is None and old_kwargs is None:
                self.logger.info("No snapshot found, nothing to compare.")

            args_diff = self.diff_func(args, old_args)
            args_ = self.diff_logger(args_diff, "Args")
            kwargs_diff = self.diff_func(kwargs, old_kwargs)
            kwargs_ = self.diff_logger(kwargs_diff, "Kwargs")
            res_diff = self.diff_func(result, old_result)
            res_ = self.diff_logger(res_diff, "Result")
            if args_ or kwargs_ or res_:
                self.logger.info("Result has not changed.")
        else:
            self.logger.error("Invalid mode. Choose between 'snap' or 'diff'.")
        return result

    def __repr__(self) -> str:
        return self.func.__repr__()


def snapper(compare_conds=True, diff_func=None):
    def decorator(func):
        return Snapper(func, compare_conds)

    return decorator
