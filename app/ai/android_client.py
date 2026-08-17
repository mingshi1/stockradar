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

    def _stream_request_once(
        self,
        *,
        url: str,
        body: bytes,
    ):
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
                    "text/event-stream"
                ),
                "Cache-Control": (
                    "no-cache"
                ),
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
            yield from self._iter_sse_response(
                response
            )

    def _iter_sse_response(
        self,
        response,
    ):
        """
        Parse one SSE HTTP response.

        Some servers close immediately after the final SSE record without
        appending an extra blank line. The buffered final record must be
        dispatched before deciding that EOF was premature.
        """
        event_name = ""
        data_lines: list[str] = []
        terminal_seen = False
        event_count = 0
        last_event_type = ""

        def dispatch_buffered():
            nonlocal event_name
            nonlocal data_lines
            nonlocal terminal_seen
            nonlocal event_count
            nonlocal last_event_type

            if not data_lines:
                event_name = ""
                return None

            data = "\n".join(
                data_lines
            )
            data_lines = []

            if data.strip() == "[DONE]":
                terminal_seen = True
                event_name = ""
                return "__DONE__"

            item = self._decode_sse_item(
                data,
                event_name,
            )
            event_name = ""

            if item is None:
                return None

            item_type = str(
                item.get("type")
                or item.get("event")
                or ""
            )
            event_count += 1

            if item_type:
                last_event_type = item_type

            if item_type in {
                "response.completed",
                "response.incomplete",
                "response.failed",
            }:
                terminal_seen = True

            return item

        while True:
            raw_line = response.readline()

            if not raw_line:
                # RC4.27 bug: the buffered final record was yielded, but its
                # terminal type was not applied before the EOF check.
                item = dispatch_buffered()

                if (
                    item is not None
                    and item != "__DONE__"
                ):
                    yield item

                if terminal_seen:
                    return

                raise RuntimeError(
                    "Android SSE 流在完成标记前被关闭。"
                    f"已收到 {event_count} 个事件；"
                    f"最后事件：{last_event_type or '无'}。"
                )

            line = raw_line.decode(
                "utf-8",
                errors="replace",
            ).rstrip(
                "\r\n"
            )

            if line.startswith(":"):
                # DeepSeek SSE keep-alive comment.
                continue

            if line.startswith("event:"):
                event_name = (
                    line[6:].strip()
                )
                continue

            if line.startswith("data:"):
                data_lines.append(
                    line[5:].lstrip()
                )
                continue

            if line:
                # Tolerate OpenAI-compatible servers emitting raw JSON lines.
                data_lines.append(line)
                continue

            item = dispatch_buffered()

            if item == "__DONE__":
                return

            if item is not None:
                yield item

            if terminal_seen:
                return

    @staticmethod
    def _decode_sse_item(
        data: str,
        event_name: str,
    ) -> dict | None:
        text = data.strip()

        if not text:
            return None

        try:
            item = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Android SSE 收到无法解析的 JSON 事件。"
                f"\n\n片段：{text[:500]}"
            ) from exc

        if not isinstance(
            item,
            dict,
        ):
            raise RuntimeError(
                "Android SSE 事件 JSON 顶层不是对象。"
            )

        if (
            event_name
            and not item.get("type")
        ):
            item["type"] = event_name

        if (
            not item.get("type")
            and isinstance(
                item.get("event"),
                str,
            )
        ):
            item["type"] = item["event"]

        return item

    def stream(
        self,
        path: str,
        payload: dict,
    ):
        url = (
            f"{self.base_url}/"
            f"{path.lstrip('/')}"
        )

        stream_payload = dict(
            payload
        )
        stream_payload["stream"] = True

        body = json.dumps(
            stream_payload,
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        try:
            yield from self._stream_request_once(
                url=url,
                body=body,
            )

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

            raise RuntimeError(
                "Android SSE 网络连接失败。"
                "流式请求不会自动整单重试，"
                "以避免重复执行长推理/API 消耗。"
                f"\n\n详细信息：{reason}"
            ) from exc

        except (
            socket.timeout,
            TimeoutError,
        ) as exc:
            raise RuntimeError(
                "Android SSE 等待后续数据超时。"
                f"连续约 {int(self.timeout)} 秒未收到网络数据。"
                "如果服务端正常发送 token 或 keep-alive，"
                "长任务本身可以超过这个时长。"
                f"\n\n详细信息：{exc}"
            ) from exc

        except (
            http.client.IncompleteRead,
            http.client.RemoteDisconnected,
            ConnectionResetError,
        ) as exc:
            raise RuntimeError(
                "Android SSE 连接在完成事件前被关闭。"
                "本次不会自动从头重跑，避免重复调用。"
                f"\n\n详细信息：{exc}"
            ) from exc

        except ssl.SSLCertVerificationError as exc:
            raise RuntimeError(
                "TLS 证书校验失败。"
                "请检查代理/VPN/HTTPS 过滤，"
                "或切换网络后重试。"
                f"\n\n详细信息：{exc}"
            ) from exc

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
        if kwargs.get(
            "stream"
        ):
            return (
                _to_namespace(item)
                for item in self.transport.stream(
                    "/chat/completions",
                    kwargs,
                )
            )

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
        if kwargs.get(
            "stream"
        ):
            return (
                _to_namespace(item)
                for item in self.transport.stream(
                    "/responses",
                    kwargs,
                )
            )

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
