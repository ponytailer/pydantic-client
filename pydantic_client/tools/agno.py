import inspect

from typing import Any, Dict, List, Optional
from functools import wraps
from inspect import Parameter, signature
from pydantic import BaseModel


def _get_parameter_type(param: Parameter) -> str:
    """Convert Python/Pydantic type to OpenAPI type"""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }
    
    annotation = param.annotation
    if hasattr(annotation, "__origin__"):  # For generic types like List[str]
        base_type = annotation.__origin__
        if base_type in (list, List):
            return "array"
        elif base_type in (dict, Dict):
            return "object"
    
    if isinstance(annotation, type):
        if issubclass(annotation, BaseModel):
            return "object"
        return type_map.get(annotation, "string")
    
    return "string"


def create_agno_tool(func: callable, description: Optional[str] = None) -> Dict[str, Any]:
    """Create an Agno tool definition from a function"""
    sig = signature(func)
    
    # Get function description from docstring
    doc = func.__doc__ or ""
    desc = description or doc.strip().split("\n")[0]
    
    parameters = {}
    for name, param in sig.parameters.items():
        if name == "self":
            continue
            
        param_type = _get_parameter_type(param)
        param_desc = ""
        
        # Try to extract parameter description from docstring
        param_doc = doc.split(f":param {name}:")
        if len(param_doc) > 1:
            param_desc = param_doc[1].split("\n")[0].strip()
        
        parameters[name] = {
            "type": param_type,
            "description": param_desc,
            "required": param.default == Parameter.empty
        }
        
        # Handle Pydantic models
        if (isinstance(param.annotation, type) and 
            issubclass(param.annotation, BaseModel)):
            parameters[name]["properties"] = {
                field_name: {
                    "type": _get_parameter_type(inspect.Parameter(
                        field_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=field_type)
                    )
                }
                for field_name, field_type in param.annotation.__annotations__.items()
            }
    return {
        "name": func.__name__,
        "description": desc,
        "parameters": parameters
    }


def register_agno_tool(description: Optional[str] = None):
    """Decorator to register a method as an Agno tool"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Store Agno tool definition
        wrapper._agno_tool = create_agno_tool(func, description)
        return wrapper
    return decorator