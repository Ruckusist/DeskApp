import os
import ollama
from typing import List, Optional, Tuple, Any

from deskapp.apis import Provider


class OllamaProvider(Provider):
    name = "ollama"

    def list_models(self) -> List[Tuple[str, Any, Any]]:
        """Return a list of tuples: (model_name, parameter_size, disk_size_bytes).

        Keeps full detail for callers that want it; UI layers can extract just
        the first element. Prints are suppressed unless OLLAMA_VERBOSE is set.
        """
        local_models = ollama.list()  # dict with 'models'
        models_list = local_models.get('models', [])
        return [
            (
                model.get('model', 'unknown'),
                model.get('details', {}).get('parameter_size', 0),
                model.get('size', 0)
            ) for model in models_list
        ]

    def response(self,
                 prompt: str,
                 system: Optional[str] = None,
                 model: Optional[str] = None,
                 temperature: float = 0.8,
                 top_p: float = 0.95,
                 top_k: int = 40,
                 seed: Optional[int] = 420,
                 stream: bool = False,
                 formats: str = "text",
                 keep_alive: bool = False,
                 ) -> Optional[str]:
        """Return a single chat style response string for the given prompt."""
        if model is None:
            model = "qwen2.5-coder:0.5b"
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system or "I am a code master."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "seed": seed,
                },
                stream=stream,
                # format=formats,
                keep_alive=keep_alive
            )
            return response['message']['content'] if response else f'{model}: No response'
        except Exception as e:
            if self._verbose():
                print(f"[ollama] response error: {e}")
            return None

    # Backwards compatibility shim (older code expected .generate)
    def generate(self, prompt: str, **kwargs):  # type: ignore
        return self.response(prompt, **kwargs)

    def status(self) -> str:
        return "ollama: online"


def main():
    provider = OllamaProvider()
    print(provider.status())
    print(provider.response("a quick hiku", system="You are a poet."))
    print(provider.list_models())

if __name__ == "__main__":
    main()
