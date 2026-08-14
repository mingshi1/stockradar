from app.ai.base import ChatOnlyProvider, ProviderInfo


class KimiProvider(ChatOnlyProvider):
    info = ProviderInfo(
        name="Kimi",
        default_base_url="https://api.moonshot.cn/v1",
        models=(
            "kimi-k3",
            "kimi-k2.6",
            "kimi-k2.5",
        ),
        default_model="kimi-k2.6",
        supports_web_search=False,
    )
