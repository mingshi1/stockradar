# V1.0.0 RC4.20

## Actions 预期

先出现：

```text
Validate Android deploy patch logic
```

应看到：

```text
fixture 1: OK
fixture 2: OK
fixture 3: OK
PySide Android deploy patch self-test: OK
```

随后：

```text
Pin Qt Android deploy to stable p4a and cp311
```

应看到：

```text
requirements = python3==3.11.15,hostpython3==3.11.15,shiboken6,PySide6,certifi==2026.7.22
p4a.branch = v2026.05.09
```

然后才继续 wheel、Qt for Python、Buildozer 构建。

## APK 真机

RC4.19 的 Key 指纹诊断全部保留。

DeepSeek 已验证正确安全特征：

```text
35字符
指纹 cfb793fc4a63
末尾 5db9
ASCII
```

安装后继续：
AI 设置 → DeepSeek → 从剪贴板粘贴 Key → 查看指纹 → 测试此 Provider。
