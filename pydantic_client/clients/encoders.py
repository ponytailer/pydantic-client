from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    content: str


def sse_openai_encoder(chunk: str) -> Optional[Message]:
    if not chunk.startswith("data: ") or "[DONE]" in chunk:
        return
    data = json.loads(chunk[6:])
    if "choices" not in data:
        return
    delta = data["choices"][0]["delta"]
    if "content" in delta:
        return Message(content=delta["content"])
