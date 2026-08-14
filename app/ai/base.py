from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    AI 服务商统一接口。

    后续接 OpenAI、Qwen、GLM 时，UI 和分析业务层不需要知道
    每家 API 的具体调用方式，只需要面对这个接口。
    """

    name: str = ""
    models: tuple[str, ...] = ()

    @abstractmethod
    def test_connection(self, api_key: str, model: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def web_research(
        self,
        api_key: str,
        model: str,
        prompt: str,
        instructions: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def json_completion(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 7000,
    ) -> dict:
        raise NotImplementedError
