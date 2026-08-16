# V1.0.0-rc4.16 Deployment Guide

V1.0.0-rc4.16 第一次把“开发项目”升级成“可发布项目”。

---

# Windows 本地构建

## 需要的软件

开发环境继续使用 Python 3.12 / stockradar-dev。

另外 Windows 本地打包建议安装：

1. Visual Studio 2022 Build Tools
   - C++ build tools
   - MSVC
2. Inno Setup 6

然后在项目根目录：

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt
```

执行：

```powershell
.\scripts\build_windows.ps1
```

脚本流程：

```text
pyside6-deploy
→ Nuitka
→ dist\StockEventRadar.exe
→ Inno Setup
→ installer\output\StockEventRadar-Setup-1.0.0-rc4.16.exe
```

如果暂时没有 Inno Setup：

```powershell
.\scripts\build_windows.ps1 -SkipInstaller
```

只生成 EXE。

---

# GitHub Windows Release

项目包含：

```text
.github/workflows/windows-release.yml
```

支持：

```text
Actions → Windows Release Build → Run workflow
```

也支持推送 tag：

```powershell
git tag v1.0.0-rc4.16.1
git push origin v1.0.0-rc4.16.1
```

tag 构建成功后，workflow 会尝试把：

```text
StockEventRadar.exe
StockEventRadar-Setup-1.0.0-rc4.16.exe
```

上传到 GitHub Release。

---

# Android Beta

当前项目保留 Qt Widgets UI，并增加窄屏响应式导航。

Android 构建使用：

```text
pyside6-android-deploy
```

项目提供：

```text
scripts/build_android.sh
.github/workflows/android-beta.yml
requirements-android.txt
```

Android Beta 当前安全策略：

```text
API Key 只保存在本次 App 运行内存
```

不会明文写入 settings.json。

这意味着：

```text
关闭 Android App
→ 下次启动
→ 需要重新输入 API Key
```

V1.0 前再决定是否接 Android Keystore 原生安全存储。

---

# Android GitHub Action

进入：

```text
GitHub
→ Actions
→ Android Beta Build
→ Run workflow
```

需要填两个官方 Android wheel 的直链：

```text
PySide6 Android aarch64 wheel
shiboken6 Android aarch64 wheel
```

以及对应 Qt for Python branch，例如：

```text
6.10
```

workflow 会：

```text
Ubuntu
→ 下载 Android wheels
→ 下载匹配 SDK / NDK
→ pyside6-android-deploy
→ 收集 APK / AAB
→ 上传 Artifact
```

这是 Beta 构建通道，不等同于 V1.0 已完成正式 Android 发布。

---

# 数据目录

Windows 默认：

```text
%APPDATA%\StockEventRadar
```

包括：

```text
settings.json
stockradar.db
logs\
```

API Key 不在这里。

---

# 数据库备份

软件：

```text
系统与数据
→ 备份数据库
```

使用 SQLite 自己的 backup API，生成 `.db` 文件。

恢复：

```text
系统与数据
→ 恢复数据库
```

程序会先检查备份是否包含 StockEventRadar 必需的数据表。

---

# 数据库 Migration

V1.0.0-rc4.16 开始正式记录：

```text
PRAGMA user_version
schema_migrations
```

当前：

```text
Schema Version = 1
```

未来 V1.0 如果修改数据库结构，会从这里按版本执行 migration，而不是继续依赖“希望旧数据库刚好兼容”。

---

# 首次启动

新用户第一次打开：

```text
欢迎
→ 选择 Research Provider
→ 可输入 API Key
→ 选择快速 / Multi-AI
→ 完成
```

之后不会重复弹出。

可以在：

```text
系统与数据
→ 重新运行首次启动向导
```

再次打开。


## PowerShell 提示

如果直接运行：

```powershell
.\scripts\build_windows.ps1
```

出现“未进行数字签名 / PSSecurityException”，优先使用：

```powershell
.\scripts\build_windows.cmd
```

或者在确认脚本可信后：

```powershell
Unblock-File .\scripts\build_windows.ps1
.\scripts\build_windows.ps1
```


## D 盘构建缓存

V1.0.0-rc4.16 默认构建缓存：

```text
D:\StockEventRadarBuild
```

构建脚本仅对当前构建进程设置：

```text
TEMP
TMP
TMPDIR
NUITKA_CACHE_DIR
PIP_CACHE_DIR
```

不会永久修改 Windows 用户环境变量。

清理旧 C 盘 Nuitka / pip 缓存：

```powershell
.\scripts\cleanup_c_build_cache.cmd
```
