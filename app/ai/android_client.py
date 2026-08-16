from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
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


def _extract_output_text(
    data: dict,
) -> str:
    direct = data.get(
        "output_text"
    )

    if (
        isinstance(direct, str)
        and direct.strip()
    ):
        return direct.strip()

    output = data.get(
        "output"
    )

    if isinstance(
        output,
        list,
    ):
        texts: list[str] = []

        for item in output:
            if not isinstance(
                item,
                dict,
            ):
                continue

            content = item.get(
                "content"
            )

            if not isinstance(
                content,
                list,
            ):
                continue

            for part in content:
                if not isinstance(
                    part,
                    dict,
                ):
                    continue

                text = part.get(
                    "text"
                )

                if (
                    isinstance(
                        text,
                        str,
                    )
                    and text.strip()
                ):
                    texts.append(
                        text.strip()
                    )

                output_text = (
                    part.get(
                        "output_text"
                    )
                )

                if (
                    isinstance(
                        output_text,
                        str,
                    )
                    and output_text.strip()
                ):
                    texts.append(
                        output_text.strip()
                    )

        if texts:
            return "\n".join(
                texts
            )

    return ""


def _build_ssl_context() -> ssl.SSLContext:
    """
    Android's embedded CPython/OpenSSL does not reliably inherit the
    Android system CA store.  Use certifi's Mozilla CA bundle explicitly.

    Certificate verification and hostname checking remain ENABLED.
    """
    try:
        import certifi
    except Exception as exc:
        raise RuntimeError(
            "Android HTTPS 证书库未打包（certifi 缺失）。"
        ) from exc

    ca_file = certifi.where()

    context = ssl.create_default_context(
        cafile=ca_file
    )

    context.check_hostname = True
    context.verify_mode = (
        ssl.CERT_REQUIRED
    )

    try:
        context.set_alpn_protocols(
            ["http/1.1"]
        )
    except Exception:
        pass

    return context


class _HttpTransport:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
    ):
        self.api_key = api_key
        self.base_url = (
            base_url.rstrip("/")
        )
        self.timeout = float(
            timeout
        )
        self.ssl_context = (
            _build_ssl_context()
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
        ).encode(
            "utf-8"
        )

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
                detail = (
                    exc.read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
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
                    "TLS 证书校验失败。"
                    "Android 已使用 Mozilla CA 证书库；"
                    "如果仍出现此错误，请检查手机是否启用了"
                    "抓包代理、VPN、HTTPS 过滤或公司/校园 Wi-Fi，"
                    "可切换到 5G/其他 Wi-Fi 后重试。"
                    f"\n\n详细信息：{reason}"
                ) from exc

            raise RuntimeError(
                f"网络连接失败：{reason}"
            ) from exc

        except ssl.SSLCertVerificationError as exc:
            raise RuntimeError(
                "TLS 证书校验失败。"
                "请检查代理/VPN/HTTPS 过滤，"
                "或切换网络后重试。"
                f"\n\n详细信息：{exc}"
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

        if not isinstance(
            data,
            dict,
        ):
            raise RuntimeError(
                "API 返回 JSON 顶层不是对象。"
            )

        return data


class _ChatCompletions:
    def __init__(
        self,
        transport: _HttpTransport,
    ):
        self.transport = (
            transport
        )

    def create(
        self,
        **kwargs,
    ):
        data = (
            self.transport.post(
                "/chat/completions",
                kwargs,
            )
        )
        return _to_namespace(
            data
        )


class _Chat:
    def __init__(
        self,
        transport: _HttpTransport,
    ):
        self.completions = (
            _ChatCompletions(
                transport
            )
        )


class _Responses:
    def __init__(
        self,
        transport: _HttpTransport,
    ):
        self.transport = (
            transport
        )

    def create(
        self,
        **kwargs,
    ):
        data = (
            self.transport.post(
                "/responses",
                kwargs,
            )
        )

        result = _to_namespace(
            data
        )

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
    Small OpenAI-compatible Android client.

    It deliberately avoids the desktop OpenAI SDK dependency tree,
    while keeping HTTPS certificate and hostname verification enabled.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float = 120.0,
    ):
        transport = (
            _HttpTransport(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
            )
        )

        self.chat = _Chat(
            transport
        )
        self.responses = (
            _Responses(
                transport
            )
        )
