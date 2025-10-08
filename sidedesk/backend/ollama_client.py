"""
Ollama Client for SideDesk
Manages connection and inference with Ollama LLM
Created by: Claude Sonnet 4.5
Date: 10-06-25
"""

import ollama
from typing import Generator, List, Dict, Optional, Any


class OllamaClient:
    """
    Client for interacting with Ollama LLM service.
    Handles model loading, conversation management, and streaming.
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2",
        temperature: float = 0.7,
        context_window: int = 4096
    ):
        """
        Initialize Ollama client.

        Args:
            host: Ollama server URL
            model: Default model to use
            temperature: Sampling temperature
            context_window: Maximum context length
        """
        self.host = host
        self.model = model
        self.temperature = temperature
        self.context_window = context_window
        self.client = ollama.Client(host=host)
        self.conversation_history: List[Dict[str, str]] = []

    def Chat(
        self,
        message: str,
        stream: bool = True,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None] | str:
        """
        Send a chat message and get response.

        Args:
            message: User message
            stream: Whether to stream response
            system_prompt: Optional system prompt

        Returns:
            Generator yielding response chunks or full response
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=stream,
                options={
                    "temperature": self.temperature,
                    "num_ctx": self.context_window
                }
            )

            if stream:
                full_response = ""
                for chunk in response:
                    content = chunk.get("message", {}).get(
                        "content",
                        ""
                    )
                    full_response += content
                    yield content

                self.conversation_history.append({
                    "role": "user",
                    "content": message
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": full_response
                })
            else:
                content = response.get("message", {}).get(
                    "content",
                    ""
                )
                self.conversation_history.append({
                    "role": "user",
                    "content": message
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": content
                })
                return content

        except Exception as e:
            error_msg = f"Ollama error: {str(e)}"
            yield error_msg if stream else error_msg

    def Generate(
        self,
        prompt: str,
        stream: bool = True
    ) -> Generator[str, None, None] | str:
        """
        Generate text from prompt (non-chat mode).

        Args:
            prompt: Input prompt
            stream: Whether to stream response

        Returns:
            Generator yielding response or full response
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=stream,
                options={
                    "temperature": self.temperature,
                    "num_ctx": self.context_window
                }
            )

            if stream:
                for chunk in response:
                    yield chunk.get("response", "")
            else:
                return response.get("response", "")

        except Exception as e:
            error_msg = f"Ollama error: {str(e)}"
            yield error_msg if stream else error_msg

    def ListModels(self) -> List[str]:
        """
        Get list of available models.

        Returns:
            List of model names
        """
        try:
            models = self.client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception:
            return []

    def SwitchModel(self, model: str) -> bool:
        """
        Switch to different model.

        Args:
            model: Model name to switch to

        Returns:
            True if successful
        """
        available = self.ListModels()
        if model in available:
            self.model = model
            return True
        return False

    def ClearHistory(self):
        """Clear conversation history."""
        self.conversation_history = []

    def GetHistory(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def PruneHistory(self, max_turns: int = 10):
        """
        Prune conversation history to max turns.

        Args:
            max_turns: Maximum number of turns to keep
        """
        if len(self.conversation_history) > max_turns * 2:
            self.conversation_history = (
                self.conversation_history[-(max_turns * 2):]
            )

    def IsConnected(self) -> bool:
        """
        Check if Ollama server is reachable.

        Returns:
            True if connected
        """
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def GetModelInfo(self) -> Dict[str, Any]:
        """
        Get information about current model.

        Returns:
            Model information dict
        """
        try:
            info = self.client.show(self.model)
            return info
        except Exception:
            return {}
