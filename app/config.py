import json
import os
from pathlib import Path

import keyring


APP_NAME = "StockEventRadar"

# Windows 下会保存到：
# C:\Users\你的用户名\AppData\Roaming\StockEventRadar
CONFIG_DIR = Path(
    os.getenv("APPDATA") or Path.home()
) / APP_NAME

CONFIG_FILE = CONFIG_DIR / "settings.json"


class AppConfig:
    def __init__(self):
        self.provider = "DeepSeek"
        self.model = "deepseek-v4-flash"

        self.load()

    def load(self):
        """读取普通配置。"""

        if not CONFIG_FILE.exists():
            return

        try:
            data = json.loads(
                CONFIG_FILE.read_text(
                    encoding="utf-8"
                )
            )

            self.provider = data.get(
                "provider",
                "DeepSeek"
            )

            self.model = data.get(
                "model",
                "deepseek-v4-flash"
            )

        except Exception:
            pass

    def save(self):
        """保存普通配置。"""

        CONFIG_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "provider": self.provider,
            "model": self.model,
        }

        CONFIG_FILE.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

    def save_api_key(self, provider, api_key):
        """安全保存 API Key。"""

        keyring.set_password(
            APP_NAME,
            f"{provider}_api_key",
            api_key
        )

    def get_api_key(self, provider):
        """读取 API Key。"""

        return keyring.get_password(
            APP_NAME,
            f"{provider}_api_key"
        )
