# V1.0.0 RC4.4 Android 测试

RC4.3 已经成功通过：
- Python 3.11
- JDK 21
- PySide6 / Qt 6.11.1
- 官方 Android wheels
- GitPython / packaging
- Android SDK / NDK 下载

RC4.3 已经进入：

```text
Build Android APK Beta
```

当前错误：

```text
The following packages are required but not installed:
- pkginfo

Please install them using:
pip install -r .../PySide6/scripts/requirements-android.txt
```

RC4.4 直接按 pyside6-android-deploy 自己的提示处理：
1. 自动找到当前 PySide6 安装目录。
2. 找到 `scripts/requirements-android.txt`。
3. 安装整份依赖文件。
4. 验证 `import pkginfo`。
5. 再执行 APK 构建。

## 预期 GitHub 步骤

重点观察：

```text
Install pyside6-android-deploy runtime dependencies
✓

Download matching Android SDK and NDK
✓

Build Android APK Beta
...
```

如果成功：

```text
Collect APK/AAB
✓
Upload Android Beta
✓
```

页面底部下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.4
```

解压后应看到 `.apk`。
