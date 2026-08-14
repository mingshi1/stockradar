from app.ai.base import AIProvider
from app.ai.providers.deepseek import DeepSeekProvider
from app.ai.providers.kimi import KimiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.qwen import QwenProvider
from app.ai.providers.zhipu import ZhipuProvider


class ProviderManager:
    def __init__(self):
        providers = [
            DeepSeekProvider(),
            OpenAIProvider(),
            QwenProvider(),
            ZhipuProvider(),
            KimiProvider(),
        ]

        self._providers: dict[str, AIProvider] = {
            provider.info.name: provider
            for provider in providers
        }

    def provider_names(self) -> list[str]:
        return list(self._providers.keys())

    def research_provider_names(self) -> list[str]:
        return [
            name
            for name, provider in self._providers.items()
            if provider.info.supports_web_search
        ]

    def get(self, provider_name: str) -> AIProvider:
        try:
            return self._providers[provider_name]
        except KeyError as exc:
            raise ValueError(
                f"不支持的 AI Provider：{provider_name}"
            ) from exc

    def info(self, provider_name: str):
        return self.get(provider_name).info

    def models_for(self, provider_name: str) -> list[str]:
        return list(self.info(provider_name).models)

    def default_config(self) -> dict:
        result = {}

        for name, provider in self._providers.items():
            info = provider.info
            result[name] = {
                "enabled": name == "DeepSeek",
                "model": info.default_model,
                "base_url": info.default_base_url,
            }

        return result
