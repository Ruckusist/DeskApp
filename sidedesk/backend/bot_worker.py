"""
BotWorker
Decouple AI/bot calls from the main runtime using a background thread.
Added by: GitHub Copilot on 10-09-25

Responsibilities:
- Accept chat requests and stream response chunks via queues.
- Support attach/detach of an Ollama-like client.
- Allow cancellation and clean shutdown.
"""

from __future__ import annotations

import threading
import queue
import time
from typing import Any, Dict, List, Optional


class BotWorker:
    """Background worker for model chat streaming."""

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._cancel = threading.Event()
        self._lock = threading.RLock()
        self._client = None  # set via attach_client()
        self._request_q: queue.Queue[Dict[str, Any]] = queue.Queue()
        self._stream_q: queue.Queue[Dict[str, Any]] = queue.Queue()
        self._busy = False
        self._job_id = 0

    def attach_client(self, client: Any) -> None:
        with self._lock:
            self._client = client

    def detach_client(self) -> None:
        with self._lock:
            self._client = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, name="BotWorker", daemon=True
        )
        self._thread.start()

    def stop(self, timeout: float = 1.0) -> None:
        self._stop.set()
        self._cancel.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def cancel(self) -> None:
        self._cancel.set()

    def submit(self, user: str, text: str) -> int:
        """Submit a new job; returns job_id."""
        with self._lock:
            self._job_id += 1
            job_id = self._job_id
        self._request_q.put({
            "id": job_id,
            "user": user,
            "text": text,
        })
        return job_id

    def fetch_stream(self, max_items: int = 64) -> List[Dict[str, Any]]:
        """Drain up to max_items stream messages without blocking."""
        out: List[Dict[str, Any]] = []
        for _ in range(max_items):
            try:
                item = self._stream_q.get_nowait()
            except queue.Empty:
                break
            else:
                out.append(item)
        return out

    def is_busy(self) -> bool:
        return self._busy

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                job = self._request_q.get(timeout=0.1)
            except queue.Empty:
                continue

            self._cancel.clear()
            self._busy = True
            job_id = job.get("id")
            text = job.get("text", "")

            client = None
            with self._lock:
                client = self._client

            if client is None or not getattr(client, "IsConnected", lambda: False)():
                self._stream_q.put({
                    "id": job_id,
                    "text": "Ollama disconnected",
                    "done": True,
                    "error": True,
                })
                self._busy = False
                continue

            try:
                # Stream chunks from the model client
                for chunk in client.Chat(text, stream=True):
                    if self._cancel.is_set() or self._stop.is_set():
                        break
                    if chunk:
                        self._stream_q.put({
                            "id": job_id,
                            "text": chunk,
                            "done": False,
                        })
                # Signal done unless we were cancelled
                self._stream_q.put({
                    "id": job_id,
                    "text": "",
                    "done": True,
                })
            except Exception as e:  # noqa: BLE001
                self._stream_q.put({
                    "id": job_id,
                    "text": f"Ollama error: {e}",
                    "done": True,
                    "error": True,
                })
            finally:
                self._busy = False
                # Small pause to avoid hot loop on repeated errors
                time.sleep(0.01)
