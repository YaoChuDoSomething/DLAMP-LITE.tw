import importlib
from typing import Dict, Any, List # Added for type hints

def load_diagnostics(registry_config_dict: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
    """
    Loads diagnostic functions and their requirements from a configuration dictionary.

    Args:
        registry_config_dict (Dict[str, Any]): A dictionary containing the 'registry'
                                               configuration, including 'varname' and
                                               'source_dataset'.

    Returns:
        tuple[Dict[str, Any], str]: A tuple containing:
            - diagnostics (Dict[str, Any]): A dictionary where keys are variable names
                                            and values are dicts with 'requires' (list of
                                            dependencies) and 'function' (the callable
                                            diagnostic function).
            - source_dataset (str): The source dataset name from the configuration.
    """
    
    # Expect registry_config_dict to be the content of the 'registry' section
    reg_cfg = registry_config_dict["varname"]
    diagnostics = {}

    for name, item in reg_cfg.items():
        func_name = item["function"]
        # Assuming diagnostic_functions.py is always the source for these functions
        module = importlib.import_module("src.opflows.diagnostic_functions")
        func = getattr(module, func_name)
        diagnostics[name] = {
            "requires": item["requires"],
            "function": func,
        }
    source_dataset = registry_config_dict["source_dataset"]
    return diagnostics, source_dataset


def sort_diagnostics_by_dependencies(diagnostics: Dict[str, Any]) -> List[str]:
    """
    Sorts diagnostic variables by their dependencies using a topological sort.

    Args:
        diagnostics (Dict[str, Any]): A dictionary of diagnostic variables, where
                                      each value contains a 'requires' list of dependencies.

    Returns:
        List[str]: A list of diagnostic variable names, sorted such that all
                   dependencies of a variable appear before it in the list.
    """
    sorted_list = []
    visited = set()
    recursion_stack = set()

    def visit(var):
        if var in recursion_stack:
            raise RecursionError(f"Circular dependency detected: {var}")
        if var in visited:
            return

        recursion_stack.add(var)
        # Only visit dependencies that are themselves diagnostic variables
        # (i.e., keys in the diagnostics dict)
        for dep in diagnostics[var].get("requires", []):
            if dep in diagnostics: # Only recurse if the dependency is also a diagnostic we manage
                visit(dep)
        
        recursion_stack.remove(var)
        visited.add(var)
        sorted_list.append(var)

    # To handle cases where diagnostics might not be directly connected or
    # to ensure all diagnostics are processed even if not a dependency of another
    for var in diagnostics:
        if var not in visited:
            visit(var)

    return sorted_list

