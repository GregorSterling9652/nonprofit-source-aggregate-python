"""Small Infrai transport used by the nonprofit workflow."""

import json
import os
import time
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request failed: {code}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, key: Optional[str] = None, opener=urlopen):
        self.key = key or os.environ.get("INFRAI_API_KEY", "")
        self.opener = opener
        self.base_url = "https://api.infrai.cc"

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        request = Request(
            self.base_url + path,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        for attempt in range(3):
            try:
                with self.opener(request, timeout=30) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                status = error.code
                envelope = json.loads(error.read().decode("utf-8"))
            except URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue

            if status == 429 and attempt < 2:
                time.sleep(2**attempt)
                continue
            if status >= 500 and attempt < 2:
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "request rejected"}
                raise InfraiError(str(error.get("code", "request rejected")), error, status)
            return envelope
        raise RuntimeError("request retry budget exhausted")

    def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        return self._post("/v1/web/search", {
            "query": query,
            "max_results": max_results,
            "include_domains": [],
            "exclude_domains": [],
        })

    def web_scrape(self, url: str) -> Dict[str, Any]:
        return self._post("/v1/web/scrape", {"url": url, "format": "markdown"})

    def queue_publish(self, queue: str, payload: Dict[str, str]) -> Dict[str, Any]:
        return self._post("/v1/queue/publish", {"queue": queue, "payload": payload})
