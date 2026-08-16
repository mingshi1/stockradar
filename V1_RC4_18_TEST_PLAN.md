# V1.0.0 RC4.18 Android 测试

## 本轮两个目标

### 1. 修复 AI HTTPS 证书

RC4.17 DeepSeek 测试出现：

```text
SSL: CERTIFICATE_VERIFY_FAILED
self-signed certificate in certificate chain
```

RC4.18 Android APK 打包：

```text
certifi==2026.7.22
```

HTTPS client 显式使用 Mozilla CA bundle。

没有关闭证书验证。

### 2. 简化手机 AI 设置

Android Provider 页只显示：

```text
☑ 参与多模型独立分析

模型
[ DeepSeek 模型 ▼ ]

API Key
[ *************** ]

状态

[ 测试此 Provider ]
```

以下项目 Android 不再显示：

```text
Base URL
输入单价
输出单价
成本说明
Provider 长说明
```

Base URL 自动使用软件内该 Provider 的官方默认地址。

Android 成本单价统一按 0 保存，不做成本估算。

Windows 仍保留完整成本设置。

## DeepSeek 测试

1. 卸载旧版或覆盖安装 RC4.18。
2. AI 设置 → DeepSeek。
3. 模型选择 `deepseek-v4-flash`。
4. 输入 API Key。
5. 点“测试此 Provider”。

### 预期成功

```text
✓ API 连接成功
```

### 如果仍是 TLS 证书错误

RC4.18 已使用 Mozilla CA。

此时优先检查：
- 手机 VPN
- HTTP/HTTPS 抓包软件
- 广告过滤/安全软件的 HTTPS 扫描
- 公司/校园 Wi-Fi 的 HTTPS 中间证书

可关闭 Wi-Fi，直接用 5G 再测试一次。

不要关闭 SSL 证书验证。

## APK

仍然只有：

```text
StockEventRadar-Android-arm64-v8a-debug.apk
```
