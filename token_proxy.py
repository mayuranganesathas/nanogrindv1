"""
Token logging proxy — sits between nanobot and llama-server.
Forwards all requests to the upstream LLM, logs token usage from each response.

Usage:
    .venv/bin/python token_proxy.py

Config: nanobot apiBase → http://localhost:18791/v1
        This proxy forwards → http://10.0.0.132:8080/v1
"""
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route
import uvicorn

UPSTREAM = os.environ.get("PROXY_UPSTREAM", "http://10.0.0.132:8080")
LISTEN_PORT = int(os.environ.get("PROXY_PORT", "18791"))
LOG_DIR = Path(os.environ.get("PROXY_LOG_DIR", Path.home() / "nanogrindv2/logs"))

LOG_DIR.mkdir(parents=True, exist_ok=True)


def _today_pst() -> str:
    pst = datetime.now(timezone.utc) + timedelta(hours=-7)
    return pst.strftime("%Y-%m-%d")


def _now_pst() -> str:
    pst = datetime.now(timezone.utc) + timedelta(hours=-7)
    return pst.strftime("%H:%M:%S")


def _log_tokens(path: str, usage: dict, elapsed_ms: float | None) -> None:
    today = _today_pst()
    log_file = LOG_DIR / f"tokens-{today}.log"
    prompt = usage.get("prompt_tokens", "?")
    completion = usage.get("completion_tokens", "?")
    total = usage.get("total_tokens", "?")
    elapsed = f"{elapsed_ms:.0f}ms" if elapsed_ms is not None else "?"
    line = (
        f"{_now_pst()} | {path:35s} | "
        f"prompt={prompt:>6} completion={completion:>5} total={total:>6} | {elapsed}\n"
    )
    with open(log_file, "a") as f:
        f.write(line)


async def proxy(request: Request) -> Response:
    path = request.url.path
    query = str(request.url.query)
    url = f"{UPSTREAM}{path}" + (f"?{query}" if query else "")

    body = await request.body()
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }

    start = datetime.now(timezone.utc)

    async with httpx.AsyncClient(timeout=300) as client:
        upstream_resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
        )

    elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

    # Extract and log usage if present
    content_type = upstream_resp.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = upstream_resp.json()
            usage = data.get("usage")
            if usage:
                _log_tokens(path, usage, elapsed_ms)
        except Exception:
            pass

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        headers=dict(upstream_resp.headers),
        media_type=content_type,
    )


app = Starlette(routes=[Route("/{path:path}", proxy, methods=["GET", "POST", "PUT", "DELETE"])])

if __name__ == "__main__":
    print(f"Token proxy: localhost:{LISTEN_PORT} → {UPSTREAM}")
    print(f"Logging to: {LOG_DIR}/tokens-YYYY-MM-DD.log")
    uvicorn.run(app, host="0.0.0.0", port=LISTEN_PORT, log_level="warning")
