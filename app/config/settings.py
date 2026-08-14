import json
import os
from pathlib import Path

import keyring


APP_NAME = "StockEventRadar"
APP_DATA_DIR = Path(os.getenv("APPDATA") or Path.home()) / APP_NAME
CONFIG_FILE = APP_DATA_DIR / "settings.json"
DATABASE_FILE = APP_DATA_DIR / "stockradar.db"


def _provider(
    *,
    enabled: bool,
    model: str,
    base_url: str,
) -> dict:
    return {
        "enabled": enabled,
        "model": model,
        "base_url": base_url,
        # 用户自行维护的“每百万 Token 单价”。
        # 默认 0 表示未配置，因此不会伪造成本。
        "input_price_per_million": 0.0,
        "output_price_per_million": 0.0,
    }


DEFAULT_PROVIDER_CONFIGS = {
    "DeepSeek": _provider(
        enabled=True,
        model="deepseek-v4-flash",
        base_url="https://api.deepseek.com",
    ),
    "Qwen": _provider(
        enabled=False,
        model="qwen3.7-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
    "GLM": _provider(
        enabled=False,
        model="glm-4.7",
        base_url="https://open.bigmodel.cn/api/paas/v4",
    ),
    "Kimi": _provider(
        enabled=False,
        model="kimi-k2.6",
        base_url="https://api.moonshot.cn/v1",
    ),
    "Doubao": _provider(
        enabled=False,
        model="doubao-seed-2-0-lite-260215",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    ),
    "MiniMax": _provider(
        enabled=False,
        model="MiniMax-M2.7",
        base_url="https://api.minimaxi.com/v1",
    ),
}


class AppConfig:
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

            for key in (
                "enabled",
                "model",
                "base_url",
                "input_price_per_million",
                "output_price_per_million",
            ):
                if key in saved:
                    defaults[key] = saved[key]

            defaults["enabled"] = bool(defaults["enabled"])

            for price_key in (
                "input_price_per_million",
                "output_price_per_million",
            ):
                try:
                    defaults[price_key] = max(
                        0.0,
                        float(defaults[price_key]),
                    )
                except Exception:
                    defaults[price_key] = 0.0

        if self.research_provider not in self.providers:
            self.research_provider = "DeepSeek"

        if self.judge_provider not in self.providers:
            self.judge_provider = "DeepSeek"

    def save(self):
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

        CONFIG_FILE.write_text(
            json.dumps(
                {
                    "research_provider": self.research_provider,
                    "analysis_mode": self.analysis_mode,
                    "judge_enabled": self.judge_enabled,
                    "judge_provider": self.judge_provider,
                    "providers": self.providers,
                },
                ensure_ascii=False,
                indent=2,
            ),
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
        input_price_per_million: float = 0.0,
        output_price_per_million: float = 0.0,
    ):
        self.providers[provider_name] = {
            "enabled": bool(enabled),
            "model": model.strip(),
            "base_url": base_url.strip(),
            "input_price_per_million": max(
                0.0,
                float(input_price_per_million or 0.0),
            ),
            "output_price_per_million": max(
                0.0,
                float(output_price_per_million or 0.0),
            ),
        }

    def enabled_provider_names(self) -> list[str]:
        return [
            name
            for name, config in self.providers.items()
            if config.get("enabled")
        ]

    def estimate_cost(
        self,
        provider_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float | None:
        config = self.get_provider_config(provider_name)

        input_price = float(
            config.get("input_price_per_million", 0.0) or 0.0
        )
        output_price = float(
            config.get("output_price_per_million", 0.0) or 0.0
        )

        if input_price <= 0 and output_price <= 0:
            return None

        return (
            max(0, int(input_tokens)) / 1_000_000 * input_price
            + max(0, int(output_tokens)) / 1_000_000 * output_price
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

    def has_api_key(self, provider: str) -> bool:
        return bool(self.get_api_key(provider))
