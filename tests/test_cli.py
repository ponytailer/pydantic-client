import sys
import yaml
import subprocess

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
    assert len(result) == 2  # body parameter should be filtered out
    assert result[0]["name"] == "id"
    assert result[0]["type"] == "str"
    assert result[0]["required"] is True
    assert result[1]["name"] == "opt"
    assert result[1]["type"] == "int"
    assert result[1]["required"] is False


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


def test_sanitize_name_with_python_keywords():
    # Test that Python keywords are sanitized
    assert cli.sanitize_name("import") == "import_"
    assert cli.sanitize_name("from") == "from_"
    assert cli.sanitize_name("class") == "class_"
    assert cli.sanitize_name("def") == "def_"
    assert cli.sanitize_name("return") == "return_"
    assert cli.sanitize_name("lambda") == "lambda_"
    # Non-keywords should remain unchanged
    assert cli.sanitize_name("id") == "id"
    assert cli.sanitize_name("name") == "name"
    assert cli.sanitize_name("email") == "email"


def test_sanitize_name_with_invalid_identifiers():
    # Test that invalid Python identifiers are sanitized
    # Hyphens should be replaced with underscores
    assert cli.sanitize_name("x-immich-checksum") == "x_immich_checksum"
    assert cli.sanitize_name("user-id") == "user_id"
    assert cli.sanitize_name("api-key") == "api_key"
    # Other non-alphanumeric characters should be replaced
    assert cli.sanitize_name("user.id") == "user_id"
    assert cli.sanitize_name("user@name") == "user_name"
    # Combination: invalid chars + keyword
    assert cli.sanitize_name("x-import") == "x_import"
    # Underscores should be preserved
    assert cli.sanitize_name("user_id") == "user_id"
    assert cli.sanitize_name("user_name") == "user_name"


def test_gen_pydantic_model_with_keywords():
    # Test that model fields with Python keywords are sanitized
    schema = {
        "type": "object",
        "required": ["id", "import"],
        "properties": {
            "id": {"type": "string"},
            "import": {"type": "string"},
            "from": {"type": "string"},
            "class": {"type": "integer"}
        }
    }
    code = cli.gen_pydantic_model("Doc", schema, {})
    assert "id: str" in code
    assert "import_: str" in code
    assert "from_: str = None" in code
    assert "class_: int = None" in code


def test_parse_parameters_with_keywords():
    # Test that parameters with Python keywords are sanitized
    params = [
        {"name": "id", "in": "query", "required": True, "schema": {"type": "string"}},
        {"name": "import", "in": "query", "required": True, "schema": {"type": "string"}},
        {"name": "from", "in": "query", "required": False, "schema": {"type": "string"}},
    ]
    result = cli.parse_parameters(params)
    assert len(result) == 3
    assert result[0]["name"] == "id"
    assert result[0]["required"] is True
    assert result[1]["name"] == "import_"
    assert result[1]["required"] is True
    assert result[2]["name"] == "from_"
    assert result[2]["required"] is False


def test_cli_generates_client_with_keywords(tmp_path):
    # Test end-to-end CLI with Python keywords in schema
    swagger = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0"},
        "paths": {
            "/doc": {
                "get": {
                    "operationId": "get_doc",
                    "parameters": [
                        {"name": "import", "in": "query", "required": True, "schema": {"type": "string"}},
                        {"name": "from", "in": "query", "required": False, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Doc"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Doc": {
                    "type": "object",
                    "required": ["id", "import"],
                    "properties": {
                        "id": {"type": "string"},
                        "import": {"type": "string"},
                        "from": {"type": "string"},
                        "class": {"type": "integer"}
                    }
                }
            }
        }
    }
    swagger_file = tmp_path / "swagger_keywords.yaml"
    with open(swagger_file, "w") as f:
        yaml.dump(swagger, f)

    output_file = tmp_path / "client_with_keywords.py"
    result = run_cli(["-f", str(swagger_file), "-t", "requests", "-o", str(output_file)])
    assert result.returncode == 0
    assert output_file.exists()

    code = output_file.read_text()
    # Check BaseModel fields are sanitized
    assert "import_: str" in code
    assert "from_: str = None" in code
    assert "class_: int = None" in code
    # Check method parameters are sanitized
    assert "def get_doc(self, import_: str, from_: str = None)" in code


def test_generate_method_with_parameter_ordering():
    # Test that required parameters come before optional parameters
    # regardless of their order in the spec
    op = {
        "operationId": "add_assets_to_album",
        "summary": "Add assets to album",
        "parameters": [
            {"name": "key", "in": "query", "required": False, "schema": {"type": "string"}},
            {"name": "slug", "in": "query", "required": False, "schema": {"type": "string"}},
            {"name": "bulkidsdto", "in": "query", "required": True, "schema": {"type": "string"}},
        ],
        "responses": {"200": {"content": {"application/json": {"schema": {"type": "string"}}}}}
    }
    code = cli.generate_method("/albums/{id}/assets", "put", op, "requests")
    # Required parameter (bulkidsdto) should come before optional ones (key, slug)
    assert "def add_assets_to_album(self, bulkidsdto: str, key: str = None, slug: str = None)" in code


def test_cli_generates_client_with_invalid_identifiers(tmp_path):
    # Test end-to-end CLI with invalid Python identifiers in schema
    swagger = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0"},
        "paths": {
            "/upload": {
                "post": {
                    "operationId": "upload_asset",
                    "parameters": [
                        {"name": "x-immich-checksum", "in": "header", "required": True, "schema": {"type": "string"}},
                        {"name": "api-key", "in": "header", "required": False, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Asset"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Asset": {
                    "type": "object",
                    "required": ["id", "user-id"],
                    "properties": {
                        "id": {"type": "string"},
                        "user-id": {"type": "string"},
                        "file.name": {"type": "string"},
                        "x-original-name": {"type": "string"}
                    }
                }
            }
        }
    }
    swagger_file = tmp_path / "swagger_identifiers.yaml"
    with open(swagger_file, "w") as f:
        yaml.dump(swagger, f)

    output_file = tmp_path / "client_identifiers.py"
    result = run_cli(["-f", str(swagger_file), "-t", "requests", "-o", str(output_file)])
    assert result.returncode == 0
    assert output_file.exists()

    code = output_file.read_text()
    # Check BaseModel fields are sanitized
    assert "id: str" in code
    assert "user_id: str" in code
    assert "file_name: str = None" in code
    assert "x_original_name: str = None" in code
    # Check method parameters are sanitized
    assert "def upload_asset(self, x_immich_checksum: str, api_key: str = None)" in code
