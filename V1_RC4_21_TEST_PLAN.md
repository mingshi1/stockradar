# V1.0.0 RC4.21 Android 测试

## 1. 手指滚动

逐页打开：
- 今日分析
- 历史报告
- 板块管理
- 新闻源
- 数据统计
- 晨报 / 报告中心
- 自动任务
- AI 设置
- 系统与数据

直接在页面空白区域、表格、报告预览中上下拖动。

预期：
- 页面可跟随手指滚动
- QTextBrowser 可直接手指滚动
- QTableWidget 可直接手指滚动
- 不需要再抓右侧滚动条

## 2. 今日分析

选择 1~2 个板块，点击开始分析。

Android 进度表只显示：

```text
任务 | 模型 | 状态 | 耗时
```

不再显示 Token / 成本列。

### DeepSeek 联网研究

如果底层遇到：

```text
IncompleteRead
RemoteDisconnected
ConnectionResetError
timeout
```

Android 会自动重试 1 次。

若第二次仍失败，错误应显示：

```text
Android 联网响应被中途截断，
已自动重试 1 次仍未完成。
```

不应再只暴露裸 `IncompleteRead(1 bytes read)`。

## 3. 报告中心

手机端应纵向显示：

```text
分析记录
[ 下拉框 ]

报告类型
[ 下拉框 ]

[ 生成并归档 ]

已归档报告
[ 下拉框 ]

[ 打开归档 ]
[ 复制摘要 ]

[ Markdown ] [ HTML ]
[ PDF      ] [ PNG长图 ]
```

不再把所有控件挤在同一横行。

## 4. AI 设置

Key 输入区域只显示简短状态：

```text
Key 已读取：35 字符 · 末尾 5db9
```

完整 SHA-256 指纹只保留在诊断日志/失败弹窗，不再占页面空间。
