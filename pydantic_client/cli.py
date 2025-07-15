import argparse
import yaml
import json
import re


def openapi_type_to_py(schema, models):
    """根据 openapi schema 返回 python 类型字符串（支持引用）"""
    if "$ref" in schema:
        model_name = schema["$ref"].split("/")[-1]
        return model_name
    typ = schema.get("type", "object")
    if typ == "array":
        items = schema.get("items", {})
        return f'List[{openapi_type_to_py(items, models)}]'
    return {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "object": "dict"
    }.get(typ, "Any")


def gen_pydantic_model(name, schema, models):
    fields = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    for field, prop in properties.items():
        typ = openapi_type_to_py(prop, models)
        default = "" if field in required else " = None"
        fields.append(f"    {field}: {typ}{default}")
    if not fields:
        fields.append("    pass")
    return f"class {name}(BaseModel):\n" + "\n".join(fields) + "\n"


def collect_models(components):
    """collect all schema and generate the Pydantic model"""
    models = {}
    for name, schema in components.items():
        models[name] = gen_pydantic_model(name, schema, models)
    return models


def method_decorator(method):
    return {
        "get": "get",
        "post": "post",
        "put": "put",
        "patch": "patch",
        "delete": "delete"
    }[method]


def get_req_model(operation):
    # only support application/json
    req_body = operation.get("requestBody", {})
    content = req_body.get("content", {})
    for ct, obj in content.items():
        schema = obj.get("schema")
        if schema and "$ref" in schema:
            return schema["$ref"].split("/")[-1]
    return None


def get_resp_model(operation):
    # only 2xx and application/json
    for code, resp in operation.get("responses", {}).items():
        if not code.startswith("2"):
            continue
        content = resp.get("content", {})
        for ct, obj in content.items():
            schema = obj.get("schema")
            if schema and "$ref" in schema:
                return schema["$ref"].split("/")[-1]
            elif schema and schema.get("type") == "array" and "$ref" in schema["items"]:
                # 返回数组
                return f'List[{schema["items"]["$ref"].split("/")[-1]}]'
    return "Any"


def parse_parameters(parameters):
    params = []
    for p in parameters:
        if p.get("in") == "body":
            continue  # 现代 openapi 用 requestBody
        name = p["name"]
        required = p.get("required", False)
        typ = openapi_type_to_py(p.get("schema", {}), {})
        default = "" if required else " = None"
        params.append(f"{name}: {typ}{default}")
    return params


def generate_method(path, method, operation, client_type):
    deco = method_decorator(method)
    summary = operation.get("summary", "")
    parameters = operation.get("parameters", [])
    param_strs = parse_parameters(parameters)
    req_model = get_req_model(operation)
    if req_model:
        param_strs.append(f"{req_model.lower()}: {req_model}")
    params = ", ".join(["self"] + param_strs)
    resp_model = get_resp_model(operation)
    async_prefix = "async " if client_type.lower() in ["aiohttp", "httpx"] else ""
    return (
        f"    @{deco}(\"{path}\")\n"
        f"    {async_prefix}def {operation['operationId']}({params}) -> {resp_model}:\n"
        f"        \"\"\"{summary}\"\"\"\n"
        f"        ...\n"
    )


def main():
    parser = argparse.ArgumentParser("swagger-cli")
    parser.add_argument("-f", "--file", required=True, help="swagger.yaml or openapi.json file")
    parser.add_argument("-t", "--type", required=True, choices=["requests", "aiohttp", "httpx"], help="Client type")
    parser.add_argument("-o", "--output", default="generated_client.py", help="Output python file")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        if args.file.endswith(".json"):
            raw = json.load(f)
        else:
            raw = yaml.safe_load(f)

    # 1. 解析 models
    if "components" in raw and "schemas" in raw["components"]:
        schemas = raw["components"]["schemas"]
    elif "definitions" in raw:
        schemas = raw["definitions"]
    else:
        schemas = {}
    models = collect_models(schemas)

    # 2. 生成方法
    paths = raw.get("paths", {})
    class_name = f"{args.type.capitalize()}Client"
    base = {
        "requests": "RequestsWebClient",
        "aiohttp": "AiohttpWebClient",
        "httpx": "HttpxWebClient"
    }[args.type]

    methods = []
    for path, methods_dict in paths.items():
        for method, operation in methods_dict.items():
            opid = operation.get("operationId")
            if not opid:
                opid = f"{method}_{re.sub(r'[^a-zA-Z0-9]', '_', path.strip('/'))}"
                operation["operationId"] = opid
            methods.append(generate_method(path, method, operation, args.type))

    # 3. 写入文件
    with open(args.output, "w", encoding="utf-8") as out:
        out.write("from pydantic import BaseModel\n")
        out.write("from pydantic_client import get, post, put, patch, delete, RequestsWebClient, AiohttpWebClient, HttpxWebClient\n")
        out.write("from typing import Any, List\n\n")
        for m in models.values():
            out.write(m)
            out.write("\n")
        out.write(f"class {class_name}({base}):\n")
        if not methods:
            out.write("    pass\n")
        else:
            for m in methods:
                out.write(m)
                out.write("\n")


if __name__ == "__main__":
    main()
