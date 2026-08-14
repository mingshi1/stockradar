from app.ai.base import AIProvider, ProviderInfo


class OpenAIProvider(AIProvider):
    info = ProviderInfo(
        name="OpenAI",
        default_base_url="https://api.openai.com/v1",
        models=(
            "gpt-5-mini",
            "gpt-5.2",
            "gpt-5.1",
        ),
        default_model="gpt-5-mini",
        supports_web_search=True,
    )

    def _web_research(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        prompt: str,
        instructions: str,
    ) -> str:
        client = self.build_client(
            api_key=api_key,
            base_url=base_url,
        )

        try:
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=prompt,
                tools=[{"type": "web_search"}],
            )
        except Exception as exc:
            raise RuntimeError(
                f"OpenAI 联网搜索失败：{exc}"
            ) from exc

        text = (response.output_text or "").strip()

        if not text:
            raise RuntimeError(
                "OpenAI 联网搜索没有返回有效内容。"
            )

        return text
