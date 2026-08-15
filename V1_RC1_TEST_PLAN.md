# AI板块事件雷达 V1.0.0 RC2 测试计划

## 本版本新增

- 自动任务中心
- 当前本地时间 / 时区实时显示
- Windows `w32tm /resync` 时间同步按钮
- SQLite 自动任务与运行历史（schema v2）
- Windows Task Scheduler 每日任务
- `StockEventRadar.exe --run-task <ID>` 后台任务入口
- 自动生成晨报 / 标准 / 共识 / 深度报告
- 可选自动 PDF
- SMTP 邮件设置
- SMTP 测试邮件
- 自动报告邮件 + 可选 PDF 附件
- SMTP 密码/授权码通过 SecretStore 保存，不写入 settings.json
- Windows 构建继续使用 D 盘缓存
- Windows 构建增加 `D:\Inno Setup 6\ISCC.exe` 自动发现

## 推荐测试顺序

### A. 源码运行

```powershell
python main.py
```

检查左侧出现“自动任务”。

### B. 时间

进入“自动任务”：
- 当前时间每秒变化
- 时区和 UTC 偏移正确
- 点击“同步 Windows 时间”
- 如果 Windows 权限/服务不允许，要看到明确错误，而不是卡死

### C. 新建任务

建议先做一个 5~10 分钟后的测试任务：
- 名称：RC2测试
- 启用
- 时间：当前时间后 5~10 分钟
- 板块：黄金
- 分析模式：跟随当前 AI 设置
- 报告：30秒晨报
- PDF：启用
- 邮件：第一次先关闭

保存后，Windows Task Scheduler 应注册：
`StockEventRadar_Daily_<ID>`。

### D. 立即执行

选中任务 → “立即执行”。

检查：
- 联网研究完成
- 历史分析新增
- 报告中心新增晨报
- 自动任务运行历史新增记录
- `%APPDATA%\StockEventRadar\auto_reports` 有 PDF

### E. 真正定时触发

保存一个几分钟后的时间，然后完全关闭主窗口。

等到计划时间后重新打开软件，检查：
- 历史分析是否自动新增
- 自动任务运行记录是否 success
- PDF 是否生成

### F. SMTP

先在邮件设置中填写：
- SMTP服务器
- 端口
- SSL / STARTTLS
- 用户名
- 密码/授权码
- 发件地址
- 默认收件人

点击“发送测试邮件”。

注意：很多邮箱要求“SMTP授权码”，不是网页登录密码。
不要把密码或授权码发到聊天里。

### G. 自动邮件

把测试任务勾选“任务完成后发送邮件”，再执行一次。
检查：
- 正文收到
- 开启 PDF 时附件收到
- task_runs 的 email_status 为 sent

### H. EXE

```powershell
.\scripts\build_windows.cmd
```

目标：
`dist\StockEventRadar.exe`

从 EXE 创建任务时，Windows Task Scheduler 应直接调用：
`StockEventRadar.exe --run-task <ID>`

### I. Setup

目标：
`installer\output\StockEventRadar-Setup-1.0.0-rc2.exe`

在本机安装测试：
- 安装
- 启动
- 新建任务
- 定时触发
- 卸载

## RC2 已知边界

- 系统级定时后台调度目前正式实现的是 Windows Task Scheduler。
- Android 后台任务/Keystore 仍属于后续真机阶段；不能把 Windows EXE 直接装到 Android。
- “同步时间”调用 Windows 自己的时间服务，不自行实现 NTP 客户端。
- 如果 Windows Time 服务、系统策略或权限阻止同步，界面会显示原始错误。
- 定时任务使用当前 AppConfig / API Key；如果更换研究 Provider，要保证对应 Key 已安全保存。


## RC2 新增测试：自定义报告目录

1. 在自动任务里点击“选择目录”。
2. 建议选择例如：

```text
D:\StockEventRadarReports
```

3. 保存任务并“立即执行”。
4. 确认 PDF 出现在指定目录，而不是默认 AppData 目录。

## RC2 Outlook.com 提醒

Outlook.com 官方 SMTP 参数：

```text
服务器：smtp-mail.outlook.com
端口：587
加密：STARTTLS
```

但 Outlook.com 当前要求 OAuth2/Modern Auth。
RC2 的传统 SMTP 密码模式可能被 Microsoft 拒绝。
若出现 535/Authentication unsuccessful，请记录错误文本，不要反复修改账号密码。
