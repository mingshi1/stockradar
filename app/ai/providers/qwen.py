from app.ai.base import ChatOnlyProvider, ProviderInfo


class QwenProvider(ChatOnlyProvider):
    info = ProviderInfo(
        name="Qwen",
        default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        models=(
            "qwen3.7-plus",
            "qwen3.7-max",
            "qwen3.6-flash",
            "qwen-plus",
        ),
        default_model="qwen3.7-plus",
        supports_web_search=False,
    )
