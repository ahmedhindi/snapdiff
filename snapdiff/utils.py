import inspect
import ast
import hashlib
import yaml
import os
from deepdiff import DeepDiff
from pathlib import Path
from pydantic import BaseModel
from typing import Literal


class SnapperConfig(BaseModel):
    snap_dir: Path  # Required field, no default
    log_file: Path  # Required field, no default
    ignore_unchanged_funcs: bool  # Required field, no default
    mode: Literal["snap", "diff"]  # Required field, no default
    log_to_file: bool  # Required field, no default
    force_config: bool = False  # Optional field, default value provided


def load_snapper_config(subtype: str = "default") -> SnapperConfig:
    # Load the configuration file
    with open("snapdiff_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Retrieve default and subtype settings
    default_config = config.get("default", {})
    subtype_config = config.get(subtype, {})

    # Merge subtype with defaults (only filling in missing keys)
    combined_config = {**default_config, **subtype_config}

    # Convert 'snap_dir' and 'log_file' to Path objects if they exist
    if "snap_dir" in combined_config:
        combined_config["snap_dir"] = Path(combined_config["snap_dir"])
    if "log_file" in combined_config:
        combined_config["log_file"] = Path(combined_config["log_file"])

    return SnapperConfig(**combined_config)


def compare_kwargs(kwargs, old_kwargs):
    return DeepDiff(kwargs, old_kwargs)


class NormalizeNames(ast.NodeTransformer):
    def __init__(self):
        self.func_name_counter = 0
        self.var_name_counter = 0
        self.func_name_map = {}
        self.var_name_map = {}

    def visit_FunctionDef(self, node):
        # Assign a generic name to function names
        if node.name not in self.func_name_map:
            self.func_name_map[node.name] = f"func_{self.func_name_counter}"
            self.func_name_counter += 1
        node.name = self.func_name_map[node.name]
        # Continue transforming function arguments and body
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        # Assign generic names to variable names used in the function
        if isinstance(node.ctx, ast.Store) or isinstance(node.ctx, ast.Load):
            if node.id not in self.var_name_map:
                self.var_name_map[node.id] = f"var_{self.var_name_counter}"
                self.var_name_counter += 1
            node.id = self.var_name_map[node.id]
        return node


def get_normalized_code(func: callable) -> str:
    source_code = inspect.getsource(func)
    parsed_code = ast.parse(source_code)
    normalizer = NormalizeNames()
    normalized_tree = normalizer.visit(parsed_code)
    normalized_code = ast.dump(normalized_tree, annotate_fields=False)
    code_hash = hashlib.sha256(normalized_code.encode()).hexdigest()
    return code_hash, normalized_code


def get_path(func):
    return os.path.relpath(inspect.getfile(func), start=os.getcwd())
