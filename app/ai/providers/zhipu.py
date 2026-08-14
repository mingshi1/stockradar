from app.ai.base import ChatOnlyProvider, ProviderInfo


class ZhipuProvider(ChatOnlyProvider):
    info = ProviderInfo(
        name="GLM",
        default_base_url="https://open.bigmodel.cn/api/paas/v4",
        models=(
            "glm-5.2",
            "glm-4.7",
            "glm-4.7-flash",
        ),
        default_model="glm-4.7",
        supports_web_search=False,
    )
