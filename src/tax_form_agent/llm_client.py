# ─────────────────────────────────────────────────────────────────────────────
# HTTP client for the OpenAI Chat Completions API
# ─────────────────────────────────────────────────────────────────────────────

import json
import http.client
import time
from typing import List, Optional


class LLMClient:
    MODEL = "gpt-4o-mini"
    HOST  = "api.openai.com"
    PATH  = "/v1/chat/completions"

    def __init__(self, api_key: str, model: Optional[str] = None):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        if model:
            self.MODEL = model

    def complete(self,
                 messages: List[dict],
                 system: str = "",
                 max_tokens: int = 800,
                 temperature: float = 0.2,
                 timeout: int = 60,
                 retries: int = 2) -> str:

        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload = {
            "model":       self.MODEL,
            "messages":    full_messages,
            "max_tokens":  max_tokens,
            "temperature": temperature,
        }

        body    = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization":  f"Bearer {self.api_key}",
            "Content-Type":   "application/json",
            "Content-Length": str(len(body)),
        }

        last_error = None
        for attempt in range(retries + 1):
            try:
                conn = http.client.HTTPSConnection(self.HOST, timeout=timeout)
                try:
                    conn.request("POST", self.PATH, body=body, headers=headers)
                    resp = conn.getresponse()
                    raw  = resp.read().decode("utf-8")
                finally:
                    conn.close()

                data = json.loads(raw)

                if resp.status != 200:
                    err = data.get("error", {})
                    raise RuntimeError(
                        f"OpenAI API error {resp.status}: "
                        f"{err.get('type', '?')} — {err.get('message', raw[:200])}"
                    )

                return data["choices"][0]["message"]["content"].strip()

            except (TimeoutError, OSError) as e:
                last_error = e
                if attempt < retries:
                    wait = 2 ** attempt  # 1s, 2s
                    print(f"[llm_client] Timeout on attempt {attempt + 1}, retrying in {wait}s")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"Request timed out after {retries + 1} attempts: {e}")

        raise RuntimeError(f"All attempts failed: {last_error}")

    def complete_json(self,
                      messages: List[dict],
                      system: str = "",
                      max_tokens: int = 400) -> dict:
        try:
            text = self.complete(
                messages=messages,
                system=system,
                max_tokens=max_tokens,
                temperature=0.0,
                timeout=30,
                retries=2,
            )
        except RuntimeError as e:
            return {"error": str(e)}

        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"error": text}