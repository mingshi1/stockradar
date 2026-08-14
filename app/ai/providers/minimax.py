from app.ai.base import ChatOnlyProvider, ProviderInfo


class MiniMaxProvider(ChatOnlyProvider):
    """
    MiniMax 中国开放平台 OpenAI-compatible API。
    """

    info = ProviderInfo(
        name="MiniMax",
        default_base_url="https://api.minimaxi.com/v1",
        models=(
            "MiniMax-M2.7",
            "MiniMax-M2.7-highspeed",
            "MiniMax-M2.5",
            "MiniMax-M2.5-highspeed",
            "MiniMax-M2.1",
        ),
        default_model="MiniMax-M2.7",
        supports_web_search=False,
    )
