# snapdiff

Here's the README content as one continuous Markdown block:

---

# snapdiff

`snapdiff` is a Python package for capturing snapshots of function input and output data to track changes over time. It’s designed for use in testing and debugging, allowing you to compare function results across different runs and log any differences.

## Features

- **Snapshot Mode**: Saves a snapshot of function inputs and outputs.
- **Diff Mode**: Compares current function outputs with previously saved snapshots, logging differences.
- **Customizable Diff Functions**: Use built-in or custom diff functions to handle comparisons.
- **Logging**: Configurable logging options to monitor differences across function runs.

## Installation

Install snapdiff using `pip`:

```
pip install snapdiff
```

## Basic Usage

### Setting Up Snapshots

Decorate a function with `@snapper(mode="snap")` to take a snapshot of inputs and outputs. This is useful for capturing a function's behavior for later comparisons.

```
from snapdiff import snapper

@snapper(mode="snap")
def example_function(a, b):
    return a + b

# Taking a snapshot
example_function(2, 3)
```

### Comparing with Snapshots

Switch to `mode="diff"` to check if the function’s behavior has changed compared to the previous snapshot.

```
from snapdiff import snapper

@snapper(mode="diff")
def example_function(a, b):
    return a + b

# This will compare the result of the current call with the saved snapshot
example_function(2, 3)
```

If there’s any difference in input or output, it will be logged.

## Advanced Usage

### Custom Diff Functions

You can supply a custom diff function for cases where the built-in `DeepDiff` does not suit your needs.

```
from snapdiff import snapper

def custom_diff(a, b):
    return {"difference": a - b} if a != b else {}

@snapper(mode="diff", diff_func=custom_diff)
def example_function(a, b):
    return a * b

example_function(4, 5)
```

### Logging Options

To enable or disable logging to a file, use the `log_to_file` parameter when initializing the `Snapper` decorator.

```
from snapdiff import snapper

@snapper(mode="diff", log_to_file=False)
def example_function(a, b):
    return a ** b
```

## Configuration

`snapdiff` allows configuration using a YAML file named `snapdiff_config.yaml` to specify default directories for snapshots, log files, and subtype-specific options.

## License

MIT License

---

For full documentation and examples, visit the [GitHub repository](https://github.com/ahmedhindi/snapdiff).