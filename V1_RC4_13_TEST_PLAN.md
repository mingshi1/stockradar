# V1.0.0 RC4.13

## RC4.12 失败原因

GitHub 报：

```text
Invalid workflow file
.github/workflows/android-beta.yml#L307
You have an error in your yaml syntax
```

原因不是 Android 编译。

RC4.12 的：

```yaml
- name: Validate single Android APK
```

被错误地放到了 YAML 顶层，而不是：

```yaml
jobs:
  android-beta:
    steps:
      - name: Validate single Android APK
```

所以 GitHub 在 workflow 解析阶段直接拒绝执行。

## RC4.13

只修 GitHub Actions YAML，不改变已打通的 Android 编译链。

仍然只上传一个：

```text
StockEventRadar-Android-arm64-v8a-debug.apk
```

预期：

```text
Install Android native build prerequisites
✓
...
Build Android APK Beta
✓
Validate single Android APK
✓
Upload Android Beta
✓
```

之后继续手机闪退诊断。
