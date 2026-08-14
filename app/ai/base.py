from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import re

from openai import OpenAI


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    name: str
    default_base_url: str
    models: tuple[str, ...]
    default_model: str
    supports_web_search: bool = False


class AIProvider(ABC):
    info: ProviderInfo

    def build_client(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = 120.0,
    ) -> OpenAI:
        return OpenAI(
            api_key=api_key,
            base_url=(base_url or self.info.default_base_url).rstrip("/"),
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
    ) -> dict:
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

        return self._parse_json(content)

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

    def web_research(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        prompt: str,
        instructions: str,
    ) -> str:
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
    ) -> str:
        raise NotImplementedError


class ChatOnlyProvider(AIProvider):
    def _web_research(
        self,
        api_key: str,
        model: str,
        base_url: str | None,
        prompt: str,
        instructions: str,
    ) -> str:
        raise RuntimeError(
            f"{self.info.name} 当前只参与独立分析，不负责联网研究。"
        )
