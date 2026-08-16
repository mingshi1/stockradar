# V1.0.0 RC4.6 Android 测试

## RC4.5 的实际状态

GitHub 已显示：

```text
Build Android APK Beta
✓ 2m41s
```

说明 `pyside6-android-deploy` 命令本身以成功状态退出。

失败的是下一步：

```text
Collect APK/AAB
```

RC4.5 使用：

```bash
find . -maxdepth 8
```

搜索 APK/AAB，搜索范围太武断。

Qt 官方说明 Android deploy 的最终产物是 APK 或 AAB；
`--keep-deployment-files` 还会保留 Buildozer / Gradle 构建目录。

## RC4.6

APK 构建结束后直接由 `build_android.sh` 搜索并归一化产物。

搜索范围：
- 项目目录
- GitHub RUNNER_TEMP
- ~/.buildozer
- ~/.pyside6-android-deploy

并且只选择本次构建开始以后生成的 APK/AAB。

成功时：

```text
Build Android APK Beta
✓

Validate collected APK/AAB
✓

Upload Android Beta
✓
```

页面底部下载：

```text
StockEventRadar-Android-Beta-1.0.0-rc4.6
```

解压后即可拿到 APK。
