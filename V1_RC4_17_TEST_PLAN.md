# V1.0.0 RC4.17 Android 稳定性测试

## RC4.16 日志结论

仍然是：

```text
Fatal signal 11 (SIGSEGV)
qtMainLoopThread
```

native stack：

```text
libshiboken6
Shiboken::Errors::storePythonOverrideErrorOrPrint
PySide6 QtWidgets
QWidget::event
QGuiApplicationPrivate::processGeometryChangeEvent
QPlatformWindow::setVisible
```

所以本轮不再只修改 resizeEvent 的内部逻辑，
而是从 Android 路径移除应用自己的 QWidget virtual overrides。

## RC4.17 变化

Android：
- MainWindow 无 resizeEvent override
- TrendChart 无 paintEvent override
- MobileFirstRunDialog 无 accept override
- MainWindow 进入 app.exec() 后再异步 show
- show 后 120ms 再做移动布局

Desktop：
- 趋势图仍保留原绘图
- 响应式布局改为 350ms QTimer 检查宽度
- 不再依赖 QWidget.resizeEvent override

## 测试

建议：
1. 卸载旧版本。
2. 安装 RC4.17 单 APK。
3. 打开 App。
4. 如果首次设置出现，直接点“进入主界面”即可。
5. 如果进入今日分析：
   - 切换顶部菜单
   - 进入 AI 设置
   - 测试 Provider
6. 如果还闪退，再抓 logcat。

RC4.17 的 logcat 应明确出现：

```text
[StockEventRadar] Runtime platform: ...
[StockEventRadar] MainWindow stage: constructing
[StockEventRadar] MainWindow stage: constructed
[StockEventRadar] MainWindow stage: showing
[StockEventRadar] MainWindow stage: shown
```

同时 AppData 中会保存：

```text
startup_stage.log
```

这样下一次可以精确知道崩溃发生在哪个阶段。

## APK

仍然只有：

```text
StockEventRadar-Android-arm64-v8a-debug.apk
```
