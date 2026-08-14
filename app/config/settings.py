import json
import os
from pathlib import Path

import keyring


APP_NAME = "StockEventRadar"
APP_DATA_DIR = Path(os.getenv("APPDATA") or Path.home()) / APP_NAME
CONFIG_FILE = APP_DATA_DIR / "settings.json"
DATABASE_FILE = APP_DATA_DIR / "stockradar.db"


class AppConfig:
    def __init__(self):
        self.provider = "DeepSeek"
        self.model = "deepseek-v4-flash"
        self.load()

    def load(self):
        if not CONFIG_FILE.exists():
            return

        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            self.provider = data.get("provider", "DeepSeek")
            self.model = data.get("model", "deepseek-v4-flash")
        except Exception:
            pass

    def save(self):
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(
                {
                    "provider": self.provider,
                    "model": self.model,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def save_api_key(self, provider: str, api_key: str):
        keyring.set_password(
            APP_NAME,
            f"{provider}_api_key",
            api_key,
        )

    def get_api_key(self, provider: str):
        return keyring.get_password(
            APP_NAME,
            f"{provider}_api_key",
        )
