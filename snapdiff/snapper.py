import os
from functools import update_wrapper
import joblib
from deepdiff import DeepDiff, Delta
import logging
from typing import Dict, Any
from .utils import load_snapper_config, get_normalized_code
from pathlib import Path


def deltadiff(a, b):
    diff = DeepDiff(a, b)
    delta = Delta(diff)
    return delta.to_dict()


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
        mode: str,  # diff or snap
        log_to_file: bool = True,
        snap_dir: str = None,
        log_file: str = None,
        subtype: str = "default",
        id: str = None,
        diff_func: callable = None,
        ignore_unchanged_funcs: bool = False,
    ):
        self.config_file = Path(load_snapper_config())
        self.snap_dir = Path(snap_dir) if snap_dir else None
        self.log_file = Path(log_file) if log_file else None
        if mode not in {"diff", "snap"}:
            raise ValueError("Invalid mode. Choose between 'snap' or 'diff'.")
        self.mode = mode
        self.func = func
        self.id = id
        self.ignore_unchanged_funcs = ignore_unchanged_funcs
        self.set_subtype(subtype)
        update_wrapper(self, func)
        self._func_metadata()
        self._set_diff_function(diff_func)
        self.func_name = self.func.__name__
        self._set_snap_path()
        self._setup_logger(log_to_file)
        # Create the snapshot directory and log file if they don't exist
        self._setup_files(self.snap_dir)
        self._setup_files(self.log_file)

    def set_subtype(self, subtype):
        if subtype not in self.config_file.keys():
            raise ValueError(
                f"Invalid subtype. {subtype} not found in snapdiff_config.yaml"
            )
        self.subtype = subtype
        force_config = self.config_file.get("force_config", False)
        if force_config or not hasattr(self, "snap_dir"):
            self.snap_dir = self.config_file.snap_dir
        if force_config or not hasattr(self, "log_file"):
            self.log_file = self.config_file.log_file
        if force_config or not hasattr(self, "ignore_unchanged_funcs"):
            self.ignore_unchanged_funcs = self.config_file.ignore_unchanged_funcs
        if force_config or not hasattr(self, "mode"):
            self.mode = self.config_file.mode
        if force_config or not hasattr(self, "log_to_file"):
            self.log_to_file = self.config_file.log_to_file

    def _setup_folders(self, file: Path):
        "if the folder that that files in does not exist create it"
        os.makedirs(file.parent, exist_ok=True)

    def _setup_logger(self, log_to_file):
        if log_to_file:
            self.log_file = self.config_file[self.subtype].get("log_file", None)
            if self.log_file:
                self.logger = setup_logger(log_to_file=True, log_filename=self.log_file)
            else:
                print(
                    f"No log file specified in snapdiff_config.yaml for this subtype: {self.subtype} using default log file."
                )

                self.logger = setup_logger(log_to_file=True, log_filename="snapper.log")

    def _setup_files(self):
        os.makedirs(self.snap_dir, exist_ok=True)

    def _set_snap_path(self):
        self.snap_dir = self.config_file["snap_dir"]
        if self.id:
            self.snap_file = self.snap_dir / Path(f"{self.id}.pkl")
        else:
            self.snap_file = self.snap_dir / Path(
                f"{ self.function_hash +'__'+ self.func_name}.pkl"
            )

    def _set_diff_function(self, diff_func):
        if diff_func:
            self.diff_func = diff_func
        else:
            self.diff_func = deltadiff

    def dump(self, function_hash, result, *args, **kwargs) -> None:
        joblib.dump((function_hash, result, args, kwargs), self.snap_file)

    def load(self) -> Any:
        if os.path.exists(self.snap_file):
            return joblib.load(self.snap_file)
        else:
            self.logger.warning(f"No snapshot found for {self.func_name}")
            return None, None, None, None

    def diff_logger(self, diff: Dict, type: str) -> int:
        if diff:
            self.logger.info(f"{type} has changed: {diff}")
            return 1
        else:
            self.logger.info(f"{type} has not changed.")
            return 0

    def _func_metadata(self):
        code_hash, normilized_code = get_normalized_code(self.func)
        self.function_hash = code_hash
        self.normilized_code = normilized_code

    def compare(self):
        old_func_hash, old_result, old_args, old_kwargs = self.load()
        if old_result is None and old_args is None and old_kwargs is None:
            self.logger.info("No snapshot found, nothing to compare.")

        if self.ignore_unchanged_funcs:
            if old_func_hash == self.function_hash:
                self.logger.info(
                    f"Function {self.func_name} has not changed any functional changes, comparasion is skipped."
                )
                return self.result

        args_diff = self.diff_func(self.args, old_args)
        args_ = self.diff_logger(args_diff, "Args")
        kwargs_diff = self.diff_func(self.kwargs, old_kwargs)
        kwargs_ = self.diff_logger(kwargs_diff, "Kwargs")
        res_diff = self.diff_func(self.result, old_result)
        res_ = self.diff_logger(res_diff, "Result")
        if args_ or kwargs_ or res_:
            self.logger.info("Result has not changed.")

    def __call__(self, *args, **kwargs) -> Any:
        self.new_args = args
        self.new_kwargs = kwargs

        self.logger.info(
            f"Calling function {self.func_name} with args: {args}, kwargs: {kwargs}"
        )
        self.result = self.func(*args, **kwargs)

        if self.mode == "snap":
            self.dump(self.function_hash, self.result, self.new_args, self.new_kwargs)

        elif self.mode == "diff":
            self.compare()
        else:
            self.logger.error("Invalid mode. Choose between 'snap' or 'diff'.")
        return self.result

    def __repr__(self) -> str:
        return self.func.__repr__()


def snapper(
    mode="diff",
    diff_func=None,
    id=None,
    ignore_unchanged_funcs=False,
):
    def decorator(func):
        return Snapper(
            func=func,
            mode=mode,
            diff_func=diff_func,
            id=id,
            ignore_unchanged_funcs=ignore_unchanged_funcs,
        )

    return decorator
