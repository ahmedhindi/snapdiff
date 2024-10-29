import ast
import astor
import hashlib
from .utils import get_path


def get_random_hash(func_name, func_path):
    string = f"{func_name}{func_path}"
    return hashlib.sha256(string.encode()).hexdigest()


# TODO add id for each decorator and incase of replacing an old one with a new one, the id should be the same
def add_decorator_to_functions(file_path, decorator_name, decorator_params):
    # Read the file content
    with open(file_path, "r") as file:
        file_content = file.read()

    # Parse the file content into an AST
    tree = ast.parse(file_content)

    # Build the decorator string with or without parameters
    if decorator_params:
        params = "("
        for key, value in decorator_params.items():
            params += f"""{key}="{value}", """
        params += ")"
        decorator_with_params = f"{decorator_name}" + params
    else:
        raise ValueError("Decorator parameters are required")

    # Define the decorator node
    decorator_node = ast.parse(decorator_with_params).body[0].value

    # Loop through all the nodes in the AST and find function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):  # Check if it's a function
            # Check if the function already has the decorator if it already has the same decorator then delte the old one and add the new one
            for decorator in node.decorator_list:
                # print(decorator)
                if decorator.func.id == decorator_name:
                    node.decorator_list.remove(decorator)
                    break
            # Add the decorator to the function
            node.decorator_list.append(decorator_node)

    modified_code = astor.to_source(tree)

    # Write the modified code back to the file (or you could return it)
    with open(file_path, "w") as file:
        file.write(modified_code)

    print(f"Decorator '{decorator_name}' added to all functions in {file_path}")
