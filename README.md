# AI板块事件雷达 v0.4.0

这是从可运行原型 v0.3 重构出来的第一版工程化结构。

## v0.4 的目标

本版本**不追求一次加入很多新功能**，而是把已经跑通的核心能力拆成可以长期维护的模块：

- PySide6 桌面 UI
- DeepSeek API Key 安全保存
- DeepSeek API 测试
- DeepSeek Web Search 研究
- 结构化 JSON 板块分析
- 后台线程，避免 UI 在 API 请求时卡死
- HTML 分析报告显示
- 原始联网研究资料显示在“新闻源”页
- 为未来 OpenAI / Qwen / GLM / Multi-AI 预留 Provider 接口

## 项目结构

```text
stockradar-v0.4.0/
├── main.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── VERSION
└── app/
    ├── config/
    │   └── settings.py
    ├── ai/
    │   ├── base.py
    │   ├── manager.py
    │   └── providers/
    │       └── deepseek.py
    ├── analysis/
    │   ├── models.py
    │   └── service.py
    ├── news/
    │   ├── models.py
    │   └── service.py
    ├── report/
    │   └── html_renderer.py
    └── ui/
        ├── main_window.py
        ├── workers.py
        ├── styles.py
        └── pages/
            ├── dashboard_page.py
            ├── history_page.py
            ├── news_page.py
            ├── sector_page.py
            └── settings_page.py
```

## 安装依赖

请确保 VS Code 使用你的正式开发解释器，例如：

```text
D:\miniconda3\envs\stockradar-dev\python.exe
```

然后在项目目录执行：

```powershell
python -m pip install -r requirements.txt
```

如果你之前已经安装过依赖，也建议执行一次，pip 会自动跳过已经满足的版本。

## 运行

```powershell
python main.py
```

## API Key

进入软件：

```text
设置 → AI 服务 → API Key
```

填入你自己的 DeepSeek API Key，然后：

1. 保存设置
2. 测试连接
3. 回到“今日分析”
4. 先选择 1~2 个板块测试

API Key 使用 `keyring` 保存到操作系统凭据管理器，不写入项目源码。

v0.3 使用过同一个 `StockEventRadar` keyring 服务名时，原来的 DeepSeek API Key 可以直接复用。

## v0.4 当前边界

暂时没有实现：

- SQLite 历史数据库
- OpenAI / Qwen / GLM
- Multi-AI Consensus
- PDF / PNG 导出
- 新闻逐条结构化 Event Pool
- 自动晨报
- EXE 安装包

这些将在后续版本逐步加入。

## 下一版本

v0.5 计划重点：

- SQLite
- Event Pool
- 历史分析记录
- 新闻事件去重基础
- 历史报告页真正可用
