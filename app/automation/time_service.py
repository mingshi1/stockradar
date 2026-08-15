from __future__ import annotations

import locale
import subprocess
import sys
from datetime import datetime


class TimeService:
    @staticmethod
    def local_info() -> dict:
        now = datetime.now().astimezone()

        return {
            "iso": now.isoformat(timespec="seconds"),
            "display": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": str(now.tzinfo or ""),
            "utc_offset": now.strftime("%z"),
        }

    @staticmethod
    def sync_system_time() -> tuple[bool, str]:
        if sys.platform != "win32":
            return (
                False,
                "当前 RC1 的系统时间同步按钮仅支持 Windows。",
            )

        encoding = locale.getpreferredencoding(False) or "utf-8"

        try:
            completed = subprocess.run(
                ["w32tm", "/resync"],
                capture_output=True,
                timeout=30,
                check=False,
            )
        except FileNotFoundError:
            return (
                False,
                "找不到 Windows 时间工具 w32tm。",
            )
        except Exception as exc:
            return (
                False,
                f"时间同步调用失败：{exc}",
            )

        stdout = completed.stdout.decode(
            encoding,
            errors="replace",
        ).strip()
        stderr = completed.stderr.decode(
            encoding,
            errors="replace",
        ).strip()

        message = "\n".join(
            item
            for item in (stdout, stderr)
            if item
        ).strip()

        if completed.returncode == 0:
            return (
                True,
                message or "Windows 时间同步请求已完成。",
            )

        return (
            False,
            message
            or (
                "Windows 时间同步失败。请检查“自动设置时间”、"
                "Windows Time 服务或系统权限。"
            ),
        )
