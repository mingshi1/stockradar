# V1.0.0 RC4.16 Android 真机测试

RC4.15 ADB 日志已经确认：

```text
Runtime platform: android=True
Fatal signal 11 (SIGSEGV)
thread: qtMainLoopThread
```

native stack 的关键路径：

```text
libshiboken6
Shiboken::Errors::storePythonOverrideErrorOrPrint
QWidget::event
QGuiApplicationPrivate::processGeometryChangeEvent
QWidget::show / setVisible
```

应用唯一的 QWidget 事件 override 是 MainWindow.resizeEvent。
此前 MainWindow 在 `_build_ui()` 前先 `resize(1360, 880)`，
Android 可以立即派发 resize/geometry 事件，使响应式布局访问尚未创建的控件。

RC4.16 修复顺序：

```text
_ui_ready = False
_build_ui()
_connect_signals()
refresh data
_ui_ready = True
_apply_responsive_layout()
show()
```

测试：
1. 卸载旧版。
2. 安装单一 APK `StockEventRadar-Android-arm64-v8a-debug.apk`。
3. 打开首次设置页。
4. Key 可填可不填。
5. 点“进入主界面”。
6. 应正常进入今日分析，不再闪退。
7. 再进入 AI 设置测试 Provider。

若仍闪退，再抓一次 logcat。RC4.16 会额外打印：
- MainWindow stage: constructing
- MainWindow stage: constructed
- MainWindow stage: shown
