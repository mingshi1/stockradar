from app.ai.base import (
    AIProvider,
    ProviderInfo,
    TextCallResult,
)


class DeepSeekProvider(AIProvider):
    info = ProviderInfo(
        name="DeepSeek",
        default_base_url="https://api.deepseek.com",
        models=(
            "deepseek-v4-flash",
            "deepseek-v4-pro",
        ),
        default_model="deepseek-v4-flash",
        supports_web_search=True,
    )

    def _web_research(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        prompt: str,
        instructions: str,
    ) -> TextCallResult:
        client = self.build_client(
            api_key=api_key,
            base_url=base_url,
            timeout=180.0,
        )

        try:
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=prompt,
                tools=[{"type": "web_search"}],
                tool_choice={"type": "web_search"},
            )
        except Exception as exc:
            raise RuntimeError(
                f"DeepSeek 联网搜索失败：{exc}"
            ) from exc

        text = (response.output_text or "").strip()

        if not text:
            raise RuntimeError(
                "DeepSeek 联网搜索没有返回有效内容。"
            )

        return TextCallResult(
            text=text,
            usage=self._extract_usage(response),
        )
