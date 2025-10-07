from typing import Any, Dict


class Provider:
    """Abstract provider interface. Concrete providers should extend this.

    Minimal contract for now; can expand with async methods later.
    """

    name: str = "provider"

    def __init__(self, **config: Any) -> None:
        self.config: Dict[str, Any] = dict(config)

    def status(self) -> str:
        return f"{self.name}: ready"

    def info(self) -> Dict[str, Any]:
        return {"name": self.name, "config": self.config}
