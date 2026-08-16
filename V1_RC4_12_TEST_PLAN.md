# V1.0.0 RC4.12 Android 单 APK + 闪退诊断

## APK 输出

成功后 Artifact 里只会有：

```text
StockEventRadar-Android-arm64-v8a-debug.apk
```

不再上传 3 个重复 APK。

## 当前实机状态

RC4.11：
- APK 可以安装
- 点击 App 图标
- 无错误提示
- 立即闪退

这说明错误很可能发生在 Python 异常提示能够显示之前。

## 下一步：ADB Logcat

不要再根据“闪退”现象猜依赖。

手机连接电脑后，获取系统真实日志：

```powershell
adb devices
adb logcat -c
adb logcat
```

然后：
1. 保持 `adb logcat` 运行
2. 手机上点击 StockEventRadar
3. 等它闪退
4. Ctrl+C 停止日志

更方便的保存方式：

```powershell
adb logcat -c
adb logcat > stockradar-crash.txt
```

点击 App 触发闪退后 Ctrl+C。

重点关键词：
- FATAL EXCEPTION
- AndroidRuntime
- Qt
- Python
- PySide6
- UnsatisfiedLinkError
- dlopen failed
- SIGSEGV
- abort
- ModuleNotFoundError

把 `stockradar-crash.txt` 上传给开发者即可。

## 测试目标

第一目标不再是继续改代码，
而是拿到荣耀手机真实崩溃栈。
