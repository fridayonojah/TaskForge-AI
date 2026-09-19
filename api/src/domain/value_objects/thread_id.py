from __future__ import annotations
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class ThreadId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("ThreadId cannot be empty")

    @classmethod
    def generate(cls) -> ThreadId:
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_optional(cls, value: str | None) -> ThreadId:
        return cls(value=value) if value else cls.generate()
