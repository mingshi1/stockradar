# AI板块事件雷达 V1.0.0 RC3 测试计划

## RC3 核心范围

保留：
- 当前时间 / 时区显示
- Windows 时间同步
- 每日固定时间自动分析
- Windows Task Scheduler
- 自动任务历史
- 自动报告归档
- 用户自定义 PDF 保存目录
- Windows EXE / Setup 打包
- Android Beta 构建准备

移除：
- SMTP / 邮件发送
- 邮箱账号、授权码配置
- 自动邮件附件

## 1. 源码测试

```powershell
python main.py
```

检查：
- 左侧存在“自动任务”
- 不再出现任何邮件/SMTP设置
- AI设置页没有旧 V0.8 文案

## 2. 自定义报告目录

建议设置：

```text
D:\StockEventRadarReports
```

新建一个只分析“黄金”的任务：
- 运行时间：当前时间后 5~10 分钟
- 报告类型：30秒晨报
- 自动生成 PDF：开启
- 报告保存目录：D:\StockEventRadarReports

先点“立即执行”，确认：
- 历史分析新增
- 报告归档新增
- PDF 出现在 D:\StockEventRadarReports

## 3. 真正定时测试

保存一个当前时间后 5~10 分钟的每日任务。
完全关闭主窗口。

到点后重新打开应用，检查：
- 历史分析新增
- 自动任务运行记录为 success
- PDF 已生成

## 4. Windows EXE

```powershell
.\scripts\build_windows.cmd
```

检查：

```text
dist\StockEventRadar.exe
```

从 EXE 创建一个几分钟后的自动任务，再关闭 EXE，验证系统计划任务仍会触发。

## 5. Setup

检查：

```text
installer\output\StockEventRadar-Setup-1.0.0-rc3.exe
```

本机安装、运行、创建定时任务、卸载。

## 6. Android

Windows 版通过后再进行 Android APK 构建和真机测试。
Android 不能使用 Windows EXE/Setup。
