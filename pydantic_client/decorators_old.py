import inspect
from functools import wraps
from typing import Any, Callable, Optional, Type

from pydantic import BaseModel


def rest(method: str):
    def decorator(path: str):
        def wrapper(func: Callable):
            @wraps(func)
            async def async_wrapped(self, *args, **kwargs):
                sig = inspect.signature(func)
                bound_args = sig.bind(self, *args, **kwargs)
                bound_args.apply_defaults()
                params = dict(bound_args.arguments)
                params.pop('self')

                return_type = sig.return_annotation
                response_model = return_type if isinstance(return_type,
                                                           type) and issubclass(
                    return_type, BaseModel) else None

                formatted_path = path.format(**params)

                for key in path.split('{')[1:]:
                    key = key.split('}')[0]
                    params.pop(key, None)

                return await self._request(
                    method=method,
                    path=formatted_path,
                    params=params if method in ['GET', 'DELETE'] else None,
                    json=params if method in ['POST', 'PUT', 'PATCH'] else None,
                    response_model=response_model
                )

            @wraps(func)
            def sync_wrapped(self, *args, **kwargs):
                sig = inspect.signature(func)
                bound_args = sig.bind(self, *args, **kwargs)
                bound_args.apply_defaults()
                params = dict(bound_args.arguments)

                params.pop('self')

                return_type = sig.return_annotation
                response_model = return_type if isinstance(return_type,
                                                           type) and issubclass(
                    return_type, BaseModel) else None

                formatted_path = path.format(**params)

                for key in path.split('{')[1:]:
                    key = key.split('}')[0]
                    params.pop(key, None)

                return self._request(
                    method=method,
                    path=formatted_path,
                    params=params if method in ['GET', 'DELETE'] else None,
                    json=params if method in ['POST', 'PUT', 'PATCH'] else None,
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
post = rest('POST')
put = rest('PUT')
patch = rest('PATCH')
delete = rest('DELETE')
