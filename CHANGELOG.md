# Changelog

## 1.0.0-rc4.8

### Android wheel validation hotfix
- RC4.7 在真正构建开始前被我们自己的 wheel 文件名检查误拦截。
- Qt 官方 wheel URL 本身包含：
  `cp311-cp311-android_aarch64`，
  但之前 workflow 下载时人为缩短文件名，导致本地文件名丢失 `cp311`。
- RC4.8 保留 Qt 官方原始 wheel 文件名。
- 移除 bash 字符串通配符校验。
- 使用 `packaging.utils.parse_wheel_filename()` 解析 wheel 文件名，
  明确验证：
  - interpreter = cp311
  - abi = cp311
  - platform = android_aarch64
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.8`。

## 1.0.0-rc4.7

### Android Python ABI fix
- RC4.6 诊断日志显示 python-for-android 实际构建了 Python 3.14.2：
  `hostpython3 v3.14.2` / `python3 v3.14.2`。
- 官方 Qt Android wheels 是 `cp311`，因此 Android 目标 Python 必须保持 3.11。
- Buildozer 环境强制：
  `APP_REQUIREMENTS=python3==3.11.15,hostpython3==3.11.15,shiboken6,PySide6`。
- 每次 Android build 前删除项目 `.buildozer`，避免继续复用 RC4.6 的 Python 3.14 缓存。
- 构建前验证 host Python 为 3.11、两个 Android wheels 都是 cp311/aarch64。
- 构建后检测是否意外出现 Python 3.14 路径，出现则立即失败并打印诊断。
- Artifact 更新为 `StockEventRadar-Android-Beta-1.0.0-rc4.7`。

## 1.0.0-rc4.6

### Android artifact collection fix
- RC4.5 的 `Build Android APK Beta` 已成功返回 0。
- 失败发生在我们自己的 `Collect APK/AAB` 步骤，而不是 Android 编译命令。
- 移除 `find . -maxdepth 8` 的目录深度限制。
- `build_android.sh` 现在在构建完成后主动搜索：
  - 应用项目目录
  - `$RUNNER_TEMP`
  - `$HOME/.buildozer`
  - `$HOME/.pyside6-android-deploy`
- 仅收集本次构建开始后新生成的 `.apk` / `.aab`。
- 找到后统一复制到 `android-output/`。
- 找不到时打印 Buildozer/Gradle 常见输出目录和最近的大文件，方便下一轮诊断。
- workflow 的后置步骤只负责验证 `android-output/`。
- Artifact 更新为 `StockEventRadar-Android-Beta-1.0.0-rc4.6`。

## 1.0.0-rc4.5

### Android deploy project-scan fix
- RC4.4 已成功进入 `pyside6-android-deploy` 的模块扫描阶段。
- 修复 Qt for Python `pyside-setup` 源码被 clone 到应用项目根目录，
  导致 deploy 把 Qt 自己的 `__init__.tmpl.py` 当成应用源码解析的问题。
- Qt tools 现在 clone 到 GitHub Runner 临时目录：
  `$RUNNER_TEMP/pyside-setup`。
- SDK/NDK 下载脚本从临时 Qt tools 目录运行。
- 构建前显式检查应用项目中不存在 `pyside-setup`。
- `pyside6-android-deploy` 新增 `--extra-ignore-dirs`，
  排除 android-wheels、android-output、deployment、dist、installer、
  .git、.github 等非应用目录。
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.5`。

## 1.0.0-rc4.4

### Android CI hotfix
- RC4.3 已成功进入 `Build Android APK Beta` 阶段。
- 修复 `pyside6-android-deploy` 启动时缺少 `pkginfo`。
- 不再单独手写 `pip install pkginfo`，而是自动定位并安装当前
  PySide6 自带的 `scripts/requirements-android.txt`。
- 增加 `pkginfo` import 预检。
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.4`。

## 1.0.0-rc4.3

### Android CI hotfix
- RC4.2 已成功解决 GitPython 缺失问题。
- 修复 SDK/NDK 下载阶段：
  `ModuleNotFoundError: No module named 'packaging'`。
- 按 Qt 官方 Android 交叉编译步骤同时安装：
  - `pyside-setup/requirements.txt`
  - `pyside-setup/tools/cross_compile_android/requirements.txt`
- 增加 `import packaging` 和 `packaging.version.Version` 预检。
- GitHub Android Runner 固定 JDK 21，与 Qt 6.11 当前 Android 支持配置一致。
- 增加 Java/JAVA_HOME 诊断。
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.3`。

## 1.0.0-rc4.2

### Android CI hotfix
- RC4.1 已成功解决 Qt Android wheel 下载问题。
- 修复 Android SDK/NDK 下载阶段：
  `ModuleNotFoundError: No module named 'git'`。
- clone Qt for Python 后，自动安装官方：
  `tools/cross_compile_android/requirements.txt`。
- 增加 `import git` / GitPython 预检。
- 将 Qt 工具 clone、依赖安装、SDK/NDK 下载拆成独立步骤，
  后续失败位置更清晰。
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.2`。

## 1.0.0-rc4.1

### Android hotfix
- 修复 PySide6 Android 官方 wheel 文件名大小写：`PySide6-...whl` → `pyside6-...whl`。
- 增加官方 wheel URL HEAD 预检，下载失败时能直接看到 HTTP 错误。
- `actions/upload-artifact` 更新到 v6（Node.js 24）。
- Android Artifact 名更新为 `StockEventRadar-Android-Beta-1.0.0-rc4.1`。

## 1.0.0-rc4

### Windows CI
- GitHub `windows-latest` 构建前显式加载 Visual Studio 2022 Developer Command Prompt 环境。
- 构建前验证 `cl.exe` 与 `dumpbin.exe`。
- 固定 PySide6 6.11.1，并将 Nuitka 限定为 4.0~4.1 系列，减少 CI 与本机的版本漂移。
- 移除 Nuitka `--quiet`，失败时显示真正的编译错误。
- 生成 `deployment/nuitka-report.xml`。
- GitHub 构建失败时自动上传 deployment / spec 诊断 Artifact。
- Checkout / Setup Python 更新到 Node 24 版本的 GitHub Actions。
- Windows 工作流支持 `dev-v1.0-*` 分支 push 测试，不必创建正式 tag。
- 新增 `scripts/build_windows_ci.ps1` 和 `scripts/build_installer.ps1`。

### Android CI
- Android Host Python 改为 3.11，与官方 Android wheel 的 cp311 ABI 对齐。
- 固定 Qt for Python / PySide6 6.11.1。
- ARM64 PySide6 / Shiboken6 官方 wheel URL 内置到 workflow，不再要求手工填写。
- 使用 Qt for Python 6.11 分支下载匹配的 Android SDK / NDK。
- Android deploy 开启 verbose 和 keep-deployment-files，便于失败诊断。
- APK/AAB 未生成时 workflow 明确失败，而不是上传空 Artifact。

### Release discipline
- RC 阶段建议只 push `dev-v1.0-rc4`，不要创建 `v1.0.0` 正式 tag。
- Windows + Android 真机测试通过后再创建正式 v1.0.0 Release。

## 1.0.0-rc3

### Changed
- 从 V1.0 范围移除 SMTP / 邮件发送功能。
- 自动任务聚焦于每日定时分析、自动报告和本地文件保存。
- 保留自定义报告保存目录。
- 新任务强制关闭历史 email 字段，兼容 RC1/RC2 数据库而不做破坏性迁移。

### Build
- 保留 D 盘构建缓存。
- 保留 `D:\Inno Setup 6\ISCC.exe` 自动发现。

### Test
- 新增 `V1_RC3_TEST_PLAN.md`。

## 1.0.0-rc2

### Fixed
- 清理 AI 设置等界面残留的 V0.8 文案。

### Added
- 每个自动任务都可以指定“报告保存目录”。
- 留空时继续使用默认 `%APPDATA%\StockEventRadar\auto_reports\YYYY-MM`。
- 指定目录时 PDF 直接保存到用户选择的文件夹。
- SMTP 页面增加 Outlook.com 参数按钮：
  - `smtp-mail.outlook.com`
  - `587`
  - `STARTTLS`
- Outlook.com 新式身份验证提示，避免把 OAuth2 认证失败误判为密码填写错误。

### Database
- SQLite schema v3。
- `scheduled_tasks` 新增 `report_directory` 字段。

### Status
- Outlook.com 官方目前要求 OAuth2/Modern Auth。
- RC2 仍保留标准 SMTP 用户名/密码模式用于支持该方式的邮箱；
  Outlook OAuth 登录将在实际认证测试需要时单独补齐。

## 1.0.0-rc1

### Added
- 自动任务中心。
- Windows 系统时间同步。
- Windows Task Scheduler 每日固定时间任务。
- `--run-task <ID>` 无主窗口自动任务执行入口。
- 自动报告归档与可选 PDF。
- SMTP 邮件配置、测试邮件、报告邮件、PDF 附件。
- 自动任务运行历史。
- SQLite schema v2：`scheduled_tasks`、`task_runs`。

### Security
- SMTP 密码/授权码继续通过 SecretStore / Windows Credential Manager 保存。
- 不把 SMTP 密码写入 settings.json。

### Build
- 继续把 TEMP / Nuitka / pip 缓存放到 D 盘。
- 自动识别 `D:\Inno Setup 6\ISCC.exe`。

### Status
- RC1 候选测试版；Windows EXE / Setup / 定时触发 / SMTP 需要用户机器实测后再发布正式 v1.0.0。

## 0.9.3

### Changed
- Windows 构建默认把大容量临时文件与缓存移动到 `D:\StockEventRadarBuild`。
- 构建进程的 `TEMP`、`TMP`、`TMPDIR` 指向 D 盘。
- 使用 Nuitka 官方 `NUITKA_CACHE_DIR` 将 Nuitka 缓存移动到 D 盘。
- 使用 `PIP_CACHE_DIR` 将 pip 下载/构建缓存移动到 D 盘。
- `dist` 与 `deployment` 继续位于 D 盘项目目录。

### Added
- `scripts\cleanup_c_build_cache.cmd`
- `scripts\cleanup_c_build_cache.ps1`
- 安全清理旧 Nuitka 与 pip 构建缓存。
- 清理脚本不会删除 StockEventRadar SQLite 历史数据库。

## 0.9.2

### Fixed
- 修复 Windows `pyside6-deploy` 已成功生成 `deployment\main.exe`
  但因 `dist` 目录不存在而在最终复制阶段抛出 `FileNotFoundError`。
- Windows 构建脚本现在在 deployment 前显式创建 `dist` 和 `deployment`。
- `configure_deploy.py` 再次确保 `exec_directory` 存在。
- 增加构建恢复逻辑：如果 Nuitka 已生成 `deployment\main.exe`
  但 pyside6-deploy 最终复制失败，脚本会自动复制为
  `dist\StockEventRadar.exe`，避免整次编译白跑。

### Notes
- Nuitka 的 Windows Defender / Anti-Virus post-processing warning
  如果随后显示 `Succeeded ... in attempt 2`，不属于本次失败根因。

## 0.9.1

### Fixed
- 修复 Windows 窄屏顶部导航 QComboBox 弹出菜单文字/背景对比度过低。
- 修复 Dashboard 残留 V0.8 文案。
- 更新应用、Installer、GitHub Artifact 版本号到 0.9.1。

### Added
- `scripts/build_windows.cmd`：在不永久修改系统 Execution Policy 的情况下启动 Windows 构建脚本。
- README 增加 Windows PowerShell Execution Policy 处理说明。

## 0.9.0

### Added

- First-run onboarding wizard.
- Responsive desktop/mobile navigation.
- System & Data page.
- UI mode: auto / desktop / mobile.
- SQLite schema versioning.
- `schema_migrations` table.
- SQLite backup.
- SQLite backup validation.
- SQLite restore.
- Open data/log directory actions.
- Re-run onboarding action.
- Cross-platform SecretStore abstraction.
- Android Beta session-only secret strategy.
- App PNG / ICO icon.
- Windows build PowerShell script.
- `pyside6-deploy` config helper.
- Inno Setup installer script.
- GitHub Windows Release workflow.
- Android Beta build script.
- GitHub Android Beta workflow.
- Deployment documentation.

### Changed

- Minimum window size reduced for narrow/mobile testing.
- Main navigation switches to top selector on narrow windows.
- MainWindow can reuse AppConfig / ProviderManager from onboarding.
- API Key access no longer imports keyring unconditionally.

### Preserved

All V0.8 analysis, database, report, statistics and Multi-AI functions.

### Next

V1.0:
- final beginner/advanced UI
- Windows production release
- Android real-device RC
- privacy / license / third-party notices
- production QA
