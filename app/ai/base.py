from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import re

from typing import Any

from app.platform import is_android


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    name: str
    default_base_url: str
    models: tuple[str, ...]
    default_model: str
    supports_web_search: bool = False


@dataclass(slots=True)
class UsageInfo:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass(slots=True)
class TextCallResult:
    text: str
    usage: UsageInfo


@dataclass(slots=True)
class JsonCallResult:
    data: dict
    usage: UsageInfo


class AIProvider(ABC):
    info: ProviderInfo

    def build_client(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = 120.0,
    ) -> Any:
        resolved_base_url = (
            base_url
            or self.info.default_base_url
        ).rstrip("/")

        if is_android():
            from app.ai.android_client import (
                AndroidOpenAICompat,
            )

            return AndroidOpenAICompat(
                api_key=api_key,
                base_url=resolved_base_url,
                timeout=timeout,
            )

        # Desktop keeps using the official OpenAI-compatible SDK.
        # The import is intentionally lazy so Android startup does
        # not require the openai/httpx/pydantic dependency tree.
        from openai import OpenAI

        return OpenAI(
            api_key=api_key,
            base_url=resolved_base_url,
            timeout=timeout,
        )

    def test_connection(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
    ) -> str:
        client = self.build_client(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,
        )

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
                stream=False,
            )
        except Exception as exc:
            raise RuntimeError(
                f"{self.info.name} 连接失败：{exc}"
            ) from exc

        content = response.choices[0].message.content or "OK"
        return content.strip()

    def analyze_evidence(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        system_prompt: str,
        user_prompt: str,
    ) -> JsonCallResult:
        client = self.build_client(
            api_key=api_key,
            base_url=base_url,
        )

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
                stream=False,
            )
        except Exception as exc:
            raise RuntimeError(
                f"{self.info.name} 分析失败：{exc}"
            ) from exc

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                f"{self.info.name} 返回空结果。"
            )

        return JsonCallResult(
            data=self._parse_json(content),
            usage=self._extract_usage(response),
        )

    @staticmethod
    def _parse_json(content: str) -> dict:
        text = content.strip()

        fence_match = re.search(
            r"```(?:json)?\s*(\{.*\})\s*```",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if fence_match:
            text = fence_match.group(1).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            first = text.find("{")
            last = text.rfind("}")

            if first == -1 or last == -1 or last <= first:
                raise RuntimeError(
                    "模型返回内容中找不到可解析的 JSON。"
                )

            try:
                data = json.loads(text[first:last + 1])
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"模型返回 JSON 无法解析：{exc}"
                ) from exc

        if not isinstance(data, dict):
            raise RuntimeError(
                "模型返回的 JSON 顶层不是对象。"
            )

        return data

    @staticmethod
    def _extract_usage(response) -> UsageInfo:
        usage = getattr(response, "usage", None)

        if usage is None:
            return UsageInfo()

        def read(*names):
            for name in names:
                value = getattr(usage, name, None)

                if value is None and isinstance(usage, dict):
                    value = usage.get(name)

                if value is not None:
                    try:
                        return int(value)
                    except Exception:
                        pass

            return 0

        input_tokens = read(
            "input_tokens",
            "prompt_tokens",
        )
        output_tokens = read(
            "output_tokens",
            "completion_tokens",
        )
        total_tokens = read("total_tokens")

        if total_tokens <= 0:
            total_tokens = (
                input_tokens
                + output_tokens
            )

        return UsageInfo(
            input_tokens=max(0, input_tokens),
            output_tokens=max(0, output_tokens),
            total_tokens=max(0, total_tokens),
        )

    def web_research(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        prompt: str,
        instructions: str,
    ) -> TextCallResult:
        if not self.info.supports_web_search:
            raise RuntimeError(
                f"{self.info.name} 当前未配置为联网研究 Provider。"
            )

        return self._web_research(
            api_key=api_key,
            model=model,
            base_url=base_url,
            prompt=prompt,
            instructions=instructions,
        )

    @abstractmethod
    def _web_research(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        prompt: str,
        instructions: str,
    ) -> TextCallResult:
        raise NotImplementedError


class ChatOnlyProvider(AIProvider):
    def _web_research(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        prompt: str,
        instructions: str,
    ) -> TextCallResult:
        raise RuntimeError(
            f"{self.info.name} 当前只参与独立分析，不负责联网研究。"
        )
