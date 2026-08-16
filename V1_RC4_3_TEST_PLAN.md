# V1.0.0 RC4.3 Android 测试

## RC4.2 已经通过

- Checkout
- Python 3.11
- 应用 Python 依赖
- Android wheel URL 验证
- PySide6 Android ARM64 wheel 下载
- Shiboken6 Android ARM64 wheel 下载
- Qt for Python tools clone
- GitPython 安装

## RC4.2 当前错误

```text
ModuleNotFoundError: No module named 'packaging'
```

Qt 官方 Android 交叉编译说明要求同时安装：

```bash
pip install -r requirements.txt
pip install -r tools/cross_compile_android/requirements.txt
```

RC4.2 只安装了第二份。

RC4.3 已改为两份都安装，并增加：

```text
GitPython 检查
packaging 检查
JDK 21
JAVA_HOME 检查
```

## GitHub 测试

Push 后进入：

```text
Actions
→ Android Beta Build
```

预期依次通过：

1. Checkout
2. Setup Python 3.11
3. Setup Java 21
4. Verify Java
5. Install app build environment
6. Verify official Android wheel URLs
7. Download official Android ARM64 wheels
8. Clone matching Qt for Python tools
9. Install Qt for Python tool dependencies
10. Download matching Android SDK and NDK
11. Build Android APK Beta
12. Collect APK/AAB
13. Upload Android Beta

成功以后下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.3
```

解压后应包含 `.apk`。
