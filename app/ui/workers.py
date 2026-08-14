from PySide6.QtCore import QThread, Signal

from app.ai.manager import ProviderManager
from app.analysis.service import AnalysisService


class AnalysisWorker(QThread):
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        analysis_service: AnalysisService,
        api_key: str,
        provider_name: str,
        model: str,
        sectors: list[str],
    ):
        super().__init__()

        self.analysis_service = analysis_service
        self.api_key = api_key
        self.provider_name = provider_name
        self.model = model
        self.sectors = sectors

    def run(self):
        try:
            bundle = self.analysis_service.analyze(
                api_key=self.api_key,
                provider_name=self.provider_name,
                model=self.model,
                sectors=self.sectors,
            )
            self.result_ready.emit(bundle)
        except Exception as exc:
            self.error_occurred.emit(str(exc))


class ConnectionWorker(QThread):
    success = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        provider_manager: ProviderManager,
        api_key: str,
        provider_name: str,
        model: str,
    ):
        super().__init__()

        self.provider_manager = provider_manager
        self.api_key = api_key
        self.provider_name = provider_name
        self.model = model

    def run(self):
        try:
            provider = self.provider_manager.get(
                self.provider_name
            )
            result = provider.test_connection(
                api_key=self.api_key,
                model=self.model,
            )
            self.success.emit(result)
        except Exception as exc:
            self.error_occurred.emit(str(exc))
