# Changelog

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
