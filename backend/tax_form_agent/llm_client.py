# ─────────────────────────────────────────────────────────────────────────────
# HTTP client for the OpenAI Chat Completions API
# ─────────────────────────────────────────────────────────────────────────────

import json
import http.client
import socket
import ssl
import time
from typing import Iterator, List, Optional


def _ssl_context() -> ssl.SSLContext:
    """SSL context backed by certifi's CA bundle.
    Falls back to the system default if certifi is unavailable. Using certifi
    avoids 'unable to get local issuer certificate' errors on Windows machines
    whose cert store is missing intermediates Python can't auto-fetch."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _resolve_via_doh(name: str, timeout: float = 5.0) -> Optional[str]:
    """Resolve `name` (A record) via Cloudflare DNS-over-HTTPS at 1.1.1.1.
    Returns an IPv4 string, or None on any failure."""
    try:
        c = http.client.HTTPSConnection(
            "1.1.1.1", 443, timeout=timeout, context=_ssl_context()
        )
        try:
            c.request(
                "GET",
                f"/dns-query?name={name}&type=A",
                headers={"Accept": "application/dns-json"},
            )
            r = c.getresponse()
            if r.status != 200:
                return None
            data = json.loads(r.read())
        finally:
            c.close()
        for ans in (data.get("Answer") or []):
            if ans.get("type") == 1:
                ip = ans.get("data")
                if ip:
                    return ip
    except Exception:
        return None
    return None


def open_https_resilient(host: str, port: int = 443, timeout: int = 30
                         ) -> http.client.HTTPSConnection:
    """Open an HTTPSConnection to host:port and connect.
    First tries system DNS. If that fails (some routers have flaky DNS for
    specific names — e.g. api.openai.com), falls back to Cloudflare DoH and
    connects by IP while keeping correct SNI and Host header for the original
    hostname. Always uses certifi's CA bundle for cert verification."""
    ctx = _ssl_context()

    conn = http.client.HTTPSConnection(host, port, timeout=timeout, context=ctx)
    try:
        conn.connect()
        return conn
    except (socket.gaierror, socket.timeout, OSError):
        try:
            conn.close()
        except Exception:
            pass

    ip = _resolve_via_doh(host)
    if not ip:
        # No fallback path available — let the caller see the original error.
        conn2 = http.client.HTTPSConnection(host, port, timeout=timeout, context=ctx)
        conn2.connect()
        return conn2

    class _IPHTTPSConnection(http.client.HTTPSConnection):
        def connect(self):
            sock = socket.create_connection((ip, port), self.timeout)
            self.sock = self._context.wrap_socket(sock, server_hostname=host)

    conn3 = _IPHTTPSConnection(host, port, timeout=timeout, context=ctx)
    conn3.connect()
    return conn3


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
                conn = open_https_resilient(self.HOST, timeout=timeout)
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
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"Request timed out after {retries + 1} attempts: {e}")

        raise RuntimeError(f"All attempts failed: {last_error}")

    def stream_complete(self,
                        messages: List[dict],
                        system: str = "",
                        max_tokens: int = 800,
                        temperature: float = 0.2,
                        timeout: int = 60) -> Iterator[str]:
        """Stream completion as Server-Sent Events. Yields content tokens as
        they arrive from OpenAI. No retries — if the connection drops mid-
        stream, the caller sees a truncated response."""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload = {
            "model":       self.MODEL,
            "messages":    full_messages,
            "max_tokens":  max_tokens,
            "temperature": temperature,
            "stream":      True,
        }
        body    = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization":  f"Bearer {self.api_key}",
            "Content-Type":   "application/json",
            "Content-Length": str(len(body)),
            "Accept":         "text/event-stream",
        }

        conn = open_https_resilient(self.HOST, timeout=timeout)
        try:
            conn.request("POST", self.PATH, body=body, headers=headers)
            resp = conn.getresponse()

            if resp.status != 200:
                raw = resp.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"OpenAI API error {resp.status}: {raw[:300]}")

            # Read SSE events: lines like "data: {json}\n" separated by blank lines.
            while True:
                line = resp.readline()
                if not line:
                    break
                line = line.strip()
                if not line or not line.startswith(b"data:"):
                    continue
                payload_str = line[5:].lstrip().decode("utf-8", errors="replace")
                if payload_str == "[DONE]":
                    break
                try:
                    event = json.loads(payload_str)
                    delta = event.get("choices", [{}])[0].get("delta", {}).get("content")
                    if delta:
                        yield delta
                except (json.JSONDecodeError, IndexError, KeyError):
                    continue
        finally:
            try:
                conn.close()
            except Exception:
                pass

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