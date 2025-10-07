import os
from typing import List, Optional, Dict, Any
from google import genai  # type: ignore
from google.genai import types as genai_types
from openai import models  # type: ignore

from ..base import Provider
from ..keys import get_api_key


class GeminiProvider(Provider):
    name = "gemini"
    cached_models: List[str] = []

    def get_client(self):
        key = get_api_key('gemini')
        if not hasattr(self, 'client'):
            try:
                self.client = genai.GenerativeModel(api_key=key)  # type: ignore
            except Exception:
                return None
        return getattr(self, 'client', None)

    # ---- public API ----
    def list_models(self, refresh: bool = False) -> List[str]:
        if refresh:
            self.cached_models = []
        if self.cached_models:
            return self.cached_models
        models: List[str] = []
        # Prefer new client
        client = self.get_client()
        if client is not None:
            try:
                for m in client.models.list():  # type: ignore
                    name = getattr(m, 'name', '') or ''
                    if name.startswith('models/'):
                        name = name.split('/', 1)[1]
                    if name:
                        models.append(name)
            except Exception:
                pass

        if models:
            self.cached_models = models

        return sorted(models)

    def response(self,
                 prompt: str,
                 system: Optional[str] = None,
                 model: Optional[str] = None,
                 temperature: float = 0.8,
                 top_p: float = 0.95,
                 top_k: int = 40,
                 thinking_budget: int = -1,
                 ) -> Optional[str]:
        # Choose model
        if not model: model = self.list_models()[0]
        model_id = model
        if not model_id: return None

        context = prompt if not system else f"{system}\n\n{prompt}"

        # New client path
        client = self.get_client()
        cfg = {"temperature": temperature, "top_p": top_p, }

        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": content}
            ],
            **cfg
        )

                # Add thinking config if types module available
        #         if genai_types is not None:
        #             try:
        #                 cfg_obj = genai_types.GenerateContentConfig(  # type: ignore
        #                     thinking_config=genai_types.ThinkingConfig(thinking_budget=thinking_budget),  # type: ignore
        #                     **{k: v for k, v in cfg.items() if v is not None}
        #                 )
        #             except Exception:
        #                 cfg_obj = None
        #         else:
        #             cfg_obj = None
        #         resp = client.models.generate_content(  # type: ignore
        #             model=model_id,
        #             contents=content,
        #             config=cfg_obj if cfg_obj else None,
        #         )
        #         text = getattr(resp, 'text', None)
        #         if text:
        #             return text.strip()
        #         # New client candidate parsing
        #         cand = getattr(resp, 'candidates', None)
        #         if cand:
        #             texts: List[str] = []
        #             try:
        #                 for c in cand:  # type: ignore
        #                     ct = getattr(c, 'content', None)
        #                     parts = getattr(ct, 'parts', []) if ct else []
        #                     for p in parts:
        #                         t = getattr(p, 'text', None)
        #                         if t:
        #                             texts.append(t)
        #             except Exception:
        #                 pass
        #             if texts:
        #                 return "\n".join(texts).strip()
        #         if debug:
        #             print(f"[gemini] empty response for model {model_id}")
        #     except Exception as e:
        #         if 'GEMINI_DEBUG' in os.environ:
        #             print(f"[gemini] error new-client: {e}")
        #     # fall through to old client fallback if empty
        # # Old client fallback

        return None

    # Backwards compatibility alias
    def generate(self, prompt: str, **kwargs):  # type: ignore
        return self.response(prompt, **kwargs)

    def status(self) -> str:
        if not self._get_api_key():
            return "gemini: no-key"
        base = "gemini: ready"
        if not self.cached_models:
            return base + " (no-cached-models)"
        return base


def main():  # simple manual test hook
    p = GeminiProvider()
    print(p.status())
    print(p.list_models(refresh=True))
    print(p.response("Write a concise haiku about synergy."))


if __name__ == "__main__":  # pragma: no cover
    main()
