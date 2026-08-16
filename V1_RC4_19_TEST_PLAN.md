# V1.0.0 RC4.19 Android Key 诊断测试

已知正确 DeepSeek Key 的安全特征：

```text
length      = 35
fingerprint = cfb793fc4a63
last4       = 5db9
```

## 推荐测试方式

1. 在 DeepSeek 控制台复制当前有效 Key。
2. 手机打开 StockEventRadar → AI 设置 → DeepSeek。
3. 不要先唤起键盘，直接点击：

```text
从剪贴板粘贴 Key
```

4. 输入框下方应该显示类似：

```text
Key检测：35字符 · 指纹 cfb793fc4a63 · 末尾 5db9 · ASCII
```

5. 点击：

```text
测试此 Provider
```

## 判断

### A. 指纹就是：

```text
35 / cfb793fc4a63 / 5db9
```

但仍 401：

说明手机输入没有改 Key，继续看错误弹窗里的：

```text
Worker Key诊断
Key诊断
```

如果它们仍全部一致，则问题已经缩小到 Android urllib / HTTP Header 的平台行为。

### B. 第一行指纹已经不同

说明手机剪贴板/输入过程改变了 Key。

RC4.19 会自动清理常见不可见字符；如果清理后仍不同，就重点检查复制来源。

### C. 第一行正确，Worker 不同

说明应用内部某一层改变了 Key，日志会精确定位。

## 安全说明

不会：
- 显示完整 API Key
- 把完整 API Key 写入日志
- 把完整 API Key写入数据库

只显示：
- 字符长度
- SHA-256 前 12 位
- 最后 4 位
- 是否纯 ASCII

Android Beta 仍只在当前会话内存保存 Key。
