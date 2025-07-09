from typing import Optional


class File:
    """Represents a file response"""
    def __init__(self, content: bytes, filename: Optional[str] = None, content_type: Optional[str] = None):
        self.content: bytes = content
        self.filename: Optional[str] = filename
        self.content_type: Optional[str] = content_type

    @property
    def text(self) -> str:
        """Return the file content as text"""
        return self.content.decode()