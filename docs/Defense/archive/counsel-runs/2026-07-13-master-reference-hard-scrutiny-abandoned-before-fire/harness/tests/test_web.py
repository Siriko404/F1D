from pathlib import Path

import httpx
import pytest

from counsel_harness.policy import ExpertPolicy, PolicyViolation
from counsel_harness.web import RawDownloader, WebDiscovery


def test_downloads_raw_public_https_response(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=b"raw page", request=request))
    downloader = RawDownloader(
        policy,
        transport=transport,
        resolver=lambda host: ["93.184.216.34"],
    )

    path = downloader.download("https://example.com/page", "page.html")

    assert path.read_bytes() == b"raw page"


@pytest.mark.parametrize(
    ("url", "addresses"),
    [
        ("http://localhost/x", ["127.0.0.1"]),
        ("http://metadata/x", ["169.254.169.254"]),
        ("http://private/x", ["10.0.0.2"]),
        ("file:///etc/passwd", []),
    ],
)
def test_private_or_non_http_targets_are_rejected(run_config, isolated_expert, url, addresses):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    downloader = RawDownloader(policy, resolver=lambda host: addresses)

    with pytest.raises(PolicyViolation):
        downloader.download(url, "blocked.html")


def test_redirect_target_is_revalidated(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://internal/secret"}, request=request)

    addresses = {"public.example": ["93.184.216.34"], "internal": ["127.0.0.1"]}
    downloader = RawDownloader(
        policy,
        transport=httpx.MockTransport(handler),
        resolver=lambda host: addresses[host],
    )

    with pytest.raises(PolicyViolation, match="public"):
        downloader.download("https://public.example/start", "redirect.html")


def test_size_limit_and_overwrite_are_enforced(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=b"12345", request=request))
    downloader = RawDownloader(
        policy,
        max_bytes=4,
        transport=transport,
        resolver=lambda host: ["93.184.216.34"],
    )

    with pytest.raises(PolicyViolation, match="size limit"):
        downloader.download("https://example.com/large", "large.bin")
    assert not (isolated_expert.download_dir / "large.bin").exists()

    existing = isolated_expert.download_dir / "existing.html"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("keep", encoding="utf-8")
    with pytest.raises(PolicyViolation, match="already exists"):
        downloader.download("https://example.com/page", "existing.html")
    assert existing.read_text(encoding="utf-8") == "keep"


def test_web_discovery_marks_results_as_non_evidence():
    class Backend:
        def text(self, query, max_results):
            return [{"title": "Guide", "href": "https://example.com", "body": "snippet"}]

    discovery = WebDiscovery(backend_factory=lambda: Backend())

    results = discovery.search("thesis defense visualization guidance", max_results=5)

    assert results == [
        {
            "title": "Guide",
            "url": "https://example.com",
            "snippet": "snippet",
            "evidence": False,
            "instruction": "Discovery only; raw-download the source before citation.",
        }
    ]
