import inspect
from functools import wraps
from typing import Any, Callable, Optional, Type, get_type_hints

from pydantic import BaseModel


def rest(method: str, form_body: bool = False):
    def decorator(path: str):
        def wrapper(func: Callable):
            @wraps(func)
            async def async_wrapped(self, *args, **kwargs):
                sig = inspect.signature(func)
                bound_args = sig.bind(self, *args, **kwargs)
                bound_args.apply_defaults()
                params = dict(bound_args.arguments)
                params.pop('self')

                # Handle request headers if provided
                request_headers = params.pop('request_headers', None)

                # Get return type for response model
                return_type = sig.return_annotation
                response_model = return_type if isinstance(return_type, type) and issubclass(
                    return_type, BaseModel) else None

                # Format path with parameters
                formatted_path = path.format(**params)

                # Remove path parameters from params dict
                for key in path.split('{')[1:]:
                    key = key.split('}')[0]
                    params.pop(key, None)

                # Handle Pydantic models in parameters
                body_data = None
                query_params = {}
                
                type_hints = get_type_hints(func)
                for param_name, param_value in params.items():
                    param_type = type_hints.get(param_name)
                    if isinstance(param_value, BaseModel):
                        if method in ['POST', 'PUT', 'PATCH']:
                            if form_body:
                                # Convert model to form data
                                body_data = param_value.model_dump()
                            else:
                                # Use model as JSON body
                                body_data = param_value.model_dump()
                    else:
                        if method in ['GET', 'DELETE']:
                            query_params[param_name] = param_value

                return await self._request(
                    method=method,
                    path=formatted_path,
                    params=query_params if method in ['GET', 'DELETE'] else None,
                    json=body_data if not form_body and method in ['POST', 'PUT', 'PATCH'] else None,
                    data=body_data if form_body and method in ['POST', 'PUT', 'PATCH'] else None,
                    headers=request_headers,
                    response_model=response_model
                )

            @wraps(func)
            def sync_wrapped(self, *args, **kwargs):
                sig = inspect.signature(func)
                bound_args = sig.bind(self, *args, **kwargs)
                bound_args.apply_defaults()
                params = dict(bound_args.arguments)
                params.pop('self')

                # Handle request headers if provided
                request_headers = params.pop('request_headers', None)

                # Get return type for response model
                return_type = sig.return_annotation
                response_model = return_type if isinstance(return_type, type) and issubclass(
                    return_type, BaseModel) else None

                # Format path with parameters
                formatted_path = path.format(**params)

                # Remove path parameters from params dict
                for key in path.split('{')[1:]:
                    key = key.split('}')[0]
                    params.pop(key, None)

                # Handle Pydantic models in parameters
                body_data = None
                query_params = {}
                
                type_hints = get_type_hints(func)
                for param_name, param_value in params.items():
                    param_type = type_hints.get(param_name)
                    if isinstance(param_value, BaseModel):
                        if method in ['POST', 'PUT', 'PATCH']:
                            if form_body:
                                # Convert model to form data
                                body_data = param_value.model_dump()
                            else:
                                # Use model as JSON body
                                body_data = param_value.model_dump()
                    else:
                        if method in ['GET', 'DELETE']:
                            query_params[param_name] = param_value

                return self._request(
                    method=method,
                    path=formatted_path,
                    params=query_params if method in ['GET', 'DELETE'] else None,
                    json=body_data if not form_body and method in ['POST', 'PUT', 'PATCH'] else None,
                    data=body_data if form_body and method in ['POST', 'PUT', 'PATCH'] else None,
                    headers=request_headers,
                    response_model=response_model
                )

            def choose_wrapper(self, *args, **kwargs):
                if inspect.iscoroutinefunction(self._request):
                    return async_wrapped(self, *args, **kwargs)
                return sync_wrapped(self, *args, **kwargs)

            return choose_wrapper

        return wrapper

    return decorator


get = rest('GET')
post = lambda path, form_body=False: rest('POST', form_body=form_body)(path)
put = lambda path, form_body=False: rest('PUT', form_body=form_body)(path)
patch = lambda path, form_body=False: rest('PATCH', form_body=form_body)(path)
delete = rest('DELETE')