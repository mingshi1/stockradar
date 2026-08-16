# V1.0.0 RC4.11 Android 实机启动测试

## RC4.10 已完成的里程碑

APK 已成功生成、下载并安装到荣耀手机。

当前问题：

```text
点击 App 图标
→ 立即闪退
```

## 已发现的高概率启动问题

应用原先在启动 import 阶段执行：

```python
from openai import OpenAI
```

但 Android p4a distribution 并未包含 desktop `openai` SDK。

因此可能在主窗口创建之前发生：

```text
ModuleNotFoundError: openai
```

用户侧表现就是直接闪退。

## RC4.11

Android 不再依赖 desktop OpenAI SDK。

Android 网络调用改为 Python 标准库：

```text
urllib.request
```

支持当前应用用到的：

```text
/chat/completions
/responses
```

Windows 桌面版本仍继续使用原来的 OpenAI-compatible SDK，
不改变 Windows 工作方式。

## 首轮手机测试

安装：

```text
StockEventRadar-*-arm64-v8a-debug.apk
```

测试顺序：

1. 点击图标。
2. 看是否进入首次启动向导。
3. 如果弹出“AI板块事件雷达启动失败”，截图完整提示。
4. 如果仍然完全无提示闪退，下一步使用 Android `adb logcat`
   获取 native/Qt 层崩溃。
5. 如果能进入 UI：
   - 先切换页面
   - 打开 AI 设置
   - 输入一个 API Key
   - 测试连接
   - 再测试单模型单板块分析

## 注意

Windows 自动任务仍然是 Windows Task Scheduler 功能。
Android RC4.11 首轮重点是：
- 稳定启动
- UI
- AI API 请求
- 历史与报告

Android 后台定时任务暂不在本轮测试范围。
