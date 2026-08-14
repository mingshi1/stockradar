from app.ai.base import AIProvider, ProviderInfo


class DoubaoProvider(AIProvider):
    """
    火山方舟 / 豆包。

    Base URL 使用火山方舟 OpenAI SDK 兼容地址。
    model 输入框保持可编辑，以便用户直接使用方舟控制台给出的准确 Model ID。
    """

    info = ProviderInfo(
        name="Doubao",
        default_base_url="https://ark.cn-beijing.volces.com/api/v3",
        models=(
            "doubao-seed-2-0-lite-260215",
            "doubao-seed-evolving",
            "doubao-seed-2-1-pro",
            "doubao-seed-2-1-turbo",
        ),
        default_model="doubao-seed-2-0-lite-260215",
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

        combined_input = (
            f"{instructions}\n\n"
            f"{prompt}"
        )

        try:
            response = client.responses.create(
                model=model,
                input=combined_input,
                tools=[
                    {
                        "type": "web_search"
                    }
                ],
            )
        except Exception as exc:
            raise RuntimeError(
                f"豆包联网搜索失败：{exc}"
            ) from exc

        text = (response.output_text or "").strip()

        if not text:
            raise RuntimeError(
                "豆包联网搜索没有返回有效内容。"
            )

        return text
