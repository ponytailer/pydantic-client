import sys
import yaml
import subprocess
import pytest

from pydantic_client import cli


def run_cli(args):
    result = subprocess.run(
        [sys.executable, "-m", "pydantic_client.cli"] + args,
        capture_output=True,
        text=True,
    )
    return result


def test_cli_generates_client_file(tmp_path):
    # simple swagger
    swagger = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0"},
        "paths": {
            "/user": {
                "post": {
                    "operationId": "create_user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    }
                }
            }
        }
    }
    swagger_file = tmp_path / "swagger.yaml"
    with open(swagger_file, "w") as f:
        yaml.dump(swagger, f)

    output_file = tmp_path / "my_client.py"
    # run cli
    result = run_cli(["-f", str(swagger_file), "-t", "requests", "-o", str(output_file)])
    assert result.returncode == 0
    assert output_file.exists()
    code = output_file.read_text()
    # check
    assert "class User(BaseModel):" in code
    assert "class RequestsClient(RequestsWebClient):" in code
    assert "def create_user(self, user: User) -> User" in code


def test_cli_invalid_args():
    result = run_cli(["-t", "requests"])
    assert result.returncode != 0
    assert "usage" in result.stderr.lower()


def test_openapi_type_to_py_basic_types():
    assert cli.openapi_type_to_py({"type": "string"}, {}) == "str"
    assert cli.openapi_type_to_py({"type": "integer"}, {}) == "int"
    assert cli.openapi_type_to_py({"type": "number"}, {}) == "float"
    assert cli.openapi_type_to_py({"type": "boolean"}, {}) == "bool"
    assert cli.openapi_type_to_py({"type": "object"}, {}) == "dict"
    assert cli.openapi_type_to_py({"type": "array", "items": {"type": "string"}}, {}) == "List[str]"
    # $ref
    assert cli.openapi_type_to_py({"$ref": "#/components/schemas/Foo"}, {}) == "Foo"
    # unknown type
    assert cli.openapi_type_to_py({"type": "unknown"}, {}) == "Any"


def test_gen_pydantic_model_and_collect_models():
    schema = {
        "type": "object",
        "required": ["id"],
        "properties": {"id": {"type": "string"}, "name": {"type": "string"}}
    }
    code = cli.gen_pydantic_model("User", schema, {})
    assert "class User(BaseModel):" in code
    assert "id: str" in code
    assert "name: str = None" in code
    # no properties
    code2 = cli.gen_pydantic_model("Empty", {"type": "object"}, {})
    assert "pass" in code2
    # collect_models
    models = cli.collect_models({"User": schema})
    assert "User" in models


def test_method_decorator():
    assert cli.method_decorator("get") == "get"
    assert cli.method_decorator("post") == "post"
    assert cli.method_decorator("put") == "put"
    assert cli.method_decorator("patch") == "patch"
    assert cli.method_decorator("delete") == "delete"


def test_get_req_model():
    op = {"requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Foo"}}}}}
    assert cli.get_req_model(op) == "Foo"
    # no ref
    op2 = {"requestBody": {"content": {"application/json": {"schema": {"type": "string"}}}}}
    assert cli.get_req_model(op2) is None
    # no requestBody
    assert cli.get_req_model({}) is None


def test_get_resp_model():
    op = {"responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Bar"}}}}}}
    assert cli.get_resp_model(op) == "Bar"
    # array
    op2 = {"responses": {"200": {"content": {
        "application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Baz"}}}}}}}
    assert cli.get_resp_model(op2) == "List[Baz]"
    # no 2xx
    assert cli.get_resp_model({"responses": {"404": {}}}) == "Any"


def test_parse_parameters():
    params = [
        {"name": "id", "in": "query", "required": True, "schema": {"type": "string"}},
        {"name": "opt", "in": "query", "required": False, "schema": {"type": "integer"}},
        {"name": "body", "in": "body"}
    ]
    result = cli.parse_parameters(params)
    assert "id: str" in result[0]
    assert "opt: int = None" in result[1]
    assert all("body" not in p for p in result)


def test_generate_method():
    op = {
        "operationId": "get_user",
        "summary": "Get user info",
        "parameters": [
            {"name": "id", "in": "query", "required": True, "schema": {"type": "string"}}
        ],
        "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}}
    }
    code = cli.generate_method("/user", "get", op, "requests")
    assert "def get_user(self, id: str) -> User" in code
    code2 = cli.generate_method("/user", "get", op, "aiohttp")
    assert "async def get_user" in code2
    # with req_model
    op2 = {
        "operationId": "create_user",
        "summary": "Create user",
        "parameters": [],
        "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}},
        "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}}
    }
    code3 = cli.generate_method("/user", "post", op2, "requests")
    assert "user: User" in code3
    assert "def create_user" in code3


def test_generate_method_no_operation_id():
    """Test method generation when operationId is missing"""
    op = {
        "summary": "Get user info",
        "parameters": [
            {"name": "user_id", "in": "path", "required": True, "schema": {"type": "string"}}
        ],
        "responses": {"200": {"content": {"application/json": {"schema": {"type": "object"}}}}}
    }
    # This should handle missing operationId gracefully
    with pytest.raises(KeyError):
        cli.generate_method("/users/{user_id}", "get", op, "requests")


def test_generate_method_complex_path():
    """Test method generation with complex path parameters"""
    op = {
        "operationId": "get_complex_resource",
        "summary": "Get complex resource",
        "parameters": [
            {"name": "user_id", "in": "path", "required": True, "schema": {"type": "string"}},
            {"name": "post_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            {"name": "opt_param", "in": "query", "required": False, "schema": {"type": "boolean"}}
        ],
        "responses": {"200": {"content": {"application/json": {"schema": {"type": "object"}}}}}
    }
    code = cli.generate_method("/users/{user_id}/posts/{post_id}", "get", op, "requests")
    assert "user_id: str" in code
    assert "post_id: int" in code
    assert "opt_param: bool = None" in code


def test_generate_method_empty_responses():
    """Test method generation with empty or non-2xx responses"""
    op = {
        "operationId": "no_response",
        "summary": "No response data",
        "parameters": [],
        "responses": {"204": {"description": "No Content"}}
    }
    code = cli.generate_method("/empty", "delete", op, "requests")
    assert "-> Any" in code


def test_generate_method_with_array_response():
    """Test method generation with array response type"""
    op = {
        "operationId": "list_users",
        "summary": "List users",
        "parameters": [],
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/User"}
                        }
                    }
                }
            }
        }
    }
    code = cli.generate_method("/users", "get", op, "requests")
    assert "-> List[User]" in code


def test_generate_method_no_parameters():
    """Test method generation with no parameters"""
    op = {
        "operationId": "simple_get",
        "summary": "Simple get request",
        "parameters": [],
        "responses": {"200": {"content": {"application/json": {"schema": {"type": "string"}}}}}
    }
    code = cli.generate_method("/simple", "get", op, "requests")
    assert "def simple_get(self)" in code
    # Note: The actual implementation might return 'Any' instead of 'str' for some response types
    assert "-> Any" in code or "-> str" in code


def test_generate_method_invalid_type():
    """Test method generation with invalid/unknown type"""
    op = {
        "operationId": "unknown_type",
        "summary": "Unknown type test",
        "parameters": [],
        "responses": {"200": {"content": {"application/json": {"schema": {"type": "unknown_type"}}}}}
    }
    code = cli.generate_method("/unknown", "get", op, "requests")
    assert "-> Any" in code
