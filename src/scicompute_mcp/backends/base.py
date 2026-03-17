from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


@dataclass
class TextContent:
    type: Literal["text"] = "text"
    text: str = ""


@dataclass
class ImageContent:
    type: Literal["image"] = "image"
    data: str = ""
    mimeType: str = "image/png"


@dataclass
class AudioContent:
    type: Literal["audio"] = "audio"
    data: str = ""
    mimeType: str = "audio/wav"


@dataclass
class ErrorContent:
    type: Literal["error"] = "error"
    message: str = ""


Content = TextContent | ImageContent | AudioContent | ErrorContent


@dataclass
class Result:
    success: bool
    content: list[Content]


class ComputeBackend(ABC):
    name: str
    description: str
    capabilities: list[str]
    
    _started: bool = False
    
    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if this backend is available on the system."""
        ...
    
    @abstractmethod
    def start(self) -> bool:
        """Start the backend (e.g., initialize kernel session)."""
        ...
    
    @abstractmethod
    def evaluate(self, code: str, timeout: float = 30.0) -> Result:
        """Execute code and return result."""
        ...
    
    @abstractmethod
    def reset(self) -> None:
        """Reset backend state, clear all variables."""
        ...
    
    def stop(self) -> None:
        """Stop the backend."""
        self._started = False