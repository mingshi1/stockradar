# V1.0.0 RC4.8 Android wheel 校验修复

## RC4.7 为什么 0 秒失败

RC4.7 日志显示：

```text
Android target Python:
3.11.15

Host Python:
3.11.15

PySide6:
6.11.1
```

这些都正确。

失败来自我们自己的检查：

```text
ERROR: PySide Android wheel is not the expected cp311 aarch64 wheel.
exit code 10
```

RC4.7 下载时把官方文件名：

```text
pyside6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl
```

重命名成：

```text
pyside6-6.11.1-android_aarch64.whl
```

因此检查文件名是否含 `cp311` 必然失败。

## RC4.8

下载后保留官方原始文件名，并使用 Python Packaging 的
`parse_wheel_filename()` 做结构化校验。

预期 Build Android APK Beta 开头出现：

```text
Validating Android wheel ABI/platform metadata...
...
Android wheel ABI/platform validation: OK
```

然后才继续 pyside6-android-deploy / Buildozer。

## 成功目标

```text
Build Android APK Beta
✓

Validate collected APK/AAB
✓

Upload Android Beta
✓
```

下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.8
```
