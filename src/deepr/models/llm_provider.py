from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Optional

class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str: ...

    def stream(self, prompt: str) -> Iterable[str]:  # default non-stream
        yield self.generate(prompt)

class DummyProvider(ModelProvider):
    def generate(self, prompt: str) -> str:  # pragma: no cover
        return f"echo: {prompt[:20]}"


class OllamaProvider(ModelProvider):
    """Simple Ollama HTTP-backed provider.

    This performs a POST to the configured Ollama HTTP endpoint. The exact
    response shape from Ollama may vary by version; the implementation
    attempts to extract a reasonable text field from common response shapes.

    Endpoints used:
    - List models: GET {base_url}/v1/models
    - Generate: POST {base_url}/api/generate
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3-coder",
        temperature: Optional[float] = 0.2,
        max_tokens: Optional[int] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        try:
            import httpx
            import json
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("httpx is required for OllamaProvider") from exc

        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt}
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens

        # Try streaming response first (Ollama often streams chunked JSON objects)
        try:
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", url, json=payload) as resp:
                    resp.raise_for_status()
                    parts: list[str] = []
                    buffer = ""
                    for chunk in resp.iter_text(chunk_size=1024):
                        if not chunk:
                            continue
                        buffer += chunk
                        # process complete lines (server often sends newline-separated JSON objects)
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue
                            # try to parse JSON line
                            try:
                                obj = json.loads(line)
                            except Exception:
                                # not JSON line, append raw
                                parts.append(line)
                                continue
                            # extract common keys
                            if isinstance(obj, dict):
                                if "response" in obj and isinstance(obj["response"], str):
                                    parts.append(obj["response"])
                                    continue
                                if "text" in obj and isinstance(obj["text"], str):
                                    parts.append(obj["text"])
                                    continue
                                if "results" in obj and isinstance(obj["results"], list):
                                    for r in obj["results"]:
                                        if isinstance(r, dict) and "content" in r and isinstance(r["content"], str):
                                            parts.append(r["content"])
                                            break
                                # fallback: try to stringify the object
                                # (rare for Ollama streaming but safe)
                                # continue to next
                    # after stream ends, if we collected parts return their concatenation
                    if parts:
                        # join without separator to preserve spacing sent by server fragments
                        return "".join(parts)
        except Exception:
            # streaming not available or failed — fall back to single-shot request
            pass

        # Single-shot request (existing behavior)
        resp = httpx.post(url, json=payload, timeout=30.0)
        resp.raise_for_status()

        try:
            data = resp.json()
        except Exception:
            return resp.text

        # Best-effort extraction of text from common response shapes
        if isinstance(data, dict):
            if "text" in data and isinstance(data["text"], str):
                return data["text"]
            if "response" in data and isinstance(data["response"], str):
                return data["response"]
            if "results" in data and isinstance(data["results"], list):
                parts: list[str] = []
                for r in data["results"]:
                    if isinstance(r, dict):
                        if "content" in r and isinstance(r["content"], str):
                            parts.append(r["content"])
                if parts:
                    return "\n".join(parts)

        # Fallback to raw response text
        return resp.text

    def list_models(self) -> list[str]:
        """Return available model ids from the Ollama server (best-effort)."""
        try:
            import httpx
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("httpx is required for OllamaProvider") from exc

        url = f"{self.base_url}/v1/models"
        resp = httpx.get(url, timeout=10.0)
        resp.raise_for_status()

        try:
            data = resp.json()
        except Exception:
            return []

        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            ids: list[str] = []
            for item in data["data"]:
                if isinstance(item, dict) and "id" in item:
                    ids.append(str(item["id"]))
            return ids

        return []


class LMStudioProvider(ModelProvider):
    """Simple LM Studio HTTP-backed provider.

    Targets LMStudio's OpenAI-compatible endpoints by default. The provider
    will try OpenAI-style chat and completion endpoints (`/v1/chat/completions`,
    `/v1/completions`) and fall back to other common paths if needed.

    Endpoints used:
    - List models: GET {base_url}/v1/models
    - Chat generate: POST {base_url}/v1/chat/completions
    - Text generate: POST {base_url}/v1/completions
    """

    def __init__(
        self,
        base_url: str = "http://localhost:1234",
        model: str = "glm-4.5-air-dwq",
        temperature: Optional[float] = 0.2,
        max_tokens: Optional[int] = None,
        endpoint: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        # if endpoint provided, it will be tried first; otherwise prefer chat
        self.endpoint = endpoint
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _extract_text(self, data) -> Optional[str]:
        """Best-effort extraction including OpenAI/LMStudio shapes."""
        # OpenAI-style responses
        if isinstance(data, dict):
            # chat/completion choices
            if "choices" in data and isinstance(data["choices"], list):
                parts: list[str] = []
                for c in data["choices"]:
                    if isinstance(c, dict):
                        # chat-style: choice.message.content
                        msg = c.get("message")
                        if isinstance(msg, dict):
                            content = msg.get("content")
                            if isinstance(content, str):
                                parts.append(content)
                                continue
                        # completion-style: choice.text
                        text = c.get("text")
                        if isinstance(text, str):
                            parts.append(text)
                            continue
                        # streaming delta
                        delta = c.get("delta")
                        if isinstance(delta, dict):
                            dcont = delta.get("content") or delta.get("text")
                            if isinstance(dcont, str):
                                parts.append(dcont)
                if parts:
                    return "\n".join(parts)
            # single-field text
            for key in ("text", "response", "generated_text", "output", "result"):
                if key in data and isinstance(data[key], str):
                    return data[key]
            # outputs / results lists
            if "outputs" in data and isinstance(data["outputs"], list):
                collected: list[str] = []
                for o in data["outputs"]:
                    if isinstance(o, dict):
                        for k in ("generated_text", "text", "content"):
                            if k in o and isinstance(o[k], str):
                                collected.append(o[k])
                    elif isinstance(o, str):
                        collected.append(o)
                if collected:
                    return "\n".join(collected)
            if "results" in data and isinstance(data["results"], list):
                collected: list[str] = []
                for r in data["results"]:
                    if isinstance(r, dict):
                        for k in ("content", "text", "generated_text"):
                            if k in r and isinstance(r[k], str):
                                collected.append(r[k])
                if collected:
                    return "\n".join(collected)
        elif isinstance(data, str):
            return data
        return None

    def generate(self, prompt: str) -> str:
        try:
            import httpx
            import json
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("httpx is required for LMStudioProvider") from exc

        # Prefer OpenAI-compatible endpoints
        candidate_paths = []
        if self.endpoint:
            candidate_paths.append(self.endpoint)
        candidate_paths.extend(["/v1/chat/completions", "/v1/completions", "/api/generate", "/api/v1/generate", "/generate"]) 

        def build_url(path: str) -> str:
            if path.startswith("http://") or path.startswith("https://"):
                return path
            if not path.startswith("/"):
                path = "/" + path
            return f"{self.base_url}{path}"

        # Prepare OpenAI-style payloads first (chat then completion)
        params = {}
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        payload_variants = [
            # chat-style
            {"model": self.model, "messages": [{"role": "user", "content": prompt}], **({} if not params else {k: v for k, v in params.items()})},
            # completion-style
            {"model": self.model, "prompt": prompt, **({} if not params else {k: v for k, v in params.items()})},
            # generic shapes
            {"model": self.model, "inputs": prompt},
            {"inputs": prompt},
            {"input": prompt},
        ]

        last_exc: Optional[Exception] = None
        for path in candidate_paths:
            url = build_url(path)
            for payload in payload_variants:
                try:
                    resp = httpx.post(url, json=payload, timeout=30.0)
                    resp.raise_for_status()
                except Exception as exc:  # try next combination
                    last_exc = exc
                    continue

                try:
                    data = resp.json()
                except Exception:
                    return resp.text

                text = self._extract_text(data)
                if text is not None:
                    return text

                return resp.text

        if last_exc is not None:
            raise RuntimeError(f"LMStudio generation failed: {last_exc}") from last_exc
        return ""

    def stream(self, prompt: str) -> Iterable[str]:
        """Attempt streaming generation with OpenAI-style parsing (data: chunks).

        Falls back to non-stream generate() if streaming unsupported.
        """
        try:
            import httpx
            import json
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("httpx is required for LMStudioProvider") from exc

        candidate_paths = []
        if self.endpoint:
            candidate_paths.append(self.endpoint)
        candidate_paths.extend(["/v1/chat/completions", "/v1/completions", "/api/generate", "/generate"]) 

        params = {}
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
        if params:
            payload.update(params)

        def build_url(path: str) -> str:
            if path.startswith("http://") or path.startswith("https://"):
                return path
            if not path.startswith("/"):
                path = "/" + path
            return f"{self.base_url}{path}"

        last_exc: Optional[Exception] = None
        yielded_any = False
        for path in candidate_paths:
            url = build_url(path)
            try:
                with httpx.Client(timeout=60.0) as client:
                    with client.stream("POST", url, json=payload) as resp:
                        resp.raise_for_status()
                        # stream may come as SSE-like lines starting with 'data: '
                        buffer = ""
                        for chunk in resp.iter_text(chunk_size=1024):
                            if not chunk:
                                continue
                            buffer += chunk
                            # process completed lines
                            while "\n" in buffer:
                                line, buffer = buffer.split("\n", 1)
                                line = line.strip()
                                if not line:
                                    continue
                                # OpenAI-style SSE: lines prefixed with 'data: '
                                if line.startswith("data:"):
                                    payload_line = line[len("data:"):].strip()
                                    if payload_line == "[DONE]":
                                        if yielded_any:
                                            return
                                        # if nothing yielded yet, break to try fallback endpoints
                                        raise RuntimeError("stream signaled done without chunks")
                                    try:
                                        obj = json.loads(payload_line)
                                    except Exception:
                                        yielded_any = True
                                        yield payload_line
                                        continue
                                    # try to extract incremental delta content
                                    # choices[].delta.content or choices[].message.content
                                    if isinstance(obj, dict) and "choices" in obj:
                                        for c in obj["choices"]:
                                            if isinstance(c, dict):
                                                # delta-based streaming
                                                delta = c.get("delta")
                                                if isinstance(delta, dict):
                                                    dcont = delta.get("content") or delta.get("text")
                                                    if isinstance(dcont, str):
                                                        yielded_any = True
                                                        yield dcont
                                                        continue
                                                # full message in streaming chunk
                                                msg = c.get("message")
                                                if isinstance(msg, dict):
                                                    cont = msg.get("content")
                                                    if isinstance(cont, str):
                                                        yielded_any = True
                                                        yield cont
                                                        continue
                                                txt = c.get("text")
                                                if isinstance(txt, str):
                                                    yielded_any = True
                                                    yield txt
                                                    continue
                                    # fallback: try full-object extraction
                                    t = self._extract_text(obj)
                                    if t:
                                        yielded_any = True
                                        yield t
                                else:
                                    # not SSE, try parsing as JSON
                                    try:
                                        obj = json.loads(line)
                                        t = self._extract_text(obj)
                                        if t:
                                            yielded_any = True
                                            yield t
                                            continue
                                    except Exception:
                                        yielded_any = True
                                        yield line
                        # if stream ended normally, return if we yielded something
                        if yielded_any:
                            return
                        # otherwise continue to next candidate path
            except Exception as exc:
                last_exc = exc
                continue

        # streaming failed for all endpoints or produced no chunks -> fallback
        try:
            gen_out = self.generate(prompt)
        except Exception as exc:
            raise RuntimeError("LMStudio streaming and fallback generate both failed") from exc
        # yield generate output as a single chunk
        yield gen_out

    def list_models(self) -> list[str]:
        """List models using LMStudio's OpenAI-compatible `/v1/models` endpoint."""
        try:
            import httpx
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("httpx is required for LMStudioProvider") from exc

        url = f"{self.base_url}/v1/models"
        try:
            resp = httpx.get(url, timeout=10.0)
            resp.raise_for_status()
        except Exception:
            return []

        try:
            data = resp.json()
        except Exception:
            return []

        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            ids: list[str] = []
            for item in data["data"]:
                if isinstance(item, dict) and "id" in item:
                    ids.append(str(item["id"]))
            return ids
        return []


__all__ = ["ModelProvider", "DummyProvider", "OllamaProvider", "LMStudioProvider"]
