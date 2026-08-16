# V1.0.0 RC4.15 Android 测试

## 根因

RC4.14 手机测试：

```text
No module named 'openai'
```

原因：

```python
def is_android():
    return sys.platform == "android"
```

但当前 APK 使用 Python 3.11。

Python 3.11 在 Android 上可能仍然：

```text
sys.platform == "linux"
```

所以软件误走 Desktop 分支：

```text
Desktop OpenAI SDK
↓
from openai import OpenAI
↓
APK 没有 openai
↓
ModuleNotFoundError
```

## RC4.15

Android 判断改为优先检测：

```python
hasattr(sys, "getandroidapilevel")
```

并保留 Android/p4a 环境变量 fallback。

## 这会同时修复两个现象

### AI
测试 Provider 时应该进入：

```text
AndroidOpenAICompat
```

不应再出现：

```text
No module named 'openai'
```

### UI
RC4.14 已写好的 Android 布局这次才会真正激活：
- AI 设置纵向布局
- Android 小字号
- 移动端下拉框样式
- Android 首次启动单页界面

## 手机测试顺序

1. 最好卸载旧 RC4.14。
2. 安装 RC4.15。
3. 进入 AI 设置。
4. 填写一个 Provider API Key。
5. 点“测试此 Provider”。

成功时应该显示 API 返回结果 / 连接成功。

如果出现新的网络错误，例如：

```text
CERTIFICATE_VERIFY_FAILED
SSL
Connection refused
timed out
HTTP 401
HTTP 404
```

请直接截图。

这些错误和 `No module named openai` 已经属于下一层，
届时可以根据实际 HTTP/SSL 错误继续处理。

## APK

仍然只有一个：

```text
StockEventRadar-Android-arm64-v8a-debug.apk
```
