from __future__ import annotations

import mimetypes
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def parse_recipients(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        raw = value
    else:
        raw = (
            str(value)
            .replace("；", ";")
            .replace("，", ",")
            .replace(";", ",")
            .split(",")
        )

    result: list[str] = []

    for item in raw:
        address = str(item).strip()

        if address and address not in result:
            result.append(address)

    return result


class EmailService:
    """
    Minimal SMTP mailer using the Python standard library.

    The password itself is supplied by SecretStore and is never written
    to settings.json.
    """

    def send_test(
        self,
        *,
        settings: dict,
        password: str | None,
        recipients: str,
    ):
        to = parse_recipients(recipients)

        if not to:
            raise ValueError("请至少填写一个测试收件邮箱。")

        message = EmailMessage()
        message["Subject"] = "AI板块事件雷达｜测试邮件"
        message["From"] = self._sender(settings)
        message["To"] = ", ".join(to)
        message.set_content(
            "这是一封来自 AI板块事件雷达 的 SMTP 测试邮件。\n\n"
            "如果你收到了它，说明邮件发送配置已经可以工作。"
        )

        self._send(
            settings=settings,
            password=password,
            message=message,
        )

    def send_report(
        self,
        *,
        settings: dict,
        password: str | None,
        recipients: str,
        subject: str,
        plain_text: str,
        html_text: str,
        attachment_path: str | None = None,
    ):
        to = parse_recipients(recipients)

        if not to:
            raise ValueError("自动任务启用了邮件，但没有有效收件人。")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._sender(settings)
        message["To"] = ", ".join(to)
        message.set_content(plain_text or "AI板块事件雷达自动报告")
        message.add_alternative(
            html_text or "<p>AI板块事件雷达自动报告</p>",
            subtype="html",
        )

        if attachment_path:
            path = Path(attachment_path)

            if path.exists():
                mime, _ = mimetypes.guess_type(path.name)
                maintype = "application"
                subtype = "octet-stream"

                if mime and "/" in mime:
                    maintype, subtype = mime.split("/", 1)

                message.add_attachment(
                    path.read_bytes(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=path.name,
                )

        self._send(
            settings=settings,
            password=password,
            message=message,
        )

    def _send(
        self,
        *,
        settings: dict,
        password: str | None,
        message: EmailMessage,
    ):
        host = str(settings.get("smtp_host", "")).strip()

        if not host:
            raise ValueError("请填写 SMTP 服务器。")

        try:
            port = int(settings.get("smtp_port", 465))
        except Exception as exc:
            raise ValueError("SMTP 端口必须是数字。") from exc

        security = str(
            settings.get("security", "ssl")
        ).strip().lower()

        username = str(
            settings.get("username", "")
        ).strip()

        timeout = 30
        context = ssl.create_default_context()

        if security == "ssl":
            client = smtplib.SMTP_SSL(
                host,
                port,
                timeout=timeout,
                context=context,
            )
        else:
            client = smtplib.SMTP(
                host,
                port,
                timeout=timeout,
            )

        try:
            client.ehlo()

            if security == "starttls":
                client.starttls(context=context)
                client.ehlo()

            if username:
                if not password:
                    raise ValueError(
                        "已经填写 SMTP 用户名，但尚未保存 SMTP 密码/授权码。"
                    )

                client.login(
                    username,
                    password,
                )

            client.send_message(message)
        finally:
            try:
                client.quit()
            except Exception:
                try:
                    client.close()
                except Exception:
                    pass

    @staticmethod
    def _sender(settings: dict) -> str:
        sender = str(
            settings.get("sender", "")
        ).strip()

        username = str(
            settings.get("username", "")
        ).strip()

        value = sender or username

        if not value:
            raise ValueError("请填写发件邮箱或 SMTP 用户名。")

        return value
