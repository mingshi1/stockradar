from PySide6.QtCore import QThread, Signal

from app.ai.manager import ProviderManager
from app.analysis.service import AnalysisService


class AnalysisWorker(QThread):
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        analysis_service: AnalysisService,
        request: dict,
    ):
        super().__init__()

        self.analysis_service = (
            analysis_service
        )
        self.request = request

    def run(self):
        try:
            bundle = (
                self.analysis_service.analyze(
                    **self.request
                )
            )
            self.result_ready.emit(
                bundle
            )
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

        self.provider_manager = (
            provider_manager
        )
        self.provider_name = (
            provider_name
        )
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def run(self):
        try:
            provider = (
                self.provider_manager.get(
                    self.provider_name
                )
            )

            result = (
                provider.test_connection(
                    api_key=self.api_key,
                    model=self.model,
                    base_url=self.base_url,
                )
            )
            self.success.emit(result)

        except Exception as exc:
            self.error_occurred.emit(
                str(exc)
            )
