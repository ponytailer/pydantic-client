import inspect
from functools import wraps
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel

from .tools.agno import register_agno_tool


def _process_request_params(
    func: Callable, method: str, path: str, form_body: bool, *args, **kwargs
) -> Dict[str, Any]:
    """
    Extract and process request parameters from function arguments.

    Args:
        func: The decorated function
        method: HTTP method (GET, POST, etc.)
        path: URL path template with placeholders
        form_body: Whether to send body as form data instead of JSON
        *args, **kwargs: Function arguments

    Returns:
        Dictionary containing processed request parameters
    """
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    params = dict(bound_args.arguments)
    params.pop("self")

    # Handle request headers if provided
    request_headers = params.pop("request_headers", None)

    # Get return type for response model
    return_type = sig.return_annotation
    response_model = (
        return_type
        if isinstance(return_type, type) and issubclass(return_type, BaseModel)
        else None
    )

    # Format path with parameters
    formatted_path = path.format(**params)

    # Remove path parameters from params dict
    for key in path.split("{")[1:]:
        key = key.split("}")[0]
        params.pop(key, None)

    # Handle Pydantic models in parameters
    body_data = None
    query_params = {}

    for param_name, param_value in params.items():
        if isinstance(param_value, BaseModel):
            if method in ["POST", "PUT", "PATCH"]:
                # Use model as JSON/form body
                body_data = param_value.model_dump()
        else:
            if method in ["GET", "DELETE"]:
                query_params[param_name] = param_value

    return {
        "method": method,
        "path": formatted_path,
        "params": query_params if method in ["GET", "DELETE"] else None,
        "json": (
            body_data
            if not form_body and method in ["POST", "PUT", "PATCH"]
            else None
        ),
        "data": (
            body_data
            if form_body and method in ["POST", "PUT", "PATCH"]
            else None
        ),
        "headers": request_headers,
        "response_model": response_model,
    }


def rest(
    method: str, 
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None
) -> Callable:
    """
    Create a REST decorator for the specified HTTP method.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        form_body: Whether to send request body as form data instead of JSON
        agno_tool: Register as Agno tool
        tool_description: Custom description for the Agno tool

    Returns:
        Decorator function that accepts a path template
    """

    def decorator(path: str) -> Callable:
        """
        Decorator that accepts a URL path template.

        Args:
            path: URL path template with optional placeholders like
                "/users/{user_id}"

        Returns:
            Wrapper function for the decorated method
        """

        def wrapper(func: Callable) -> Callable:
            """
            Wrapper that handles both sync and async requests.

            Args:
                func: The function being decorated

            Returns:
                Function that determines whether to use sync or async
                based on client type
            """
            if agno_tool:
                func = register_agno_tool(tool_description)(func)

            @wraps(func)
            async def async_wrapped(self, *args, **kwargs):
                """Async wrapper for handling HTTP requests."""
                request_params = _process_request_params(
                    func, method, path, form_body, self, *args, **kwargs
                )
                return await self._request(**request_params)

            @wraps(func)
            def sync_wrapped(self, *args, **kwargs):
                """Sync wrapper for handling HTTP requests."""
                request_params = _process_request_params(
                    func, method, path, form_body, self, *args, **kwargs
                )
                return self._request(**request_params)

            @wraps(func)
            def choose_wrapper(self, *args, **kwargs):
                """Choose between sync and async wrapper based on client
                type."""
                if inspect.iscoroutinefunction(self._request):
                    return async_wrapped(self, *args, **kwargs)
                return sync_wrapped(self, *args, **kwargs)

            return choose_wrapper

        return wrapper

    return decorator


# HTTP method decorators
get = rest("GET")
delete = rest("DELETE")


# For HTTP methods that support form_body parameter, create wrapper functions
def post(path: str, form_body: bool = False) -> Callable:
    """POST decorator that supports form_body parameter."""
    return rest("POST", form_body=form_body)(path)


def put(path: str, form_body: bool = False) -> Callable:
    """PUT decorator that supports form_body parameter."""
    return rest("PUT", form_body=form_body)(path)


def patch(path: str, form_body: bool = False) -> Callable:
    """PATCH decorator that supports form_body parameter."""
    return rest("PATCH", form_body=form_body)(path)
