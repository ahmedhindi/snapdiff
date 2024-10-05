import inspect
import ast
import hashlib
import yaml
import os
import json


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
