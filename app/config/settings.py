import json
import os
from pathlib import Path

import keyring


APP_NAME = "StockEventRadar"
CONFIG_DIR = Path(os.getenv("APPDATA") or Path.home()) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "settings.json"


class AppConfig:
    """
    管理非敏感设置与 API Key。

    普通设置：
        %APPDATA%/StockEventRadar/settings.json

    API Key：
        操作系统凭据管理器（keyring）
    """

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
            # 配置文件异常不应该阻止程序启动。
            pass

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            "provider": self.provider,
            "model": self.model,
        }

        CONFIG_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
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
