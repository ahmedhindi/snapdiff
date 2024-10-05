import inspect
import ast
import hashlib
import yaml
import os
import json
from deepdiff import DeepDiff


def get_normalized_code(func):
    # get the source code of the function
    source_code = inspect.getsource(func)
    # parse the source code into an Abstract Syntax Tree
    parsed_code = ast.parse(source_code)
    # convert the Abstract Syntax Tree back to normalized source code
    normalized_code = ast.dump(parsed_code, annotate_fields=False)
    # hash the normalized code
    code_hash = hashlib.sha256(normalized_code.encode()).hexdigest()
    return code_hash, normalized_code


def load_snapper_config():
    with open("snapper_config.yaml", "r") as f:
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


def compare_args(args, old_args):
    # new_args = set(args)
    # old_args = set(old_args)
    # added_args = new_args - old_args
    # removed_args = old_args - new_args
    # if added_args:
    #     print(f"Added positional arguments : {added_args}")
    # if removed_args:
    #     print(f"Removed positional arguments: {removed_args}")
    # for arg, old_arg in zip(args, old_args):
    #     if arg != old_arg:
    #         return False
    # return True
    return DeepDiff(args, old_args)


def compare_kwargs(kwargs, old_kwargs):
    # new_kws = set(kwargs.keys())
    # old_kws = set(old_kwargs.keys())
    # added_kws = new_kws - old_kws
    # removed_kws = old_kws - new_kws

    # if added_kws:
    #     print(f"Added keyword arguments : {added_kws}")

    # if removed_kws:
    #     print(f"Removed keyword arguments: {removed_kws}")

    # for key, value in kwargs.items():
    #     if key not in old_kwargs:
    #         return False
    #     else:
    #         if value != old_kwargs[key]:
    #             return False
    # return True
    return DeepDiff(kwargs, old_kwargs)
