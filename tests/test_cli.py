import sys
import yaml
import subprocess


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
