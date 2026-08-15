# AI板块事件雷达 V1.0.0 RC4 发布流水线测试

## 为什么 RC3 GitHub Windows 构建失败

截图显示：
- GitHub Runner 使用正确的 hosted Python 3.12，而不是本机 PyMOL。
- 失败发生在 `pyside6-deploy / Nuitka` 阶段。
- 后续 Inno Setup、Installer、Artifact 都因为前一步 exit 1 被跳过。
- RC3 使用 `--quiet`，截图没有保留最前面的真实 Nuitka 编译错误。
- Qt 官方要求 Windows 部署环境可访问 `dumpbin`；`dumpbin` 随 MSVC 提供，需要加载 Visual Studio developer environment。

RC4 因此：
1. 使用 vswhere 找 Visual Studio 2022。
2. 加载 VsDevCmd.bat。
3. 验证 cl.exe / dumpbin.exe。
4. 再运行 pyside6-deploy。
5. 去掉 --quiet 并保存 Nuitka report。

## Windows GitHub 测试

建议分支：

```powershell
git checkout -b dev-v1.0-rc4
git add .
git commit -m "Fix Windows and Android release pipelines for v1.0 RC4"
git push -u origin dev-v1.0-rc4
```

RC4 workflow 会自动在 `dev-v1.0-*` push 时运行 Windows Build。

成功后 GitHub Actions 页面应出现 Artifact：

```text
StockEventRadar-Windows-1.0.0-rc4
```

里面有：
- `StockEventRadar.exe`
- `StockEventRadar-Setup-1.0.0-rc4.exe`

失败时会出现诊断 Artifact：

```text
StockEventRadar-Windows-Diagnostics-1.0.0-rc4
```

## Android GitHub 测试

Push `dev-v1.0-*` 分支时 RC4 会自动启动 Android Beta Build；
也可以在 Actions 页面手动运行。

RC4 不再要求填写 PySide6/Shiboken URL。

固定：
- Host Python: 3.11
- PySide6: 6.11.1
- Android: aarch64 / ARM64
- Qt for Python branch: 6.11

成功后下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4
```

其中应有 APK。

## 手机安装

把 APK 下载到 Android 手机。
首次安装外部 APK 时，Android 可能要求允许浏览器/文件管理器“安装未知应用”。

重点测试：
- 启动
- 窄屏导航
- API设置
- 一次真实分析
- 历史报告
- 报告导出

RC4 Android 仍是 Beta。Windows Task Scheduler 不适用于 Android；Android 后台定时任务需要后续单独适配 Android 的后台调度机制。

## 正式 tag

RC4 测试期间不要创建：

```text
v1.0.0
```

全部通过后再：

```powershell
git checkout main
git merge dev-v1.0-rc4
git tag v1.0.0
git push origin main
git push origin v1.0.0
```
