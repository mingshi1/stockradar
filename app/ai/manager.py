from app.ai.base import AIProvider
from app.ai.providers.deepseek import DeepSeekProvider
from app.ai.providers.doubao import DoubaoProvider
from app.ai.providers.kimi import KimiProvider
from app.ai.providers.minimax import MiniMaxProvider
from app.ai.providers.qwen import QwenProvider
from app.ai.providers.zhipu import ZhipuProvider


class ProviderManager:
    """
    当前版本 国产优先 Provider 注册中心。

    已移除 OpenAI。
    """

    def __init__(self):
        providers = [
            DeepSeekProvider(),
            QwenProvider(),
            ZhipuProvider(),
            KimiProvider(),
            DoubaoProvider(),
            MiniMaxProvider(),
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
