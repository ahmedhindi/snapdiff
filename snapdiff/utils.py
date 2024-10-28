import inspect
import ast
import hashlib
import yaml
import os
import json
from deepdiff import DeepDiff
import astor


# def get_normalized_code(func):
#     # get the source code of the function
#     source_code = inspect.getsource(func)
#     # parse the source code into an Abstract Syntax Tree
#     parsed_code = ast.parse(source_code)
#     # convert the Abstract Syntax Tree back to normalized source code
#     normalized_code = ast.dump(parsed_code, annotate_fields=False)
#     # hash the normalized code
#     code_hash = hashlib.sha256(normalized_code.encode()).hexdigest()
#     return code_hash, normalized_code


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


def get_normalized_code(func):
    # Get the source code of the function
    source_code = inspect.getsource(func)
    # Parse the source code into an Abstract Syntax Tree
    parsed_code = ast.parse(source_code)
    # Normalize function and variable names
    normalizer = NormalizeNames()
    normalized_tree = normalizer.visit(parsed_code)
    # Convert the normalized AST back to source code (as a string) for hashing
    normalized_code = ast.dump(normalized_tree, annotate_fields=False)
    # Hash the normalized code
    code_hash = hashlib.sha256(normalized_code.encode()).hexdigest()
    return code_hash, normalized_code


def get_path(func):
    return os.path.relpath(inspect.getfile(func), start=os.getcwd())
