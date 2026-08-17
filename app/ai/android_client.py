from __future__ import annotations

import http.client
import json
import logging
import socket
import ssl
import time
import urllib.error
import urllib.request
from types import SimpleNamespace
from typing import Any

from app.ai.key_utils import (
    key_diagnostic,
    normalize_api_key,
)


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
    try:
        import certifi
    except Exception as exc:
        raise RuntimeError(
            "Android HTTPS 证书库未打包（certifi 缺失）。"
        ) from exc

    context = ssl.create_default_context(
        cafile=certifi.where()
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


def _decode_json_bytes(
    raw: bytes,
) -> dict:
    data = json.loads(
        raw.decode(
            "utf-8",
            errors="strict",
        )
    )

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "API 返回 JSON 顶层不是对象。"
        )

    return data


class _HttpTransport:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
    ):
        self.api_key = normalize_api_key(
            api_key
        )
        self.base_url = (
            base_url.rstrip("/")
        )
        self.timeout = float(
            timeout
        )
        self.ssl_context = (
            _build_ssl_context()
        )
        self.logger = logging.getLogger(
            "StockEventRadar"
        )

        diag = key_diagnostic(
            self.api_key
        )
        self.logger.info(
            "Android HTTP Key diagnostic: %s",
            diag.compact(),
        )

    def _request_once(
        self,
        *,
        url: str,
        body: bytes,
    ) -> bytes:
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
                # Avoid compressed/chunk-reuse edge cases in the
                # embedded Android urllib/http.client stack.
                "Accept-Encoding": (
                    "identity"
                ),
                "Connection": (
                    "close"
                ),
                "User-Agent": (
                    "StockEventRadar-Android/1.0"
                ),
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=self.timeout,
            context=self.ssl_context,
        ) as response:
            try:
                return response.read()

            except http.client.IncompleteRead as exc:
                partial = (
                    exc.partial
                    if isinstance(
                        exc.partial,
                        bytes,
                    )
                    else b""
                )

                # Some servers close after the complete JSON body but
                # before http.client receives the advertised byte count.
                # If the partial payload is already valid JSON, use it.
                if partial:
                    try:
                        _decode_json_bytes(
                            partial
                        )
                        self.logger.warning(
                            "Android HTTP recovered complete "
                            "JSON from IncompleteRead partial=%s",
                            len(partial),
                        )
                        return partial
                    except Exception:
                        pass

                raise

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

        # One retry only, and only for transport-level interruption.
        # HTTP status errors (401/402/429/etc.) are never retried here.
        max_attempts = 2

        for attempt in range(
            1,
            max_attempts + 1,
        ):
            try:
                raw = self._request_once(
                    url=url,
                    body=body,
                )
                break

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

                diag = key_diagnostic(
                    self.api_key
                )

                self.logger.warning(
                    "Android HTTP error %s "
                    "url=%s key=%s",
                    exc.code,
                    url,
                    diag.compact(),
                )

                raise RuntimeError(
                    f"HTTP {exc.code}："
                    f"{detail[:1200] or exc.reason}"
                    f"\n\nKey诊断：{diag.compact()}"
                ) from exc

            except urllib.error.URLError as exc:
                reason = exc.reason

                if isinstance(
                    reason,
                    ssl.SSLCertVerificationError,
                ):
                    raise RuntimeError(
                        "TLS 证书校验失败。"
                        "请检查代理/VPN/HTTPS 过滤，"
                        "或切换网络后重试。"
                        f"\n\n详细信息：{reason}"
                    ) from exc

                # A read timeout after several minutes is not the same as
                # an immediate connection reset. Retrying the whole model
                # inference doubles waiting time and can duplicate API
                # usage, so long read timeouts fail once with a clear
                # message. Real connection truncations still get one retry.
                if isinstance(
                    reason,
                    (
                        socket.timeout,
                        TimeoutError,
                    ),
                ):
                    raise RuntimeError(
                        "Android 等待模型响应超时。"
                        f"本次已等待约 {int(self.timeout)} 秒。"
                        "这通常表示模型生成或联网搜索时间较长，"
                        "或移动网络在长连接期间没有持续收到数据。"
                        "\n\n建议：保持应用在前台并使用稳定 Wi-Fi；"
                        "RC4.26 已显著延长 Android 长请求等待时间。"
                        f"\n\n详细信息：{reason}"
                    ) from exc

                transient = isinstance(
                    reason,
                    (
                        ConnectionResetError,
                        http.client.RemoteDisconnected,
                    ),
                )

                if (
                    transient
                    and attempt < max_attempts
                ):
                    self.logger.warning(
                        "Android transient URL error; "
                        "retrying attempt=%s/%s reason=%r",
                        attempt,
                        max_attempts,
                        reason,
                    )
                    time.sleep(
                        1.25 * attempt
                    )
                    continue

                raise RuntimeError(
                    f"网络连接失败：{reason}"
                ) from exc

            except (
                socket.timeout,
                TimeoutError,
            ) as exc:
                raise RuntimeError(
                    "Android 等待模型响应超时。"
                    f"本次已等待约 {int(self.timeout)} 秒。"
                    "这通常表示模型生成或联网搜索时间较长，"
                    "或移动网络在长连接期间没有持续收到数据。"
                    "\n\n建议：保持应用在前台并使用稳定 Wi-Fi；"
                    "RC4.26 已显著延长 Android 长请求等待时间。"
                    f"\n\n详细信息：{exc}"
                ) from exc

            except (
                http.client.IncompleteRead,
                http.client.RemoteDisconnected,
                ConnectionResetError,
            ) as exc:
                if attempt < max_attempts:
                    self.logger.warning(
                        "Android HTTP transport interrupted; "
                        "retrying attempt=%s/%s error=%r",
                        attempt,
                        max_attempts,
                        exc,
                    )
                    time.sleep(
                        1.25 * attempt
                    )
                    continue

                raise RuntimeError(
                    "Android 联网连接被中途关闭，"
                    "已自动重试 1 次仍未完成。"
                    "这通常是长请求在移动网络链路中被提前关闭。"
                    f"\n\n详细信息：{exc}"
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

        else:
            raise RuntimeError(
                "Android 网络请求没有得到响应。"
            )

        try:
            return _decode_json_bytes(
                raw
            )
        except Exception as exc:
            raise RuntimeError(
                "API 返回内容不是有效 JSON。"
            ) from exc


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
