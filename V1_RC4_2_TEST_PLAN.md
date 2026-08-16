# V1.0.0 RC4.2 Android 测试

RC4.1 已通过：
- Python 3.11
- PySide6 环境
- 官方 Android ARM64 wheel URL 校验
- PySide6 Android wheel 下载
- Shiboken6 Android wheel 下载

RC4.1 失败于：

```text
Download matching Android SDK and NDK
ModuleNotFoundError: No module named 'git'
```

Qt 官方 `tools/cross_compile_android/main.py` 有自己的 Python 依赖。
RC4.2 在 clone Qt for Python 源码后执行：

```bash
python -m pip install \
  -r pyside-setup/tools/cross_compile_android/requirements.txt
```

并验证：

```bash
python -c "import git"
```

## GitHub 测试

Push 后进入：

```text
Actions
→ Android Beta Build
```

预期步骤：

1. Checkout
2. Setup Python 3.11
3. Install app build environment
4. Verify official Android wheel URLs
5. Download official Android ARM64 wheels
6. Clone matching Qt for Python tools
7. Install Qt Android tool dependencies
8. Download matching Android SDK and NDK
9. Build Android APK Beta
10. Collect APK/AAB
11. Upload Android Beta

成功后页面底部下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.2
```

解压后应包含 `.apk`。
