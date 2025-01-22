import logging
from collections import defaultdict
from typing import Optional

from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from pydantic import BaseModel

all_models = {}

logger = logging.getLogger(__name__)


class RequestEntity(BaseModel):
    method: str
    function_name: str
    path: str
    response: str
    arg_dict: dict
    args: Optional[str] = ""


def generate_pydantic_model(schema, model_name):
    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])

    simple_fields = {}
    for field_name, field_schema in properties.items():
        field_type = field_schema.get('type')
        if field_type == 'object':
            ref_object = field_schema["$ref"].rsplit("/", 1)[-1]
            simple_fields[field_name] = ref_object
        elif field_type == 'array':
            items_schema = field_schema.get('items', {})
            items_type = items_schema.get('type')
            if items_type == 'object':
                ref_object = field_schema["$ref"].rsplit("/", 1)[-1]
                simple_fields[field_name] = list[ref_object]
            else:
                simple_fields[field_name] = list[
                    map_type_to_string(items_type)]
        else:
            simple_fields[field_name] = map_type_to_string(
                field_type)

        if field_name in required_fields:
            simple_fields[field_name] = f"Optional[{simple_fields[field_name]}]"

    if simple_fields:
        all_models[model_name] = simple_fields


def map_type_to_string(openapi_type):
    type_mapping = {
        'string': "str",
        'integer': "int",
        'number': "float",
        'boolean': "bool",
        'array': list,
        'object': dict
    }
    return type_mapping.get(openapi_type, str)  # 默认返回 str


def success_return(status, response):
    return status == "200" or status == "201" and "content" in response


def convert_request_name(name: str):
    s = []
    for k in name:
        if k.isupper():
            s.append("_")
            s.append(k.lower())
        else:
            s.append(k)
    return "".join(s[1:])


def parse_swagger_and_generate_models(swagger_path):
    swagger_dict, _ = read_from_filename(swagger_path)
    validate(swagger_dict)

    definitions = swagger_dict.get('components', {}).get('schemas', {})
    paths = swagger_dict.get('paths', {})

    for model_name, model_schema in definitions.items():
        generate_pydantic_model(model_schema, model_name)

    path_pairs = defaultdict(list)

    for path, path_item in paths.items():
        function_name_suffix = "_".join(
            p for p in path.split("/") if "{" not in p)

        for method, operation in path_item.items():
            request_entity_body = {}
            arg_dict = {}

            # 处理路径参数和查询参数
            if "parameters" in operation:
                for parameter in operation["parameters"]:
                    if parameter["in"] == "path":
                        for _, value_ in parameter["schema"].items():
                            value_string = map_type_to_string(value_)
                            arg_dict[parameter["name"]] = value_string
                            break
                    elif parameter["in"] == "query":
                        for _, value_ in parameter["schema"].items():
                            value_string = map_type_to_string(value_)
                            arg_dict[
                                parameter["name"]] = f"Optional[{value_string}]"
                            break
                    else:
                        logger.warning(
                            f"unknown parameter in {path}: {parameter}")

            # 处理请求体
            if "requestBody" in operation:
                request_body = operation['requestBody']
                for _, media_type in request_body.get("content", {}).items():
                    schema = media_type.get("schema", {})
                    if not schema:
                        continue
                    request_model_name = schema.get("$ref", "").split('/')[-1]
                    arg_dict[convert_request_name(
                        request_model_name)] = request_model_name
                    break

            # 处理响应体
            if 'responses' in operation:
                for status_code, response in operation['responses'].items():
                    if not success_return(status_code, response):
                        continue
                    for _, media_type in response["content"].items():
                        if "schema" not in media_type:
                            continue
                        schema = media_type['schema']
                        # 提取响应模型名称
                        response_model_name = \
                            schema.get('$ref', '').split('/')[-1]
                        request_entity_body["response"] = response_model_name

            request_entity_body["method"] = method
            request_entity_body[
                "function_name"] = f"{method}{function_name_suffix}"
            request_entity_body["arg_dict"] = arg_dict
            path_pairs[path].append(request_entity_body)

    ret = []
    for path, values in path_pairs.items():
        for value in values:
            value["path"] = path
            ret.append(RequestEntity(**value))
    return ret


def handle_swagger_file(path: str, model_file_name: str = ""):
    import jinja2
    results = parse_swagger_and_generate_models(path)
    tmpl = jinja2.Template(open("models.template").read())
    render_fields = {}

    for key, value in all_models.items():
        fields = [
            f"{field}: {ftype}"
            for field, ftype in value.items()
        ]
        render_fields[key] = fields
        for entity in results:
            args = ", ".join([
                f"{name}: {type_}"
                for name, type_ in entity.arg_dict.items()
            ])
            entity.args = args

    if render_fields:
        model_string = tmpl.render(models=render_fields, info=results)
        if model_file_name:
            with open(model_file_name, "w") as f:
                f.write(model_string)
        else:
            print(model_string)
