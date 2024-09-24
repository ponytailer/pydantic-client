from typing import Dict, Any

from pydantic import BaseModel


class ClientConfig(BaseModel):
    base_url: str
    headers: Dict[str, Any] = {}
    http2: bool = False

    @classmethod
    def load_toml(cls, path: str):
        try:
            import toml
        except ImportError:
            raise ImportError("toml is required, please install it using pip")

        with open(path) as f:
            config = toml.load(f)
            cfg = config.get("tools", {}) \
                .get("pydantic-client", {}).get("config")
            if not cfg:
                raise ValueError("`tools.pydantic-client.config` not found in toml file")  # noqa
            return cls(**cfg)
