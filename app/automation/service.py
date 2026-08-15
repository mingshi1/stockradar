from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from app.ai.manager import ProviderManager
from app.analysis.service import AnalysisService
from app.config.settings import APP_DATA_DIR, AppConfig
from app.database.database import Database
from app.report.exporters import export_report
from app.report.service import ReportService


class AutomationService:
    def __init__(
        self,
        *,
        config: AppConfig,
        database: Database,
        provider_manager: ProviderManager,
    ):
        self.config = config
        self.database = database
        self.provider_manager = provider_manager
        self.analysis_service = AnalysisService(
            provider_manager
        )
        self.report_service = ReportService()
        self.logger = logging.getLogger(
            "StockEventRadar"
        )

    def run_task(
        self,
        task_id: int,
        progress_callback=None,
    ) -> dict:
        task = self.database.get_scheduled_task(
            task_id
        )

        if not task:
            raise RuntimeError(
                f"找不到自动任务 #{task_id}。"
            )

        task_run_id = (
            self.database.start_task_run(
                task_id
            )
        )

        analysis_run_id = None
        report_id = None
        email_status = "disabled"
        attachment_path = None

        try:
            request = self._analysis_request(
                task
            )

            bundle = self.analysis_service.analyze(
                **request,
                progress_callback=progress_callback,
            )

            analysis_run_id = (
                self.database.save_analysis(
                    bundle
                )
            )

            run = self.database.get_analysis_run(
                analysis_run_id
            )

            if not run:
                raise RuntimeError(
                    "分析已完成，但无法重新读取历史分析。"
                )

            provider_results = (
                self.database.get_provider_results(
                    analysis_run_id
                )
            )

            artifact = self.report_service.generate(
                run=run,
                provider_results=provider_results,
                report_type=task["report_type"],
            )

            report_id = self.database.save_report(
                analysis_run_id=analysis_run_id,
                artifact=artifact,
            )

            if task["generate_pdf"]:
                attachment_path = self._export_pdf(
                    task_id=task_id,
                    artifact=artifact,
                    report_directory=str(
                        task.get(
                            "report_directory",
                            "",
                        )
                    ).strip(),
                )

            # Email delivery was intentionally removed in RC3.
            # Reports remain local and can be exported to a user-selected folder.
            final_status = "success"
            error_message = None
            email_status = "disabled"

            self.database.finish_task_run(
                task_run_id=task_run_id,
                task_id=task_id,
                status=final_status,
                analysis_run_id=analysis_run_id,
                report_id=report_id,
                email_status=email_status,
                error=error_message,
            )

            return {
                "task_id": task_id,
                "task_run_id": task_run_id,
                "status": final_status,
                "analysis_run_id": analysis_run_id,
                "report_id": report_id,
                "email_status": email_status,
                "attachment_path": attachment_path,
                "message": (
                    "自动任务完成。"
                    if final_status == "success"
                    else error_message
                ),
            }

        except Exception as exc:
            self.database.finish_task_run(
                task_run_id=task_run_id,
                task_id=task_id,
                status="failed",
                analysis_run_id=analysis_run_id,
                report_id=report_id,
                email_status=email_status,
                error=str(exc),
            )

            self.logger.exception(
                "Scheduled task failed | task_id=%s",
                task_id,
            )
            raise

    def _analysis_request(
        self,
        task: dict,
    ) -> dict:
        research_provider = (
            self.config.research_provider
        )

        provider_settings = {
            name:
            self.config.get_provider_config(
                name
            )
            for name in (
                self.provider_manager
                .provider_names()
            )
        }

        task_mode = str(
            task.get("analysis_mode", "current")
        )

        analysis_mode = (
            self.config.analysis_mode
            if task_mode == "current"
            else task_mode
        )

        if analysis_mode == "single":
            analyst_names = [
                research_provider
            ]
        else:
            analyst_names = (
                self.config
                .enabled_provider_names()
            )

            if (
                research_provider
                not in analyst_names
            ):
                analyst_names.insert(
                    0,
                    research_provider,
                )

        needed = set(analyst_names)
        needed.add(research_provider)

        if self.config.judge_enabled:
            needed.add(
                self.config.judge_provider
            )

        api_keys: dict[str, str] = {}

        for name in needed:
            key = self.config.get_api_key(
                name
            )

            if key:
                api_keys[name] = key

        if research_provider not in api_keys:
            raise RuntimeError(
                f"自动任务需要 {research_provider} API Key。"
                "请先在“AI 设置”中保存。"
            )

        return {
            "sectors": list(
                task.get("sectors", [])
            ),
            "research_provider_name": (
                research_provider
            ),
            "analysis_mode": analysis_mode,
            "judge_enabled": (
                self.config.judge_enabled
            ),
            "judge_provider_name": (
                self.config.judge_provider
            ),
            "provider_settings": (
                provider_settings
            ),
            "api_keys": api_keys,
        }

    @staticmethod
    def _safe_filename(
        value: str,
    ) -> str:
        for char in '<>:"/\\|?*':
            value = value.replace(
                char,
                "-",
            )

        return value.strip() or "report"

    def _export_pdf(
        self,
        *,
        task_id: int,
        artifact,
        report_directory: str = "",
    ) -> str:
        if report_directory:
            report_dir = Path(
                report_directory
            ).expanduser()
        else:
            report_dir = (
                APP_DATA_DIR
                / "auto_reports"
                / datetime.now().strftime(
                    "%Y-%m"
                )
            )
        report_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        stamp = datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        )

        filename = (
            f"task-{task_id}-{stamp}-"
            f"{self._safe_filename(artifact.title)}.pdf"
        )

        path = report_dir / filename

        export_report(
            artifact=artifact,
            file_format="pdf",
            file_path=str(path),
        )

        return str(path)
