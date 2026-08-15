# AI板块事件雷达 v1.0.0-rc4

V0.9 的主题是：

> 从开发项目进入可发布软件阶段。

---

# V0.9 新增

## 首次启动向导

第一次启动会出现：

```text
欢迎
→ 配置第一个联网 AI
→ 选择分析模式
→ 使用说明
→ 主界面
```

用户不再需要一上来就理解：

```text
Research Provider
Judge
Base URL
Consensus
```

---

## 响应式导航

桌面宽屏：

```text
左侧 Sidebar
+
主内容
```

窗口变窄 / Android Beta：

```text
顶部导航
+
主内容
```

系统设置可以强制：

```text
自动
桌面
移动 / 窄屏
```

V0.9 是移动端 Beta UI 基础，V1.0 再继续做最终手机体验优化。

---

## 系统与数据

左侧新增：

```text
系统与数据
```

包括：

- SQLite Schema Version
- 数据库路径
- 备份数据库
- 恢复数据库
- 打开数据目录
- 打开日志目录
- 响应式 UI 模式
- 重新运行首次启动向导
- API Key 持久化状态

---

## SQLite Migration

V0.9 正式加入数据库结构版本：

```text
PRAGMA user_version
schema_migrations
```

当前：

```text
Schema Version 1
```

这为 V1.0 和未来升级旧数据库建立正式 migration 基础。

---

## 数据库备份 / 恢复

不再简单复制正在使用的数据库。

程序使用 SQLite backup API。

恢复前会检查：

```text
analysis_runs
events
custom_sectors
```

等关键表是否存在。

---

## Windows 应用图标

新增：

```text
resources/app_icon.png
resources/app_icon.ico
```

Windows EXE / Installer 构建会使用 `.ico`。

---

# Windows 打包

提供：

```text
scripts/build_windows.ps1
scripts/configure_deploy.py
installer/StockEventRadar.iss
requirements-build.txt
```

发布流程：

```text
PySide6 source
→ pyside6-deploy
→ Nuitka
→ StockEventRadar.exe
→ Inno Setup
→ StockEventRadar-Setup-0.9.0.exe
```

---

# GitHub Actions

新增：

```text
.github/workflows/windows-release.yml
.github/workflows/android-beta.yml
```

Windows 可以：

```text
手动触发
```

或者：

```text
git tag v1.0.0-rc4
git push origin v1.0.0-rc4
```

触发 Release 构建。

---

# Android Beta

V0.9 包含 Android Beta 构建准备：

```text
requirements-android.txt
scripts/build_android.sh
android-beta.yml
```

重要：

Android Beta 的 API Key 当前只保存在运行内存中。

这是刻意的安全取舍：

```text
不安全地明文永久存储 Key
```

和

```text
Beta 阶段重新输入 Key
```

之间，V0.9 选择后者。

V1.0 再评估 Android Keystore 原生安全存储。

---

# 已有功能全部保留

- DeepSeek
- Qwen
- GLM
- Kimi
- Doubao
- MiniMax
- 同证据 Multi-AI
- Consensus Engine
- Judge
- 自定义板块
- Event Pool
- SQLite 历史
- 实时进度
- Token / 成本
- Provider 性能统计
- 板块趋势
- 晨报归档
- PDF
- PNG 长图
- HTML
- Markdown
- 日志

---

# 安装开发依赖

```powershell
python -m pip install -r requirements.txt
```

V0.9 正常开发运行没有新增第三方运行依赖。

---

# 本地运行

```powershell
python main.py
```

---

# Windows Build

详见：

```text
DEPLOYMENT.md
```

最简：

```powershell
.\scripts\build_windows.ps1
```

---

# 推荐 V0.9 验收

## 软件本体

1. 首次启动向导正常。
2. DeepSeek 等原 API Key 在 Windows 仍可读取。
3. 今日分析正常。
4. Multi-AI 进度正常。
5. 历史 / 新闻 / 统计 / 报告正常。

## 响应式

1. 把窗口宽度缩到 900 以下。
2. 左 Sidebar 应隐藏。
3. 顶部出现移动导航。
4. 再拉宽后恢复 Sidebar。
5. 系统与数据可强制 Desktop / Mobile。

## 数据

1. 系统与数据 → 备份。
2. 确认产生 `.db`。
3. 恢复该备份。
4. 历史数据仍存在。
5. Schema Version 显示 1。

## Windows Build

1. 安装 Visual Studio Build Tools + Inno Setup。
2. 运行 `scripts\build_windows.ps1`。
3. 测试 `dist\StockEventRadar.exe`。
4. 测试 Setup 安装和卸载。

## GitHub

1. Push dev-v0.9。
2. 手动跑 Windows Release Build。
3. 下载 GitHub Artifact，在第二台 Windows 测试。

---

# V1.0 剩余目标

V1.0 不再大改架构。

主要做：

- 新手模式 / 高级模式
- Windows Release 最终验证
- Android Beta 真实设备测试
- Android UI 最终适配
- 错误信息最终整理
- 隐私说明
- API Key 说明
- License / Third-party notices
- 数据迁移最终验证
- 多台 Windows / 多台 Android 测试
- 性能优化
- 版本发布页面


---

# V1.0.0 RC4 Hotfix

本修订专门修复两项 V0.9 Windows 测试问题：

1. 窄屏 / 移动导航的 QComboBox 弹出菜单在部分 Windows 配色下出现
   “深色背景 + 深色文字”，现在统一使用白色菜单背景和深色文字，
   选中项使用蓝底白字。

2. 新增：

```text
scripts\build_windows.cmd
```

如果 `.ps1` 因 PowerShell Execution Policy 被拦截，可以直接：

```powershell
.\scripts\build_windows.cmd
```

CMD 包装器只为启动的子 PowerShell 进程传入：

```text
-ExecutionPolicy Bypass
```

不会永久修改系统执行策略。

如果希望继续直接运行 `.ps1`，也可以先对可信脚本执行：

```powershell
Unblock-File .\scripts\build_windows.ps1
```


---

# V1.0.0 RC4 Windows Build Hotfix

如果旧版构建日志出现：

```text
Succeeded with add resources to file ... deployment\main.exe
...
FileNotFoundError:
...\dist\StockEventRadar.exe
```

说明 Nuitka 编译已经成功，失败发生在最终复制阶段。

V1.0.0 RC4 会在编译前创建：

```text
dist\
deployment\
```

并增加自动恢复：

```text
deployment\main.exe
→
dist\StockEventRadar.exe
```

推荐：

```powershell
.\scripts\build_windows.cmd
```


---

# V1.0.0 RC4：Windows 构建缓存转移到 D 盘

默认大型构建工作区：

```text
D:\StockEventRadarBuild
├── temp
├── nuitka-cache
└── pip-cache
```

项目自身的构建输出继续在 D 盘项目目录：

```text
D:\coding\stock-event-radar
├── deployment
└── dist
```

正常构建：

```powershell
.\scripts\build_windows.cmd
```

清理以前 C 盘上的 Nuitka / pip 构建缓存：

```powershell
.\scripts\cleanup_c_build_cache.cmd
```

这个清理脚本不会删除：

```text
%APPDATA%\StockEventRadar\stockradar.db
```

也不会粗暴删除整个 Windows `%TEMP%`。


---

# V1.0.0 RC4：自动任务中心

本候选版新增：

- Windows 每日固定时间自动分析
- Windows 时间同步
- 自动报告 / PDF
- SMTP 测试邮件
- 自动报告邮件
- 自动任务运行历史
- SQLite schema v2
- `--run-task <ID>` 无主窗口任务模式

详细测试步骤见：

```text
V1_RC1_TEST_PLAN.md
```

建议测试通过后再创建 GitHub Release / Android Beta。


---

# V1.0.0 RC4

RC3 将邮件/SMTP功能从正式范围中移除，聚焦：
- 自动定时分析
- 时间同步
- 自动报告
- 自定义报告目录
- Windows 发布
- Android Beta 真机测试

测试步骤见 `V1_RC3_TEST_PLAN.md`。

## RC3 功能范围说明

邮件 / SMTP 功能已从当前版本移除。自动任务只负责定时分析、报告归档和本地 PDF 保存。


---

# V1.0.0 RC4

RC4 重点是发布流水线可靠性：

- Windows GitHub Actions 显式加载 MSVC / dumpbin
- PySide6 6.11.1 + Nuitka 4.x 固定版本范围
- Nuitka 详细诊断日志和 report
- Android GitHub Action 自动使用官方 ARM64 wheels
- Android Host Python 3.11
- 不再要求手工填写 Android wheel URL

详细步骤见 `V1_RC4_TEST_PLAN.md`。
