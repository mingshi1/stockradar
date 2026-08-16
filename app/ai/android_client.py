from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request

import certifi
from types import SimpleNamespace
from typing import Any


def _to_namespace(value: Any):
    if isinstance(value, dict):
        return SimpleNamespace(
            **{
                key: _to_namespace(item)
                for key, item in value.items()
            }
        )

    if isinstance(value, list):
        return [
            _to_namespace(item)
            for item in value
        ]

    return value


def _extract_output_text(data: dict) -> str:
    direct = data.get("output_text")

    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    output = data.get("output")

    if isinstance(output, list):
        texts: list[str] = []

        for item in output:
            if not isinstance(item, dict):
                continue

            content = item.get("content")

            if not isinstance(content, list):
                continue

            for part in content:
                if not isinstance(part, dict):
                    continue

                text = part.get("text")

                if isinstance(text, str) and text.strip():
                    texts.append(text.strip())

                output_text = part.get("output_text")

                if (
                    isinstance(output_text, str)
                    and output_text.strip()
                ):
                    texts.append(
                        output_text.strip()
                    )

        if texts:
            return "\n".join(texts)

    return ""


class _HttpTransport:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)

        # Use a bundled CA bundle on Android while keeping certificate
        # verification enabled.
        self.ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )

    def post(
        self,
        path: str,
        payload: dict,
    ) -> dict:
        url = (
            f"{self.base_url}/"
            f"{path.lstrip('/')}"
        )

        body = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": (
                    "application/json"
                ),
                "Accept": (
                    "application/json"
                ),
                "User-Agent": (
                    "StockEventRadar-Android/1.0"
                ),
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
                context=self.ssl_context,
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                detail = ""

            raise RuntimeError(
                f"HTTP {exc.code}："
                f"{detail[:1200] or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            reason = exc.reason

            if isinstance(
                reason,
                ssl.SSLCertVerificationError,
            ):
                raise RuntimeError(
                    "TLS 证书校验失败。Android 已使用内置 CA 证书库"
                    "进行安全校验，但当前网络返回的证书链仍不受信任。"
                    "请关闭 HTTPS 抓包/代理/VPN，或换普通 Wi-Fi/"
                    "移动数据后重试。"
                    f" 原始错误：{reason}"
                ) from exc

            raise RuntimeError(
                f"网络连接失败：{reason}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Android 网络请求失败：{exc}"
            ) from exc

        try:
            data = json.loads(
                raw.decode(
                    "utf-8",
                    errors="strict",
                )
            )
        except Exception as exc:
            raise RuntimeError(
                "API 返回内容不是有效 JSON。"
            ) from exc

        if not isinstance(data, dict):
            raise RuntimeError(
                "API 返回 JSON 顶层不是对象。"
            )

        return data


class _ChatCompletions:
    def __init__(
        self,
        transport: _HttpTransport,
    ):
        self.transport = transport

    def create(
        self,
        **kwargs,
    ):
        data = self.transport.post(
            "/chat/completions",
            kwargs,
        )
        return _to_namespace(data)


class _Chat:
    def __init__(
        self,
        transport: _HttpTransport,
    ):
        self.completions = _ChatCompletions(
            transport
        )


class _Responses:
    def __init__(
        self,
        transport: _HttpTransport,
    ):
        self.transport = transport

    def create(
        self,
        **kwargs,
    ):
        data = self.transport.post(
            "/responses",
            kwargs,
        )

        result = _to_namespace(data)

        if not hasattr(
            result,
            "output_text",
        ):
            result.output_text = (
                _extract_output_text(
                    data
                )
            )

        return result


class AndroidOpenAICompat:
    """
    Minimal OpenAI-compatible client for Android.

    It deliberately uses only Python's standard library so the APK
    does not need the desktop openai/httpx/pydantic dependency tree.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float = 120.0,
    ):
        transport = _HttpTransport(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

        self.chat = _Chat(
            transport
        )
        self.responses = _Responses(
            transport
        )
