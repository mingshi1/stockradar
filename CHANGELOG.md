# Changelog

## 0.8.0

### Added

- 分析流水线总体进度条。
- 每个 AI Provider 实时状态。
- Research / Analysis / Judge 分阶段显示。
- 每 Provider 耗时。
- Token usage 记录。
- 用户可配置每百万 Token 输入/输出单价。
- 成本估算。
- SQLite `provider_calls` 表。
- 数据统计页面。
- 板块事件评分历史趋势图。
- Provider 调用次数统计。
- Provider 成功率统计。
- Provider 平均耗时统计。
- Provider Token 累计统计。
- Provider 成本累计统计。
- SQLite `saved_reports` 表。
- 晨报 / 报告持久归档。
- 归档报告重新打开。
- Rotating application log。

### Changed

- Multi-AI 分析服务新增 progress callback。
- AI Provider 调用结果同时返回 usage 数据。
- Dashboard 不再只有“分析中...”文字，而是显示真实流水线状态。
- 最终分析报告显示本次总耗时、Token 和可选成本估算。
- 成本价格不硬编码官方价格，由用户自行维护。

### Preserved

- DeepSeek。
- Qwen。
- GLM。
- Kimi。
- Doubao。
- MiniMax。
- Multi-AI Consensus。
- Judge。
- Event Pool。
- 自定义板块。
- 历史报告。
- PDF / PNG / Markdown / HTML。
- Keyring API Key 安全保存。

### Dependencies

无新增第三方 Python 包。
