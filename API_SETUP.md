# V0.8 API 配置指南

V0.8 移除了 OpenAI，聚焦国内网络环境下更容易使用的模型。

当前支持：

1. DeepSeek
2. Qwen / 阿里云百炼
3. GLM / 智谱
4. Kimi / Moonshot
5. Doubao / 火山方舟
6. MiniMax

你不需要一次申请全部 API Key。

---

## 推荐组合

### 最低 Multi-AI

```text
DeepSeek
+
任意另一家
```

### 推荐国内组合

```text
DeepSeek
Qwen
GLM
Doubao
MiniMax
```

Kimi 可按需要再开启。

模型越多，API 成本越高。建议先用 2~3 个模型测试。

---

# 1. DeepSeek

官方平台：

```text
https://platform.deepseek.com/
```

软件默认：

```text
Base URL
https://api.deepseek.com

Model
deepseek-v4-flash
```

DeepSeek 可以作为联网 Research Provider。

---

# 2. Qwen / 阿里云百炼

官方控制台：

```text
https://bailian.console.aliyun.com/
```

创建 API Key 后，请注意：

不同地域、业务空间和计费模式可能对应不同 Base URL。

V0.8 提供的默认兼容地址：

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

如果控制台创建 API Key 时给出了专属 API Host，
请优先把控制台地址复制到软件：

```text
AI 设置
→ Qwen
→ Base URL
```

模型输入框可编辑。

---

# 3. GLM / 智谱

官方开放平台：

```text
https://open.bigmodel.cn/
```

创建 API Key 后在：

```text
AI 设置 → GLM
```

配置。

默认 Base URL：

```text
https://open.bigmodel.cn/api/paas/v4
```

模型输入框可编辑。

---

# 4. Kimi / Moonshot

官方开放平台：

```text
https://platform.moonshot.cn/
```

默认：

```text
Base URL
https://api.moonshot.cn/v1
```

模型输入框可编辑。

---

# 5. Doubao / 火山方舟

火山方舟：

```text
https://console.volcengine.com/ark/
```

进入：

```text
API Key 管理
```

创建 ARK API Key。

V0.8 默认：

```text
Base URL
https://ark.cn-beijing.volces.com/api/v3

Model
doubao-seed-2-0-lite-260215
```

重要：

火山方舟模型更新很快，而且你的账号实际可调用模型
与控制台开通情况有关。

因此推荐：

```text
火山方舟
→ 模型 / API 接入
→ 复制准确 Model ID
→ AI 设置 → Doubao → 模型
```

V0.8 模型输入框允许手动编辑。

软件还预置了以下便于尝试的名称：

```text
doubao-seed-evolving
doubao-seed-2-1-pro
doubao-seed-2-1-turbo
```

如果其中某个名称测试失败，请以你方舟控制台显示的准确 Model ID 为准。

Doubao 可以作为联网 Research Provider。

---

# 6. MiniMax

中国开放平台：

```text
https://platform.minimaxi.com/
```

在：

```text
账户管理 → 接口密钥
```

创建 API Key。

V0.8 使用中国区 OpenAI-compatible 地址：

```text
https://api.minimaxi.com/v1
```

默认模型：

```text
MiniMax-M2.7
```

预置：

```text
MiniMax-M2.7
MiniMax-M2.7-highspeed
MiniMax-M2.5
MiniMax-M2.5-highspeed
MiniMax-M2.1
```

MiniMax 在 V0.8 参与独立分析 / Judge，
暂不作为联网 Research Provider。

---

# API Key 安全

每一家 API Key 都通过：

```text
keyring
```

单独存入操作系统凭据管理器。

例如：

```text
StockEventRadar
├── DeepSeek_api_key
├── Qwen_api_key
├── GLM_api_key
├── Kimi_api_key
├── Doubao_api_key
└── MiniMax_api_key
```

Key 不写进 GitHub，也不会明文写进 settings.json。

---

# 推荐第一次测试

建议先：

```text
Research Provider
DeepSeek

分析模式
多模型交叉验证

Judge
关闭
```

启用：

```text
DeepSeek
+
Doubao
+
MiniMax
```

只分析：

```text
黄金
+
生物医药
```

测试成功以后，再加入：

```text
Qwen
GLM
Kimi
```

最后再尝试开启 Judge。


---

# V0.8 Token 单价设置

V0.8 会记录 Provider 返回的 Token usage。

软件没有内置固定官方价格，因为价格可能随：

- 模型版本
- 上下文缓存
- 套餐
- 地域
- 活动
- 计费政策

发生变化。

请进入各 Provider 官方控制台查看你自己的实际计费价格，然后在：

```text
AI 设置
→ 对应 Provider
→ 输入单价 / 1M tokens
→ 输出单价 / 1M tokens
```

自行填写。

如果不想使用成本估算，保持：

```text
0
```

即可。

软件会继续记录 Token，但成本显示为未配置。
