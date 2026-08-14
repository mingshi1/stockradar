# AI板块事件雷达 v0.8.0

V0.8 的主题是：

> 分析过程可见 + 长期数据统计

本版本不再扩张新的 AI Provider，而是把已经存在的 Multi-AI 流程做成
更适合日常使用、调试和长期观察的系统。

---

# V0.8 新增

## 1. 实时分析进度

“今日分析”页面新增：

- 总体阶段进度条
- 当前任务说明
- 联网 Research Provider 状态
- 每个独立分析模型状态
- Judge 状态
- 每个 Provider 耗时
- 每个 Provider Token
- 每个 Provider 可选成本估算

重要：

进度条代表的是软件可以真实观察到的流水线阶段，例如：

```text
准备
→ 联网研究
→ 多模型独立分析
→ Consensus
→ Judge
→ SQLite 保存
```

它不声称知道模型内部“思考到 63%”。

---

# 2. Provider 用量与性能记录

SQLite 新增：

```text
provider_calls
```

每次调用保存：

- phase
- provider
- model
- status
- duration_ms
- input_tokens
- output_tokens
- total_tokens
- estimated_cost
- error
- created_at

因此“数据统计”页面可以显示：

- Provider 累计调用次数
- 成功率
- 平均耗时
- Input Tokens
- Output Tokens
- Total Tokens
- 用户配置价格下的累计成本估算

注意：

并非所有 OpenAI-compatible Provider / 请求类型都一定返回 Token usage。

如果 API 没有返回，程序会记录 0，而不会编造数字。

---

# 3. 可配置 Token 单价

进入：

```text
AI 设置
```

每家 Provider 都新增：

```text
输入单价 / 1M input tokens
输出单价 / 1M output tokens
```

默认全部为：

```text
0
```

即：

```text
不估算成本
```

原因是模型 API 价格变化很快，本软件不会把某一天的官网价格硬编码成永久真相。

你可以按照自己实际账号的计费页面填写。

例如你决定全部使用人民币作为货币单位，那么所有 Provider 都保持人民币即可。

---

# 4. 数据统计与板块历史趋势

左侧新增：

```text
数据统计
```

包括：

### 板块事件评分趋势

SQLite 会读取过去分析结果，例如：

```text
黄金

08-10   +18
08-11   +35
08-12   +62
08-13   +55
08-14   +70
```

绘制 -100 ~ +100 的趋势图。

同时显示：

- 样本次数
- 首期评分
- 最新评分
- 评分变化
- 平均 AI 一致度

趋势图使用 PySide6 QPainter 自己绘制，没有新增 matplotlib。

### Provider 性能

表格显示：

```text
Provider
调用
成功率
平均耗时
Input Tokens
Output Tokens
Total Tokens
估算成本
```

---

# 5. 晨报 / 报告归档

V0.7 已经可以生成报告。

V0.8 新增 SQLite：

```text
saved_reports
```

当你：

```text
晨报 / 报告中心
→ 生成并归档
```

报告会同时存入数据库。

同一个：

```text
analysis_run
+
report_type
```

再次生成时会更新原归档，而不是无限产生重复记录。

支持归档：

- 30秒晨报
- 标准报告
- Multi-AI 共识报告
- 深度研究报告

并且仍支持：

- 复制摘要
- Markdown
- HTML
- PDF
- PNG 长图

---

# 6. 运行日志

V0.8 增加 Rotating Log。

日志位置：

```text
%APPDATA%\StockEventRadar\logs\app.log
```

最多保留：

```text
app.log
app.log.1
app.log.2
app.log.3
```

每份约 2 MB。

以后如果软件出现：

```text
某模型失败
数据库写入错误
报告导出失败
```

除了界面提示，也能从日志定位问题。

---

# 7. 失败隔离

Multi-AI 继续并发运行。

例如：

```text
DeepSeek  ✓
Qwen      ✓
GLM       ✕
Doubao    ✓
MiniMax   ✓
```

只要至少有一个分析模型成功，系统仍可以继续：

```text
Consensus
→ 报告
→ SQLite
```

失败模型会在任务进度和最终报告中明确标记。

AI Provider 默认网络请求仍有超时限制，因此单个请求不会无限等待。

---

# V0.8 数据库

目前包含：

```text
analysis_runs
events
analysis_events
custom_sectors
provider_results
provider_calls
saved_reports
```

旧 V0.5 / V0.6 / V0.7 数据库可以继续使用。

程序启动时：

```sql
CREATE TABLE IF NOT EXISTS ...
```

自动补上 V0.8 新表，不需要手动迁移 SQL。

---

# 安装

继续使用开发环境：

```text
D:\miniconda3\envs\stockradar-dev\python.exe
```

执行：

```powershell
python -m pip install -r requirements.txt
```

本版本没有新增第三方 Python 包。

仍然只有：

```text
PySide6
openai
keyring
```

---

# API

V0.8 不需要申请新的 API。

继续支持：

```text
DeepSeek
Qwen
GLM
Kimi
Doubao
MiniMax
```

API Key 仍然通过 Windows Credential Manager / keyring 保存。

---

# 推荐验收步骤

## A. 进度系统

1. 启用 DeepSeek + Doubao + MiniMax。
2. 只分析黄金 + 生物医药。
3. 点击开始分析。
4. 确认总进度变化。
5. 确认每个模型分别出现：
   - 进行中
   - 完成 / 失败
   - 耗时
   - Token（API 返回时）
6. 确认最后到 100%。

## B. Token / 成本

1. 不填写价格跑一次。
2. 确认 Token 可记录时正常显示。
3. 确认成本显示“—”。
4. 在某 Provider 填测试单价。
5. 再分析一次。
6. 确认出现估算成本。

## C. 数据统计

1. 进入“数据统计”。
2. 切换黄金 / 生物医药。
3. 确认趋势图可以显示历史评分。
4. 检查 Provider 成功率和平均耗时。

## D. 晨报归档

1. 打开“晨报 / 报告中心”。
2. 生成 30 秒晨报。
3. 确认自动出现在“已归档”。
4. 关闭软件。
5. 重启软件。
6. 再打开归档报告。

## E. 日志

查看：

```text
%APPDATA%\StockEventRadar\logs\app.log
```

确认启动和分析记录存在。

---

# 后续版本

## V0.9

发布工程版本：

- Windows EXE / Installer
- 首次启动向导
- 数据备份恢复
- 数据库迁移版本号
- 响应式桌面/移动布局
- Android Beta 构建路线
- GitHub Release 构建脚本

## V1.0

上线版本：

- Windows 正式版
- Android Release Candidate / 正式版
- 新手模式
- 高级模式
- 稳定性和性能打磨
- 发布说明
- 隐私 / API Key 说明
- 多设备真实测试
