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
    "OpenAI": {
        "enabled": False,
        "model": "gpt-5-mini",
        "base_url": "https://api.openai.com/v1",
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
}


class AppConfig:
    """
    V0.6 开始支持多 AI Provider。

    API Key 继续由 keyring 保存；
    普通配置保存在 settings.json。
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
        return json.loads(
            json.dumps(DEFAULT_PROVIDER_CONFIGS)
        )

    def load(self):
        if not CONFIG_FILE.exists():
            return

        try:
            data = json.loads(
                CONFIG_FILE.read_text(encoding="utf-8")
            )
        except Exception:
            return

        # Backward compatibility with V0.4/V0.5.
        old_provider = data.get("provider")
        old_model = data.get("model")

        self.research_provider = data.get(
            "research_provider",
            old_provider or "DeepSeek",
        )
        self.analysis_mode = data.get(
            "analysis_mode",
            "multi",
        )
        self.judge_enabled = bool(
            data.get("judge_enabled", False)
        )
        self.judge_provider = data.get(
            "judge_provider",
            self.research_provider,
        )

        saved_providers = data.get("providers", {})

        for name, defaults in self.providers.items():
            saved = saved_providers.get(name, {})

            defaults["enabled"] = bool(
                saved.get(
                    "enabled",
                    defaults["enabled"],
                )
            )
            defaults["model"] = saved.get(
                "model",
                defaults["model"],
            )
            defaults["base_url"] = saved.get(
                "base_url",
                defaults["base_url"],
            )

        if old_provider in self.providers:
            self.providers[old_provider]["enabled"] = True

            if old_model:
                self.providers[old_provider]["model"] = old_model

    def save(self):
        APP_DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "research_provider": self.research_provider,
            "analysis_mode": self.analysis_mode,
            "judge_enabled": self.judge_enabled,
            "judge_provider": self.judge_provider,
            "providers": self.providers,
        }

        CONFIG_FILE.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def get_provider_config(self, provider_name: str) -> dict:
        return dict(
            self.providers.get(
                provider_name,
                {},
            )
        )

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

    def save_api_key(
        self,
        provider: str,
        api_key: str,
    ):
        keyring.set_password(
            APP_NAME,
            f"{provider}_api_key",
            api_key,
        )

    def get_api_key(
        self,
        provider: str,
    ):
        return keyring.get_password(
            APP_NAME,
            f"{provider}_api_key",
        )

    def has_api_key(
        self,
        provider: str,
    ) -> bool:
        return bool(
            self.get_api_key(provider)
        )
