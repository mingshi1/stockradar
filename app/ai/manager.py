from app.ai.base import AIProvider
from app.ai.providers.deepseek import DeepSeekProvider


class ProviderManager:
    """
    AI Provider 注册中心。

    v0.4 只有 DeepSeek。
    后续新增 Provider 时，只需要在这里注册。
    """

    def __init__(self):
        providers = [
            DeepSeekProvider(),
        ]

        self._providers: dict[str, AIProvider] = {
            provider.name: provider
            for provider in providers
        }

    def provider_names(self) -> list[str]:
        return list(self._providers.keys())

    def get(self, provider_name: str) -> AIProvider:
        try:
            return self._providers[provider_name]
        except KeyError as exc:
            raise ValueError(
                f"不支持的 AI Provider：{provider_name}"
            ) from exc

    def models_for(self, provider_name: str) -> list[str]:
        return list(self.get(provider_name).models)
