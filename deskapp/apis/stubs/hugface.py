from ..base import Provider
from ..keys import has_api_key


class HugfaceProvider(Provider):
    name = "hugface"

    def status(self) -> str:
        return "hugface: ready" if has_api_key("hugface") else "hugface: no key"
