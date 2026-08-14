# Changelog

## 0.5.0

### Added
- 自定义板块临时分析。
- 自定义板块持久保存。
- SQLite 本地数据库。
- `analysis_runs` 历史分析表。
- `events` 事件池表。
- `analysis_events` 分析-事件关联表。
- `custom_sectors` 自定义板块表。
- SHA-256 事件基础 fingerprint。
- 历史报告查看页面。
- SQLite Event Pool 新闻页面。

### Changed
- 每次成功分析会自动保存。
- “板块管理”页面由占位页变成可用页面。
- “历史报告”页面由占位页变成可用页面。
- “新闻源”页面从临时研究文本升级为数据库事件池。
- 分析 Prompt 支持用户自行输入的主题板块。

### API / Dependencies
- 无新增 API。
- 无新增第三方 Python 包。
- SQLite 使用 Python 标准库 `sqlite3`。
