import inspect
import ast
import hashlib
import yaml
import os
import json
from deepdiff import DeepDiff
import astor


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


def compare_kwargs(kwargs, old_kwargs):
    return DeepDiff(kwargs, old_kwargs)


def add_decorator_to_functions(file_path, decorator_name, decorator_params=None):
    # Read the file content
    with open(file_path, "r") as file:
        file_content = file.read()

    # Parse the file content into an AST
    tree = ast.parse(file_content)

    # Build the decorator string with or without parameters
    if decorator_params:
        decorator_with_params = f"{decorator_name}({', '.join(decorator_params)})"
    else:
        decorator_with_params = f"{decorator_name}"

    # Define the decorator node
    decorator_node = ast.parse(decorator_with_params).body[0].value

    # Loop through all the nodes in the AST and find function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):  # Check if it's a function
            # Add the decorator to the function
            node.decorator_list.append(decorator_node)

    # Convert the modified AST back to Python code
    modified_code = astor.to_source(tree)

    # Write the modified code back to the file (or you could return it)
    with open(file_path, "w") as file:
        file.write(modified_code)

    print(f"Decorator '{decorator_name}' added to all functions in {file_path}")
