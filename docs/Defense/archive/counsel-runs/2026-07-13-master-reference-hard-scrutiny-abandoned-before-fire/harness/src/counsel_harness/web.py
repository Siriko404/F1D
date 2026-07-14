from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import httpx

from .policy import ExpertPolicy, PolicyViolation


def _system_resolver(host: str) -> list[str]:
    return sorted({item[4][0] for item in socket.getaddrinfo(host, None)})


class RawDownloader:
    def __init__(
        self,
        policy: ExpertPolicy,
        *,
        max_bytes: int = 20 * 1024 * 1024,
        max_redirects: int = 5,
        timeout_seconds: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        resolver: Callable[[str], list[str]] = _system_resolver,
    ):
        self.policy = policy
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects
        self.timeout_seconds = timeout_seconds
        self.transport = transport
        self.resolver = resolver

    def _validate_public_url(self, url: str) -> None:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise PolicyViolation("raw downloads require an http(s) URL")
        try:
            addresses = self.resolver(parsed.hostname)
        except OSError as exc:
            raise PolicyViolation(f"cannot resolve download host: {parsed.hostname}") from exc
        if not addresses:
            raise PolicyViolation(f"download host has no addresses: {parsed.hostname}")
        for address in addresses:
            try:
                ip = ipaddress.ip_address(address)
            except ValueError as exc:
                raise PolicyViolation(f"invalid resolved address: {address}") from exc
            if not ip.is_global:
                raise PolicyViolation(f"download target is not public: {address}")

    def download(self, url: str, destination: str) -> Path:
        target = self.policy.resolve_download(destination, require_new=True)
        current_url = url
        response: httpx.Response | None = None
        client = httpx.Client(
            transport=self.transport,
            follow_redirects=False,
            timeout=self.timeout_seconds,
            headers={"User-Agent": "DefenseCounselRawCapture/1.0"},
        )
        try:
            for redirect_count in range(self.max_redirects + 1):
                self._validate_public_url(current_url)
                response = client.get(current_url)
                if response.is_redirect:
                    if redirect_count == self.max_redirects:
                        raise PolicyViolation("raw download exceeded redirect limit")
                    location = response.headers.get("location")
                    if not location:
                        raise PolicyViolation("redirect is missing Location")
                    current_url = urljoin(current_url, location)
                    continue
                break
            assert response is not None
            response.raise_for_status()
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_bytes:
                raise PolicyViolation("raw download exceeds size limit")

            target.parent.mkdir(parents=True, exist_ok=True)
            written = 0
            try:
                with target.open("xb") as handle:
                    for chunk in response.iter_bytes():
                        written += len(chunk)
                        if written > self.max_bytes:
                            raise PolicyViolation("raw download exceeds size limit")
                        handle.write(chunk)
            except Exception:
                target.unlink(missing_ok=True)
                raise
            if written == 0:
                target.unlink(missing_ok=True)
                raise PolicyViolation("raw download is empty")
            return target
        finally:
            client.close()


class WebDiscovery:
    def __init__(self, *, backend_factory=None):
        if backend_factory is None:
            from ddgs import DDGS

            backend_factory = DDGS
        self.backend_factory = backend_factory

    def search(self, query: str, max_results: int = 8) -> list[dict[str, object]]:
        query = query.strip()
        if not query:
            raise PolicyViolation("web search query cannot be empty")
        if not 1 <= max_results <= 20:
            raise PolicyViolation("web search max_results must be between 1 and 20")
        backend = self.backend_factory()
        results = backend.text(query, max_results=max_results)
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("href") or item.get("url", ""),
                "snippet": item.get("body") or item.get("snippet", ""),
                "evidence": False,
                "instruction": "Discovery only; raw-download the source before citation.",
            }
            for item in results
        ]

