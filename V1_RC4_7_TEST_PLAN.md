# V1.0.0 RC4.7 Android Python ABI 修复

## RC4.6 暴露的真正问题

Android wheels：

```text
cp311-cp311-android_aarch64
```

但 python-for-android 实际下载并构建：

```text
hostpython3 v3.14.2
python3 v3.14.2
```

这是目标 Python ABI 错配。

Qt 6.11.1 的 Android deploy 生成 Buildozer 配置时默认写：

```text
requirements = python3,shiboken6,PySide6
```

没有固定 Python 版本。

当前 p4a develop 已经会选择较新的 Python，因此 RC4.6 进入了 3.14 构建。

python-for-android 官方文档支持通过 requirements 同时固定：

```text
python3==X.Y.Z
hostpython3==X.Y.Z
```

## RC4.7

固定：

```text
Python host:   3.11
Android target: 3.11.15
Android hostpython: 3.11.15
Qt wheels ABI: cp311
```

Buildozer override：

```text
APP_REQUIREMENTS=
python3==3.11.15,
hostpython3==3.11.15,
shiboken6,
PySide6
```

同时每次构建前删除项目 `.buildozer`，防止复用旧 3.14 缓存。

## GitHub 测试时重点看

Build Android APK Beta 日志中不应该再出现：

```text
v3.14.2.tar.gz
python3.14
libpython3.14
```

应该出现 Python 3.11.x。

成功后：

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
StockEventRadar-Android-Beta-1.0.0-rc4.7
```
