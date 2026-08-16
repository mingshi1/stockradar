# Changelog

## 1.0.0-rc4.18

### Android HTTPS certificate + minimal AI settings
- RC4.17 已稳定进入主界面，原生闪退问题不再是当前阻塞点。
- DeepSeek 测试连接已真正发起 HTTPS 请求，但 Android 内置 Python
  报 `CERTIFICATE_VERIFY_FAILED / self-signed certificate in certificate chain`。
- Android APK 新增 `certifi==2026.7.22`。
- Android HTTP client 使用 `ssl.create_default_context(cafile=certifi.where())`
  显式加载 Mozilla CA bundle。
- HTTPS 证书验证和 hostname checking 保持开启；不采用不安全的
  `CERT_NONE` / `verify=False`。
- 若 Mozilla CA 下仍验证失败，错误提示会明确建议检查 VPN、抓包代理、
  HTTPS 过滤、公司/校园 Wi-Fi，并可切换 5G/其他网络测试。
- Android AI 设置页大幅简化：
  - 每个 Provider 只显示：参与分析、模型、API Key、连接状态、测试按钮
  - Android 隐藏 Base URL，强制使用 Provider 官方默认 Base URL
  - Android 隐藏输入/输出 Token 单价
  - Android 保存时成本单价固定为 0，不做成本估算
  - 隐藏手机端冗长成本提示和 Provider 说明
  - 测试/保存按钮改为全宽触屏布局
- Windows 版继续保留 Base URL 与 Token 成本配置，不改变桌面能力。
- 继续只上传一个 APK：
  `StockEventRadar-Android-arm64-v8a-debug.apk`。

## 1.0.0-rc4.17

### Android Shiboken virtual-override stability pass
- RC4.16 荣耀真机仍发生相同 native SIGSEGV。
- ADB backtrace 继续指向：
  `libshiboken6 -> storePythonOverrideErrorOrPrint -> QWidget::event`
  并伴随 Android geometry change / QWidget visibility。
- RC4.17 不再只保护 resizeEvent，而是从 Android 运行路径移除
  自定义 QWidget 虚函数 override：
  - MainWindow 完全移除 Python `resizeEvent()`
  - Desktop 响应式布局改用 QTimer 宽度轮询
  - Android 只在窗口显示后做一次普通方法的移动布局
  - Android TrendChart 改为 QLabel 文本趋势，不再覆写 `paintEvent()`
  - MobileFirstRunDialog 不再覆写 `QDialog.accept()`
- Android MainWindow `show()` 改为 Qt 主事件循环启动后通过 QTimer 调度。
- 移动布局在 native window 建立后延迟 120ms 应用。
- 启动阶段日志改成 `flush=True`，并同步写
  `startup_stage.log`，下次即使 native crash 也能看到准确阶段。
- 继续只上传一个 APK：
  `StockEventRadar-Android-arm64-v8a-debug.apk`。

## 1.0.0-rc4.16

### Android MainWindow native crash fix
- 荣耀真机 ADB 已确认 Android 平台识别正确。
- RC4.15 真正崩溃为 qtMainLoopThread 上的 SIGSEGV。
- native stack 位于 libshiboken6 Python override error handling，
  并经过 QWidget::event / processGeometryChangeEvent / QWidget::show。
- 修复 MainWindow 在 UI 构建完成前可能触发 resizeEvent 的初始化竞态。
- Android 不再在 `_build_ui()` 前执行桌面尺寸 `resize(1360, 880)`。
- 增加 `_ui_ready` guard；UI 未完整创建时 resizeEvent 不执行响应式布局。
- resizeEvent 内部异常全部捕获并记录，不允许异常穿过 Qt virtual override。
- 增加 MainWindow constructing / constructed / shown 阶段日志。
- 继续只上传一个 Android APK。

## 1.0.0-rc4.15

### Android runtime detection root fix
- 修复 Android APK 中 `No module named 'openai'`。
- 根因不是 API Key，而是 Python 3.11 Android 平台识别错误。
- CPython 3.11 Android 运行时可能仍报告：
  `sys.platform == "linux"`。
- Android 检测改为：
  1. `sys.platform == "android"`
  2. Android-only `sys.getandroidapilevel()`
  3. p4a/Buildozer Android 环境变量 fallback
- 修复后 Android 会真正启用：
  - `AndroidOpenAICompat` 标准库 API client
  - Android session-only API Key 存储
  - QStandardPaths Android 数据目录
  - RC4.14 移动端字体和纵向布局
  - Android 首次启动单页触屏界面
- 启动日志增加无敏感信息的 runtime platform 诊断。
- 继续只上传：
  `StockEventRadar-Android-arm64-v8a-debug.apk`。

## 1.0.0-rc4.14

### Android mobile UI usability pass
- Android 已能正常进入主界面，不再闪退。
- Android 首次启动不再使用 QWizard：
  改为单页、可滚动、底部固定“进入主界面”按钮。
- 修复首次启动页面触屏操作像“无反应”的问题。
- Android 全局字体和控件间距缩小：
  标题、卡片标题、正文、按钮、表格、输入框统一移动端尺寸。
- 顶部导航 QComboBox 使用显式 QListView：
  白底黑字，选中为浅蓝底黑字。
- 修复 Android 下拉菜单出现“白字白底，看起来一大片空白”的问题。
- AI 设置页 Android 改为纵向表单：
  避免 Provider、Judge、价格输入等控件在窄屏互相覆盖。
- Android Token 单价输入后缀简化为 `/1M`。
- 历史报告页 Android 改为上下布局，不再左右挤压。
- 页面外边距在 Android 下统一缩小。
- 删除活动页面中的旧 `V0.9` 文案，更新为 `V1.0`。
- 继续只上传一个 APK：
  `StockEventRadar-Android-arm64-v8a-debug.apk`。

## 1.0.0-rc4.13

### GitHub Actions YAML hotfix
- 修复 RC4.12 `.github/workflows/android-beta.yml` 的 YAML 缩进错误。
- `Validate single Android APK` 恢复为 `steps` 下的合法同级步骤。
- RC4.12 的 0 秒失败发生在 GitHub workflow 解析阶段，
  Android 构建本身根本没有开始。
- 保留“只上传一个 APK”的 RC4.12 设计。
- 清理 diagnostics path 中重复条目。
- Android Artifact：
  `StockEventRadar-Android-Beta-1.0.0-rc4.13`。

## 1.0.0-rc4.12

### Android single-APK test build
- Android 构建成功后只保留 1 个 APK。
- 优先选择包含 `arm64-v8a` + `debug` 的 APK。
- 最终统一命名：
  `StockEventRadar-Android-arm64-v8a-debug.apk`
- GitHub Artifact 不再包含 3 份重复 APK，显著减少下载和手机传输时间。
- 验证步骤要求 `android-output/` 中恰好只有 1 个 APK。
- RC4.11 在荣耀手机仍然“无提示直接闪退”。
- 因为 Python 层启动异常提示也没有出现，下一步改用 Android `adb logcat`
  获取系统/native/Qt 层真实崩溃原因，不再继续猜测。

## 1.0.0-rc4.11

### Android first-launch crash hotfix
- Android APK 已成功生成并可安装，但荣耀手机首次启动立即闪退。
- 修复 Android 启动时对桌面 `openai` SDK 的顶层硬依赖。
- Desktop 继续使用官方 OpenAI-compatible Python SDK。
- Android 改用标准库 `urllib` 实现轻量 OpenAI-compatible HTTP client：
  - `/chat/completions`
  - `/responses`
- Android APK 不再需要打包 `openai/httpx/pydantic` 依赖树。
- Android AppData 改用 Qt `QStandardPaths.AppDataLocation`。
- `main.py` 延迟导入应用模块，并增加启动异常捕获。
- 若仍发生 Python 层启动错误，RC4.11 会尝试弹出“启动失败”对话框，
  同时写入 `startup_crash.log`，避免只有无信息闪退。
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.11`。

## 1.0.0-rc4.10

### Android libffi / native prerequisites fix
- 完整 `android-deploy.log` 已定位真实 Buildozer 根因：
  p4a 的 `libffi/autogen.sh` 在 `autoreconf` 阶段失败。
- 真实错误：
  `possibly undefined macro: LT_SYS_SYMBOL_USCORE`。
- GitHub Ubuntu Runner 在 Android 构建前显式安装 native prerequisites：
  - autoconf
  - automake
  - autopoint
  - build-essential
  - cmake
  - gettext
  - libffi-dev
  - libltdl-dev
  - libssl-dev
  - libtool
  - libtool-bin
  - pkg-config
  - zlib1g-dev
- 特别加入 `libltdl-dev`，解决 libffi autotools 宏依赖问题。
- 修复 prerequisite 自检中的 `Broken pipe`：
  不再使用 `libtoolize --version | head -1` 等 pipefail 易误报写法。
- 版本检查改为直接执行完整 `--version`。
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.10`。

## 1.0.0-rc4.9

### Android pipeline stabilization
- 修正 RC4.7/RC4.8 的 Python 3.14 误报检测：
  p4a 仓库里的 `3.14_*.patch` 文件并不等于本次目标 Python 是 3.14。
- 不再通过 p4a 源码中的补丁文件名判断目标 Python 版本。
- 固定 python-for-android 为正式 release `v2026.05.09`，
  不再跟随不断变化的 `develop`。
- 在 GitHub 临时环境中 patch Qt 6.11.1 Android deploy helper，
  让生成的 Buildozer 配置直接使用：
  `python3==3.11.15,hostpython3==3.11.15,shiboken6,PySide6`。
- 同时保留 Buildozer 官方 `APP_REQUIREMENTS` / `APP_P4A_BRANCH`
  环境覆盖作为双保险。
- 完整保存 `android-deploy.log`。
- 即使 `pyside6-android-deploy` 外层进程返回 0，
  只要日志出现 Buildozer traceback / non-zero exit，也会正确判为失败。
- 失败时自动打印最相关错误行和完整日志尾部。
- Android Artifact 更新为
  `StockEventRadar-Android-Beta-1.0.0-rc4.9`。

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
