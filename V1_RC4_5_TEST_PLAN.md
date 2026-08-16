# V1.0.0 RC4.5 Android 测试

## RC4.4 的错误不是应用代码错误

错误文件：

```text
pyside-setup/sources/pyside-tools/deploy_lib/android/recipes/
PySide6/__init__.tmpl.py
```

这个文件属于 Qt for Python 自己的源码，不属于 StockEventRadar。

`pyside6-android-deploy` 默认将 `main.py` 的父目录视为 project_dir，
并扫描其中 Python 文件以识别 Qt 模块。

RC4.4 把 `pyside-setup` clone 到：

```text
stockradar/pyside-setup
```

因此部署扫描误入 Qt 自己的源码模板。

## RC4.5 修复

Qt tools 改为：

```text
$RUNNER_TEMP/pyside-setup
```

它位于应用项目目录之外。

同时 Android deploy 增加：

```text
--extra-ignore-dirs=
android-wheels,
android-output,
deployment,
dist,
installer,
.git,
.github
```

## 预期

GitHub Actions 应通过：

```text
Verify app project is clean before deploy
✓

Build Android APK Beta
```

如果 Build Android APK Beta 成功：

```text
Collect APK/AAB
✓
Upload Android Beta
✓
```

然后下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.5
```

解压得到 `.apk`。
