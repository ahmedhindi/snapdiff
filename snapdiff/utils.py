import inspect
import ast
import hashlib
import yaml
import os
import json
from deepdiff import DeepDiff


def load_snapper_config():
    with open("snapdiff_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config


def get_state():
    config = load_snapper_config()
    state_file = config["state_file"]
    dev_mode_name = config["dev_mode_name"]
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            state = json.load(f)
    else:
        state = {"dev_mode", False}
        with open(state_file, "w") as f:
            json.dump(state, f)
    return state[dev_mode_name]


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
