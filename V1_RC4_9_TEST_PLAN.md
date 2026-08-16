# V1.0.0 RC4.9 Android 稳定化测试

## 最新日志说明了什么

真正错误是：

```text
python -m buildozer android debug
returned non-zero exit status 1
```

后面的：

```text
3.14_armv7l_fix.patch
3.14_fix_remote_debug.patch
exit code 12
```

是 RC4.7/RC4.8 自己的误报检查。
这些只是 python-for-android 仓库中的源代码补丁文件。

## RC4.9

不再扫描 `3.14_*.patch` 判断构建 Python。

固定：
- GitHub Python：3.11
- Android Python：3.11.15
- hostpython：3.11.15
- Qt/PySide6：6.11.1
- p4a：v2026.05.09
- JDK：21

并把完整 deploy 输出保存为：

```text
android-deploy.log
```

## 如果仍失败

GitHub 的红色 Build Android APK Beta 步骤末尾会自动打印：

```text
REAL ANDROID BUILD FAILURE DETECTED
Relevant error lines from android-deploy.log:
...
Last 220 lines of the complete deploy log:
...
```

同时失败诊断 Artifact 中会有：

```text
android-deploy.log
buildozer.spec
.buildozer/...
```

这时只需要提供 `REAL ANDROID BUILD FAILURE DETECTED`
后面的部分，就能看到真正 Buildozer / p4a 根因。

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
StockEventRadar-Android-Beta-1.0.0-rc4.9
```
