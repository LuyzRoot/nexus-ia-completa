from typing import Protocol, Any

class Skill(Protocol):
    name: str

    def run(self, input: dict) -> dict:
        ...
