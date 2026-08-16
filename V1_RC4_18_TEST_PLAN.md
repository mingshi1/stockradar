# V1.0.0 RC4.18

## GitHub Actions

RC4.17 失败在：

```text
Pin Qt Android deploy to stable p4a and cp311
PySide6 buildozer.py requirements line did not match ...
```

RC4.18 改为 AST 结构化补丁。

预期：
```text
Configure Qt Android deploy for cp311      ✓
Verify official Android wheel URLs         ✓
Download official Android ARM64 wheels     ✓
Build Android APK Beta                     ✓
Validate single Android APK                ✓
Upload Android Beta                        ✓
```

最终仍只有：
```text
StockEventRadar-Android-arm64-v8a-debug.apk
```

## 手机 AI 设置

只显示：
```text
启用
模型
API Key
连接状态
测试此 Provider
```

不显示 Base URL 和成本单价。

## DeepSeek TLS

RC4.17 出现 CERTIFICATE_VERIFY_FAILED。
RC4.18 打包 CA bundle，并保持证书验证。

若仍出现 TLS 证书链错误：
- 关闭 HTTPS 抓包/代理
- 临时关闭 VPN
- 换手机移动数据或普通家用 Wi-Fi
