from __future__ import annotations

from app.platform import is_android


class SecretStore:
    """
    Desktop:
        use keyring / OS credential manager.

    Android Beta:
        keep API keys only in memory for the current app session.
        This avoids writing plaintext secrets to app files while we prepare
        a native Android Keystore integration for a later release.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._memory: dict[str, str] = {}

        self._keyring = None

        if not is_android():
            try:
                import keyring  # type: ignore
                self._keyring = keyring
            except Exception:
                self._keyring = None

    @property
    def persistent(self) -> bool:
        return self._keyring is not None

    def set(self, key: str, value: str):
        value = value.strip()

        if not value:
            return

        if self._keyring is not None:
            self._keyring.set_password(
                self.service_name,
                key,
                value,
            )
        else:
            self._memory[key] = value

    def get(self, key: str) -> str | None:
        if self._keyring is not None:
            return self._keyring.get_password(
                self.service_name,
                key,
            )

        return self._memory.get(key)
