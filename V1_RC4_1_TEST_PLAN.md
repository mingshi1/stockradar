# V1.0.0 RC4.1 Android Hotfix 测试

RC4 Android workflow 的 exit code 22 来自 `curl --fail` 的 HTTP 下载失败。

RC4 中 PySide6 Android wheel URL 的文件名大小写写成了 `PySide6-...whl`，
Qt 官方目录实际是小写 `pyside6-...whl`。RC4.1 已修正。

Push 后进入 GitHub Actions → Android Beta Build。

成功时应依次通过：
1. Checkout
2. Setup Python 3.11
3. Install build environment
4. Verify official Android wheel URLs
5. Download official Android ARM64 wheels
6. Download matching Android SDK and NDK
7. Build Android APK Beta
8. Collect APK/AAB
9. Upload Android Beta

成功后在 workflow 页面底部下载：
`StockEventRadar-Android-Beta-1.0.0-rc4.1`

解压后应有 `.apk`。
