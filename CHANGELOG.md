# Changelog

## 0.4.0

### Added
- 将单文件原型拆分为模块化工程。
- 新增统一 `AIProvider` 抽象接口。
- 新增 `ProviderManager`，为后续多 AI Provider 做准备。
- DeepSeek API 实现移动到独立 Provider。
- 新增独立 `AnalysisService`。
- 新增 `AnalysisBundle` 和 `ResearchSnapshot` 数据模型。
- 新增 `NewsService`，保存本次运行的最新联网研究资料。
- “新闻源”页面可以查看本轮分析的原始研究文本。
- 新增后台 `AnalysisWorker` 和 `ConnectionWorker`。
- HTML 报告渲染与 UI 解耦。
- 设置管理移入 `app/config/settings.py`。
- 增加 requirements.txt、README、VERSION。

### Preserved
- DeepSeek API Key 安全保存。
- DeepSeek API 测试连接。
- Web Search + 结构化 JSON 分析。
- 板块评分、传导链、风险因素和来源链接。
- 当前 UI 风格与主要交互。

### Not Yet Implemented
- SQLite 历史数据库。
- Multi-AI。
- 报告文件导出。
