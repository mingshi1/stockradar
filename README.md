# AI板块事件雷达 v0.5.0

V0.5 是第一个带本地 SQLite 数据库的版本。

## 新增功能

- 自定义板块临时查询
- 自定义板块长期保存
- SQLite 本地数据库
- 分析历史永久保存
- 历史报告页面
- Event Pool 基础
- 新闻事件基础去重
- 新闻事件详情页
- V0.4 的 AIProvider / DeepSeek / Web Search 架构继续保留

## 自定义板块

首页增加：

```text
自定义板块
[ 生物医药                    ] [加入本次分析]
```

可以输入：

```text
生物医药
机器人
创新药
光伏
游戏
低空经济
```

临时加入只用于当前程序会话。

如果想长期保存：

```text
板块管理 → 输入板块 → 保存板块
```

保存后即使关闭软件、重新启动，也还会存在。

## SQLite 是什么？

SQLite 是嵌入式关系型数据库。

它不需要安装 MySQL、PostgreSQL 之类的数据库服务器，
也不需要用户名、密码、端口。

Python 自带：

```python
import sqlite3
```

本软件数据库默认位于：

```text
%APPDATA%\StockEventRadar\stockradar.db
```

源码和数据库彼此分离，因此：

- Git 不会上传你的本地研究记录
- 更换项目源码不会自动删除历史
- 后续打包 EXE 时也适合每个用户保存自己的数据

## V0.5 数据表

### analysis_runs

一行 = 一次完整 AI 分析。

保存：

- 分析时间
- AI Provider
- 模型
- 板块列表
- 整体摘要
- 完整 JSON 结果
- 原始联网研究文本

### events

一行 = 一个新闻/事件。

保存：

- 标题
- 日期
- 来源
- URL
- AI 分析摘要
- fingerprint
- 首次看到时间
- 最近看到时间

### analysis_events

连接：

```text
某次分析
    ↕
某个事件
```

并记录这个事件当时关联的板块、影响方向和重要度。

### custom_sectors

保存用户自己的板块。

## 事件去重

V0.5 使用基础 fingerprint：

```text
标题 + 日期 + 来源
        ↓
SHA-256
        ↓
fingerprint
```

完全相同的事件不会重复插入 events 表。

注意：这只是 V0.5 的基础去重。

未来会升级成：

```text
不同标题但其实是同一事件
↓
语义聚类 / AI Event Merge
```

## 安装

继续使用：

```text
D:\miniconda3\envs\stockradar-dev\python.exe
```

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

本版本没有新增第三方 Python 包。

SQLite 来自 Python 标准库，不需要：

```text
pip install sqlite
```

## API

V0.5 不需要新增 API。

继续使用你之前配置好的 DeepSeek API Key：

```text
设置 → AI 服务
```

API Key 仍使用 keyring 保存。

## 推荐测试步骤

1. 启动软件。
2. 测试 DeepSeek API。
3. 首页取消大部分默认板块。
4. 输入 `生物医药` → 加入本次分析。
5. 只分析 `黄金 + 生物医药`。
6. 确认首页出现分析结果。
7. 打开“历史报告”，确认刚才的分析存在。
8. 点击该历史记录，确认报告可以恢复。
9. 打开“新闻源”，确认事件已保存。
10. 进入“板块管理”，新增 `机器人`。
11. 关闭软件。
12. 再次启动，确认 `机器人` 仍然存在。

## 下一版方向

V0.6：

- OpenAI Provider
- 多 AI Provider 设置结构
- 两模型独立分析基础
- Consensus Engine 第一版
- Token / 调用成本记录基础
