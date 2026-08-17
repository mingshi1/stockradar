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
        # Stream server-side web search on every platform. SSE keeps the
        # connection active through long search/reasoning phases.
        research_timeout = 300.0

        client = self.build_client(
            api_key=api_key,
            base_url=base_url,
            timeout=research_timeout,
        )

        try:
            stream = client.responses.create(
                model=model,
                instructions=instructions,
                input=prompt,
                tools=[{"type": "web_search"}],
                tool_choice={"type": "web_search"},
                stream=True,
            )

            parts: list[str] = []
            done_text = ""
            usage = None
            terminal_seen = False

            for event in stream:
                event_type = str(
                    getattr(
                        event,
                        "type",
                        "",
                    )
                    or ""
                )

                if (
                    event_type
                    == "response.output_text.delta"
                ):
                    delta = getattr(
                        event,
                        "delta",
                        None,
                    )
                    if isinstance(
                        delta,
                        str,
                    ):
                        parts.append(delta)

                elif (
                    event_type
                    == "response.output_text.done"
                ):
                    text_value = getattr(
                        event,
                        "text",
                        None,
                    )
                    if isinstance(
                        text_value,
                        str,
                    ):
                        done_text = text_value

                elif (
                    event_type
                    == "response.completed"
                ):
                    terminal_seen = True
                    final_response = getattr(
                        event,
                        "response",
                        None,
                    )
                    if final_response is not None:
                        usage = getattr(
                            final_response,
                            "usage",
                            None,
                        )

                        if (
                            not parts
                            and not done_text
                        ):
                            fallback = getattr(
                                final_response,
                                "output_text",
                                None,
                            )
                            if isinstance(
                                fallback,
                                str,
                            ):
                                done_text = fallback

                elif event_type in {
                    "response.incomplete",
                    "response.failed",
                }:
                    terminal_seen = True
                    final_response = getattr(
                        event,
                        "response",
                        None,
                    )
                    error = getattr(
                        final_response,
                        "error",
                        None,
                    )
                    raise RuntimeError(
                        "DeepSeek Responses 流未正常完成"
                        + (
                            f"：{error}"
                            if error
                            else f"（{event_type}）"
                        )
                    )

            text = (
                "".join(parts).strip()
                or done_text.strip()
            )

            if not terminal_seen:
                raise RuntimeError(
                    "DeepSeek Responses 流在收到完成事件前结束。"
                )

        except Exception as exc:
            raise RuntimeError(
                f"DeepSeek 联网搜索失败：{exc}"
            ) from exc

        if not text:
            raise RuntimeError(
                "DeepSeek 联网搜索没有返回有效内容。"
            )

        return TextCallResult(
            text=text,
            usage=self._usage_from_value(
                usage
            ),
        )
