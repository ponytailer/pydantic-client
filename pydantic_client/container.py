import inspect
import logging
import re
from typing import Dict, Any
from urllib.parse import parse_qsl, urlparse

from pydantic import BaseModel

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.schema.http_request import HttpRequest
from pydantic_client.schema.method_info import MethodInfo

logger = logging.getLogger("pydantic_client.parser")


class Parser:
    querystring_pattern = re.compile(r"{(.*?)}")

    @staticmethod
    def _apply_args(
        method_info: MethodInfo,
        *args, **kwargs
    ) -> Dict[str, Any]:
        f = inspect.getcallargs(
            method_info.func, *args, **kwargs,
        )
        f.pop("self", None)
        for key, value in f.items():
            if isinstance(value, BaseModel):
                f[key] = value.model_dump()
        return f

    @staticmethod
    def _get_url(method_info, args) -> str:
        keys = Parser.querystring_pattern.findall(method_info.url)
        query_args = {arg: val for arg, val in args.items() if
                      arg in keys and val}

        for key in keys:
            args.pop(key, None)

        url = method_info.url.format(**query_args)

        url_result = urlparse(url)
        if "{" in url_result.path:
            logger.warning(f"Not formatted args in url path: {url}")

        querystring = "&".join(
            f"{k}={v}" for k, v in parse_qsl(url_result.query) if "{" not in v
        )
        return url_result.path + "?" + querystring if querystring else url_result.path

    @staticmethod
    def dict_to_body(func_args: Dict[str, Any]) -> Dict:
        keys = list(func_args.keys())
        if len(keys) == 1:
            if keys[0] == "request_headers":
                return func_args
            return func_args[keys[0]]
        return {}

    @staticmethod
    def get_request(method_info: MethodInfo, *args, **kwargs):
        # get the function the value of args
        func_args: Dict[str, Any] = Parser._apply_args(
            method_info, *args, **kwargs)
        # format url and render the querystring
        url: str = Parser._get_url(method_info, func_args)

        body = Parser.dict_to_body(func_args)
        request_headers = body.pop("request_headers", None)

        if method_info.form_body:
            data, json = body, {}
        else:
            data, json = {}, body

        return HttpRequest(
            url=url,
            data=data,
            json_body=json,
            method=method_info.http_method,
            request_headers=request_headers,
            is_file=method_info.response_type is bytes
        )


class Container:
    def __init__(self):
        self.protocol_clients = {}
        self.func_bindings = {}

    def bind_protocol(self, protocol, client):
        self.protocol_clients[protocol] = client

    def bind_func(self, func, method_info: MethodInfo):
        self.func_bindings[func] = method_info

    def do_func(self, func, *args, **kwargs):
        method_info: MethodInfo = self.func_bindings.get(func)
        if not method_info:
            raise ValueError(f"No router info found for {func}")

        instance = args[0]
        client: AbstractClient = self.protocol_clients.get(instance)
        request = Parser.get_request(method_info, *args, **kwargs)
        return client.do_request(request)


container = Container()
