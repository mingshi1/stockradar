# AI板块事件雷达 v0.7.0

V0.7 是“国产 Multi-AI + 晨报/报告中心”版本。

## V0.7 核心变化

### AI Provider

移除：

```text
OpenAI
```

保留 / 新增：

```text
DeepSeek
Qwen
GLM
Kimi
Doubao
MiniMax
```

其中：

```text
DeepSeek
Doubao
```

可作为联网 Research Provider。

其他启用模型读取同一份证据独立分析。

---

## Multi-AI 流程

```text
Research Provider
      ↓
同一份联网证据
      ↓
┌──────────┬──────────┬──────────┐
DeepSeek   Qwen       GLM
Doubao     Kimi       MiniMax
└──────────┴──────────┴──────────┘
      ↓
Consensus Engine
      ↓
平均评分
方向一致度
评分离散度
共识置信度
      ↓
可选 Judge
```

---

# 新增：晨报 / 报告中心

左侧新增：

```text
晨报 / 报告中心
```

可以从 SQLite 中任意一条历史分析生成：

```text
30秒晨报
标准报告
Multi-AI共识报告
深度研究报告
```

## 30秒晨报

自动提取：

- 市场摘要
- 最重要板块
- 事件评分
- AI 一致度
- 5 条核心事件

晨报不额外调用 AI。

也就是说：

```text
已有 Multi-AI 分析
        ↓
本地压缩
        ↓
30秒晨报
```

没有额外 API 成本。

---

# 报告导出

V0.7 支持：

```text
复制摘要
Markdown
HTML
PDF
PNG长图
```

PDF 和 PNG 使用 PySide6 / Qt 自己生成，
因此本版本没有新增 PDF 第三方依赖。

---

# 深度研究报告

深度报告会额外保留：

```text
综合共识
+
事件分析
+
风险
+
原始联网研究资料
+
各模型原始 JSON 结果
```

它适合复核 AI 到底为什么得出某个结果。

---

# SQLite

继续沿用：

```text
%APPDATA%\StockEventRadar\stockradar.db
```

V0.5 / V0.6 历史记录和自定义板块都会继续使用。

数据库包含：

```text
analysis_runs
events
analysis_events
custom_sectors
provider_results
```

---

# 安装

仍然使用：

```text
D:\miniconda3\envs\stockradar-dev\python.exe
```

安装：

```powershell
python -m pip install -r requirements.txt
```

V0.7 没有增加新的第三方 Python 包。

---

# API

详细说明：

```text
API_SETUP.md
```

新增需要申请的主要是：

```text
Doubao / 火山方舟
MiniMax
```

你可以只申请其中一个，也可以两个都申请。

---

# 推荐测试顺序

1. 启动 V0.7。
2. 确认 OpenAI 已经从设置页消失。
3. 确认原 DeepSeek Key 仍能使用。
4. 配置豆包或 MiniMax 中任意一个。
5. 单独测试该 Provider。
6. 打开 Multi-AI，只启用 DeepSeek + 新 Provider。
7. 分析 1~2 个板块。
8. 确认共识结果正常。
9. 打开“晨报 / 报告中心”。
10. 生成“30秒晨报”。
11. 测试复制摘要。
12. 分别导出 Markdown / HTML / PDF / PNG。
13. 再生成“深度研究报告”。

---

# 下一步方向

V0.8 建议重点：

- API Token / 成本统计
- Provider 耗时统计
- 报告自动命名与归档
- 每日晨报记录
- 定时生成晨报基础
- 新闻 Event Pool 语义去重
- 历史板块趋势图
- 模型长期偏差统计
