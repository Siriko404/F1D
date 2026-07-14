from pathlib import Path

import pytest

from counsel_harness.secrets import SecretValue, load_deepseek_key


def test_decrypted_key_is_non_printing(tmp_path: Path):
    encrypted = tmp_path / "key.dpapi"
    encrypted.write_bytes(b"ciphertext")
    secret = load_deepseek_key(encrypted, decryptor=lambda data: b"sk-test-secret")

    assert isinstance(secret, SecretValue)
    assert secret.get_secret_value() == "sk-test-secret"
    assert "sk-test-secret" not in str(secret)
    assert "sk-test-secret" not in repr(secret)


def test_invalid_or_missing_key_is_rejected(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_deepseek_key(tmp_path / "missing.dpapi", decryptor=lambda data: b"sk-unused")

    encrypted = tmp_path / "key.dpapi"
    encrypted.write_bytes(b"ciphertext")
    with pytest.raises(ValueError, match="DeepSeek key"):
        load_deepseek_key(encrypted, decryptor=lambda data: b"not-a-key")
