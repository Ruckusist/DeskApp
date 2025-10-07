from ..base import Provider


class OpenAIProvider(Provider):
    name = "openai"

    def status(self) -> str:
        return "openai: stub"
