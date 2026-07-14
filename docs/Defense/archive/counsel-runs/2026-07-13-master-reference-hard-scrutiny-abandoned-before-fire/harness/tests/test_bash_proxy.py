import json
from pathlib import Path

import pytest

from counsel_harness.bash_proxy import BashProxy
from counsel_harness.policy import ExpertPolicy, PolicyViolation


class FakeDownloader:
    def __init__(self):
        self.calls = []

    def download(self, url: str, destination: str) -> Path:
        self.calls.append((url, destination))
        return Path(destination)


def make_proxy(run_config, isolated_expert):
    policy = ExpertPolicy(run_config.run_dir, isolated_expert)
    appended = []
    downloader = FakeDownloader()
    proxy = BashProxy(policy, downloader=downloader, append_entry=lambda entry: appended.append(entry) or "OK")
    return proxy, downloader, appended


def test_bounded_text_commands_work_on_c1_c2(run_config, isolated_expert):
    proxy, _, _ = make_proxy(run_config, isolated_expert)
    c1 = isolated_expert.sources[0].path

    assert proxy.run(f'sed -n \'1,3p\' "{c1}"').count("\n") <= 3
    assert proxy.run(f'head -n 2 "{c1}"').count("\n") <= 2
    assert proxy.run(f'tail -n 2 "{c1}"').count("\n") <= 2
    assert proxy.run(f'wc -l "{c1}"').strip().isdigit()
    assert "1:" in proxy.run(f'rg -n --fixed-strings -- "DEFENSE" "{c1}"')


@pytest.mark.parametrize(
    "command",
    [
        'cat "C:/repo/secret"',
        'find C:/ -type f',
        'echo ok; whoami',
        'echo ok | more',
        'echo $(whoami)',
        'echo $DEEPSEEK_API_KEY',
        'Get-ChildItem -Recurse',
        'python -c "import os; print(os.listdir())"',
    ],
)
def test_arbitrary_shell_syntax_and_executables_are_rejected(run_config, isolated_expert, command):
    proxy, _, _ = make_proxy(run_config, isolated_expert)
    with pytest.raises(PolicyViolation, match="unsupported command"):
        proxy.run(command)


def test_text_command_cannot_read_a_third_repo_file(run_config, isolated_expert):
    proxy, _, _ = make_proxy(run_config, isolated_expert)
    forbidden = run_config.run_dir / "subject-brief.md"
    with pytest.raises(PolicyViolation, match="not readable"):
        proxy.run(f'head -n 5 "{forbidden}"')


def test_canonical_journal_heredoc_is_parsed_without_shell_execution(run_config, isolated_expert):
    proxy, _, appended = make_proxy(run_config, isolated_expert)
    entry = {"t": "gap", "what": "not established"}
    command = (
        f'node "{run_config.run_dir / "tools" / "journal.js"}" append '
        f'"{isolated_expert.journal}" <<\'EOF\'\n{json.dumps(entry)}\nEOF'
    )

    assert proxy.run(command) == "OK"
    assert appended == [entry]


def test_raw_download_command_is_delegated_to_private_downloader(run_config, isolated_expert):
    proxy, downloader, _ = make_proxy(run_config, isolated_expert)
    destination = f"downloads/{isolated_expert.slug}/source.html"

    result = proxy.run(
        f'curl -L --fail --silent --show-error -o "{destination}" "https://example.com/source"'
    )

    assert downloader.calls == [("https://example.com/source", destination)]
    assert "source.html" in result

