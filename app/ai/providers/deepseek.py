import json

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from app.ai.base import AIProvider


class DeepSeekProvider(AIProvider):
    name = "DeepSeek"
    models = (
        "deepseek-v4-flash",
        "deepseek-v4-pro",
    )

    BASE_URL = "https://api.deepseek.com"

    def _client(self, api_key: str, timeout: float = 120.0) -> OpenAI:
        return OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
            timeout=timeout,
        )

    def test_connection(self, api_key: str, model: str) -> str:
        client = self._client(api_key, timeout=20.0)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是 API 连接测试助手。",
                    },
                    {
                        "role": "user",
                        "content": "只回复 OK",
                    },
                ],
                max_tokens=16,
                stream=False,
                extra_body={
                    "thinking": {
                        "type": "disabled"
                    }
                },
            )

            content = response.choices[0].message.content
            return (content or "OK").strip()

        except AuthenticationError as exc:
            raise RuntimeError(
                "API Key 无效，请检查是否复制完整。"
            ) from exc
        except APIConnectionError as exc:
            raise RuntimeError(
                "无法连接 DeepSeek，请检查网络连接。"
            ) from exc
        except RateLimitError as exc:
            raise RuntimeError(
                "API 请求过于频繁，请稍后再试。"
            ) from exc
        except APIStatusError as exc:
            raise RuntimeError(
                f"DeepSeek API 返回错误：HTTP {exc.status_code}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"连接失败：{exc}"
            ) from exc

    def web_research(
        self,
        api_key: str,
        model: str,
        prompt: str,
        instructions: str,
    ) -> str:
        client = self._client(api_key)

        try:
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=prompt,
                tools=[
                    {
                        "type": "web_search"
                    }
                ],
                tool_choice={
                    "type": "web_search"
                },
            )
        except Exception as exc:
            raise RuntimeError(
                f"联网搜索失败：{exc}"
            ) from exc

        text = (response.output_text or "").strip()

        if not text:
            raise RuntimeError(
                "DeepSeek 联网搜索没有返回有效内容。"
            )

        return text

    def json_completion(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 7000,
    ) -> dict:
        client = self._client(api_key)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                response_format={
                    "type": "json_object"
                },
                max_tokens=max_tokens,
                stream=False,
                extra_body={
                    "thinking": {
                        "type": "disabled"
                    }
                },
            )
        except Exception as exc:
            raise RuntimeError(
                f"结构化分析失败：{exc}"
            ) from exc

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "AI 返回了空的结构化分析结果。"
            )

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "AI 返回的 JSON 无法解析。"
            ) from exc
