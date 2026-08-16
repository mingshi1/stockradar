# V1.0.0 RC4.10 Android 测试

## 已定位的真实 Buildozer 根因

完整 `android-deploy.log`：

```text
RAN: .../libffi/autogen.sh

configure.ac:215:
error: possibly undefined macro: LT_SYS_SYMBOL_USCORE

autoreconf:
error: /usr/bin/autoconf failed with exit status: 1
```

因此失败发生在：

```text
python-for-android
→ libffi recipe
→ autogen.sh
→ autoreconf
→ autoconf
```

## 最新 prerequisite 截图里的 exit code 4

依赖安装已经完成。

真正导致该 GitHub step 红色的是：

```bash
libtoolize --version | head -1
```

配合：

```bash
set -euo pipefail
```

`head` 提前关闭 stdout 后，producer 收到 Broken pipe，
使验证步骤错误退出。

RC4.10 删除这种写法，直接执行：

```bash
autoconf --version
automake --version
aclocal --version
libtoolize --version
cmake --version
pkg-config --version
```

## 本轮重点观察

首先应该看到：

```text
Install Android native build prerequisites
✓
```

然后：

```text
Setup Python 3.11
✓
...
Build Android APK Beta
```

在 Build Android 日志中重点观察 libffi：

之前：

```text
LT_SYS_SYMBOL_USCORE
autoreconf ... exit status 1
```

RC4.10 目标是跨过这一段。

## 如果仍失败

RC4.9 起已经保存：

```text
android-deploy.log
```

失败后继续下载 diagnostics Artifact 即可，
不需要再复制整个 GitHub 页面。

## 成功目标

```text
Build Android APK Beta
✓
Validate collected APK/AAB
✓
Upload Android Beta
✓
```

Artifact：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.10
```
