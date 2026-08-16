import json
import os
from pathlib import Path

from app.secrets import SecretStore


APP_NAME = "StockEventRadar"


def _app_data_dir() -> Path:
    from app.platform import is_android

    if is_android():
        try:
            from PySide6.QtCore import QStandardPaths

            location = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation
            )

            if location:
                return Path(location)
        except Exception:
            pass

    return (
        Path(
            os.getenv("APPDATA")
            or Path.home()
        )
        / APP_NAME
    )


APP_DATA_DIR = _app_data_dir()
CONFIG_FILE = APP_DATA_DIR / "settings.json"
DATABASE_FILE = APP_DATA_DIR / "stockradar.db"

_SECRET_STORE = SecretStore(APP_NAME)


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

        self.onboarding_complete = False
        self.ui_mode = "auto"

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
                CONFIG_FILE.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            return

        self.research_provider = data.get(
            "research_provider",
            data.get(
                "provider",
                "DeepSeek",
            ),
        )
        self.analysis_mode = data.get(
            "analysis_mode",
            "multi",
        )
        self.judge_enabled = bool(
            data.get(
                "judge_enabled",
                False,
            )
        )
        self.judge_provider = data.get(
            "judge_provider",
            self.research_provider,
        )

        self.onboarding_complete = bool(
            data.get(
                "onboarding_complete",
                False,
            )
        )
        self.ui_mode = str(
            data.get(
                "ui_mode",
                "auto",
            )
        )

        saved_providers = data.get(
            "providers",
            {},
        )

        for name, defaults in self.providers.items():
            saved = saved_providers.get(
                name,
                {},
            )

            for key in (
                "enabled",
                "model",
                "base_url",
                "input_price_per_million",
                "output_price_per_million",
            ):
                if key in saved:
                    defaults[key] = saved[key]

            defaults["enabled"] = bool(
                defaults["enabled"]
            )

            for price_key in (
                "input_price_per_million",
                "output_price_per_million",
            ):
                try:
                    defaults[price_key] = max(
                        0.0,
                        float(
                            defaults[
                                price_key
                            ]
                        ),
                    )
                except Exception:
                    defaults[
                        price_key
                    ] = 0.0

        if (
            self.research_provider
            not in self.providers
        ):
            self.research_provider = (
                "DeepSeek"
            )

        if (
            self.judge_provider
            not in self.providers
        ):
            self.judge_provider = (
                "DeepSeek"
            )

    def save(self):
        APP_DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        CONFIG_FILE.write_text(
            json.dumps(
                {
                    "research_provider": (
                        self.research_provider
                    ),
                    "analysis_mode": (
                        self.analysis_mode
                    ),
                    "judge_enabled": (
                        self.judge_enabled
                    ),
                    "judge_provider": (
                        self.judge_provider
                    ),
                    "onboarding_complete": (
                        self.onboarding_complete
                    ),
                    "ui_mode": self.ui_mode,
                    "providers": (
                        self.providers
                    ),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def get_provider_config(
        self,
        provider_name: str,
    ) -> dict:
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
        input_price_per_million: float = 0.0,
        output_price_per_million: float = 0.0,
    ):
        self.providers[
            provider_name
        ] = {
            "enabled": bool(enabled),
            "model": model.strip(),
            "base_url": base_url.strip(),
            "input_price_per_million": max(
                0.0,
                float(
                    input_price_per_million
                    or 0.0
                ),
            ),
            "output_price_per_million": max(
                0.0,
                float(
                    output_price_per_million
                    or 0.0
                ),
            ),
        }

    def enabled_provider_names(
        self,
    ) -> list[str]:
        return [
            name
            for name, config
            in self.providers.items()
            if config.get("enabled")
        ]

    def estimate_cost(
        self,
        provider_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float | None:
        config = (
            self.get_provider_config(
                provider_name
            )
        )

        input_price = float(
            config.get(
                "input_price_per_million",
                0.0,
            )
            or 0.0
        )
        output_price = float(
            config.get(
                "output_price_per_million",
                0.0,
            )
            or 0.0
        )

        if (
            input_price <= 0
            and output_price <= 0
        ):
            return None

        if (
            input_tokens <= 0
            and output_tokens <= 0
        ):
            return None

        return (
            max(
                0,
                int(input_tokens),
            )
            / 1_000_000
            * input_price
            + max(
                0,
                int(output_tokens),
            )
            / 1_000_000
            * output_price
        )

    def save_api_key(
        self,
        provider: str,
        api_key: str,
    ):
        _SECRET_STORE.set(
            f"{provider}_api_key",
            api_key,
        )

    def get_api_key(
        self,
        provider: str,
    ):
        return _SECRET_STORE.get(
            f"{provider}_api_key"
        )

    def has_api_key(
        self,
        provider: str,
    ) -> bool:
        return bool(
            self.get_api_key(provider)
        )

    def secret_store_is_persistent(
        self,
    ) -> bool:
        return _SECRET_STORE.persistent
