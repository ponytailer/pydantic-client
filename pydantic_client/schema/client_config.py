import logging
from typing import Dict, Any, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ClientConfig(BaseModel):
    base_url: str
    headers: Dict[str, Any] = {}
    http2: bool = False
    timeout: Optional[int] = None

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
                raise ValueError(
                    "`tools.pydantic-client.config` not found in toml file")  # noqa
            return cls(**cfg)


class FactoryConfig(BaseModel):
    config: Dict[str, ClientConfig]

    def get_by_name(self, name: str) -> Optional[ClientConfig]:
        return self.config.get(name)

    @classmethod
    def load_toml(cls, path: str):
        try:
            import toml
        except ImportError:
            raise ImportError("toml is required, please install it using pip")

        with open(path) as f:
            config = toml.load(f)
            cfg = config.get("tools", {}) \
                .get("pydantic-client", {}).get("factory", [])
            if not cfg:
                raise ValueError(
                    "`tools.pydantic-client.factory` not found in toml file")  # noqa

            factory_config = {}
            for config in cfg:
                name = config.pop("name", None)
                if not name:
                    logger.warning("name not found in factory config")
                    continue
                factory_config[name] = ClientConfig(**config)

            return cls(config=factory_config)
