import logging

from PySide6.QtCore import QThread, Signal

from app.ai.manager import ProviderManager
from app.ai.key_utils import key_diagnostic, normalize_api_key
from app.analysis.service import AnalysisService


class AnalysisWorker(QThread):
    result_ready = Signal(object)
    error_occurred = Signal(str)
    progress_changed = Signal(object)

    def __init__(
        self,
        analysis_service: AnalysisService,
        request: dict,
    ):
        super().__init__()

        self.analysis_service = analysis_service
        self.request = request

    def run(self):
        try:
            request = dict(self.request)
            request["progress_callback"] = (
                self.progress_changed.emit
            )

            bundle = self.analysis_service.analyze(
                **request
            )
            self.result_ready.emit(bundle)

        except Exception as exc:
            self.error_occurred.emit(
                str(exc)
            )


class ConnectionWorker(QThread):
    success = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        provider_manager: ProviderManager,
        provider_name: str,
        api_key: str,
        model: str,
        base_url: str,
    ):
        super().__init__()

        self.provider_manager = provider_manager
        self.provider_name = provider_name
        self.api_key = normalize_api_key(
            api_key
        )
        self.model = model
        self.base_url = base_url

    def run(self):
        try:
            diag = key_diagnostic(
                self.api_key
            )
            logging.getLogger(
                "StockEventRadar"
            ).info(
                "ConnectionWorker Key diagnostic "
                "provider=%s %s",
                self.provider_name,
                diag.compact(),
            )

            provider = self.provider_manager.get(
                self.provider_name
            )

            result = provider.test_connection(
                api_key=self.api_key,
                model=self.model,
                base_url=self.base_url,
            )
            self.success.emit(result)

        except Exception as exc:
            diag = key_diagnostic(
                self.api_key
            )
            self.error_occurred.emit(
                f"{exc}"
                f"\n\nWorker Key诊断："
                f"{diag.compact()}"
            )


class AutomationWorker(QThread):
    result_ready = Signal(object)
    error_occurred = Signal(str)
    progress_changed = Signal(object)

    def __init__(
        self,
        automation_service,
        task_id: int,
    ):
        super().__init__()
        self.automation_service = automation_service
        self.task_id = int(task_id)

    def run(self):
        try:
            result = self.automation_service.run_task(
                self.task_id,
                progress_callback=(
                    self.progress_changed.emit
                ),
            )
            self.result_ready.emit(result)
        except Exception as exc:
            self.error_occurred.emit(str(exc))


class TimeSyncWorker(QThread):
    result_ready = Signal(bool, str)

    def run(self):
        from app.automation.time_service import TimeService

        success, message = (
            TimeService.sync_system_time()
        )
        self.result_ready.emit(
            success,
            message,
        )
