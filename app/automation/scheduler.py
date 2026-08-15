from __future__ import annotations

import locale
import subprocess
import sys
from pathlib import Path

from app.platform import is_windows


class WindowsTaskScheduler:
    PREFIX = "StockEventRadar_Daily_"

    @property
    def supported(self) -> bool:
        return is_windows()

    def register_daily(
        self,
        *,
        task_id: int,
        run_time: str,
    ) -> tuple[bool, str]:
        if not self.supported:
            return (
                False,
                "当前 RC1 仅在 Windows 上注册系统级每日计划任务。",
            )

        command = self._task_command(task_id)
        task_name = self.task_name(task_id)

        args = [
            "schtasks",
            "/Create",
            "/F",
            "/SC",
            "DAILY",
            "/TN",
            task_name,
            "/TR",
            command,
            "/ST",
            run_time,
        ]

        return self._run(args)

    def unregister(
        self,
        task_id: int,
    ) -> tuple[bool, str]:
        if not self.supported:
            return (True, "")

        if not self.exists(task_id):
            return (True, "系统计划任务不存在，无需删除。")

        return self._run([
            "schtasks",
            "/Delete",
            "/F",
            "/TN",
            self.task_name(task_id),
        ])

    def exists(
        self,
        task_id: int,
    ) -> bool:
        if not self.supported:
            return False

        try:
            completed = subprocess.run(
                [
                    "schtasks",
                    "/Query",
                    "/TN",
                    self.task_name(task_id),
                ],
                capture_output=True,
                timeout=15,
                check=False,
            )
        except Exception:
            return False

        return completed.returncode == 0

    @classmethod
    def task_name(
        cls,
        task_id: int,
    ) -> str:
        return f"{cls.PREFIX}{int(task_id)}"

    @staticmethod
    def _task_command(
        task_id: int,
    ) -> str:
        executable = Path(sys.executable).resolve()
        exe_name = executable.name.lower()

        # Source/dev mode:
        # python.exe main.py --run-task N
        if exe_name in {
            "python.exe",
            "pythonw.exe",
            "python",
            "python3",
        }:
            main_py = (
                Path(__file__).resolve().parents[2]
                / "main.py"
            )

            return (
                f'"{executable}" '
                f'"{main_py}" '
                f'--run-task {int(task_id)}'
            )

        # Nuitka/installed mode:
        # StockEventRadar.exe --run-task N
        return (
            f'"{executable}" '
            f'--run-task {int(task_id)}'
        )

    @staticmethod
    def _run(
        args: list[str],
    ) -> tuple[bool, str]:
        encoding = locale.getpreferredencoding(False) or "utf-8"

        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except Exception as exc:
            return (
                False,
                f"Windows Task Scheduler 调用失败：{exc}",
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

        return (
            completed.returncode == 0,
            message,
        )
