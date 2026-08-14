import json
import os
from pathlib import Path

import keyring


APP_NAME = "StockEventRadar"
APP_DATA_DIR = Path(os.getenv("APPDATA") or Path.home()) / APP_NAME
CONFIG_FILE = APP_DATA_DIR / "settings.json"
DATABASE_FILE = APP_DATA_DIR / "stockradar.db"


DEFAULT_PROVIDER_CONFIGS = {
    "DeepSeek": {
        "enabled": True,
        "model": "deepseek-v4-flash",
        "base_url": "https://api.deepseek.com",
    },
    "Qwen": {
        "enabled": False,
        "model": "qwen3.7-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "GLM": {
        "enabled": False,
        "model": "glm-4.7",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
    },
    "Kimi": {
        "enabled": False,
        "model": "kimi-k2.6",
        "base_url": "https://api.moonshot.cn/v1",
    },
    "Doubao": {
        "enabled": False,
        "model": "doubao-seed-2-0-lite-260215",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    },
    "MiniMax": {
        "enabled": False,
        "model": "MiniMax-M2.7",
        "base_url": "https://api.minimaxi.com/v1",
    },
}


class AppConfig:
    """
    V0.7 国产 Multi-AI 配置。

    API Key 使用 keyring 保存。
    模型、Base URL、是否启用等普通设置保存在 settings.json。
    """

    def __init__(self):
        self.research_provider = "DeepSeek"
        self.analysis_mode = "multi"
        self.judge_enabled = False
        self.judge_provider = "DeepSeek"
        self.providers = self._fresh_provider_defaults()
        self.load()

    @staticmethod
    def _fresh_provider_defaults() -> dict:
        return json.loads(json.dumps(DEFAULT_PROVIDER_CONFIGS))

    def load(self):
        if not CONFIG_FILE.exists():
            return

        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return

        self.research_provider = data.get(
            "research_provider",
            data.get("provider", "DeepSeek"),
        )
        self.analysis_mode = data.get("analysis_mode", "multi")
        self.judge_enabled = bool(data.get("judge_enabled", False))
        self.judge_provider = data.get(
            "judge_provider",
            self.research_provider,
        )

        saved_providers = data.get("providers", {})

        for name, defaults in self.providers.items():
            saved = saved_providers.get(name, {})
            defaults["enabled"] = bool(
                saved.get("enabled", defaults["enabled"])
            )
            defaults["model"] = saved.get(
                "model",
                defaults["model"],
            )
            defaults["base_url"] = saved.get(
                "base_url",
                defaults["base_url"],
            )

        # V0.6 曾经有 OpenAI。V0.7 直接忽略该配置，
        # 不删除系统凭据，避免擅自修改用户本地密钥。
        if self.research_provider not in self.providers:
            self.research_provider = "DeepSeek"

        if self.judge_provider not in self.providers:
            self.judge_provider = "DeepSeek"

    def save(self):
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            "research_provider": self.research_provider,
            "analysis_mode": self.analysis_mode,
            "judge_enabled": self.judge_enabled,
            "judge_provider": self.judge_provider,
            "providers": self.providers,
        }

        CONFIG_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_provider_config(self, provider_name: str) -> dict:
        return dict(self.providers.get(provider_name, {}))

    def update_provider_config(
        self,
        provider_name: str,
        *,
        enabled: bool,
        model: str,
        base_url: str,
    ):
        self.providers[provider_name] = {
            "enabled": bool(enabled),
            "model": model.strip(),
            "base_url": base_url.strip(),
        }

    def enabled_provider_names(self) -> list[str]:
        return [
            name
            for name, config in self.providers.items()
            if config.get("enabled")
        ]

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

    def has_api_key(self, provider: str) -> bool:
        return bool(self.get_api_key(provider))
