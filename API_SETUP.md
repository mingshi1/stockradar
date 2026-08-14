# V0.6 API 配置指南

V0.6 支持五个 AI Provider：

1. DeepSeek
2. OpenAI
3. Qwen（阿里云百炼）
4. GLM（智谱开放平台）
5. Kimi（月之暗面）

你不需要一次申请全部 API Key。

## 推荐起步组合

### 最低可用

```text
DeepSeek
+
任意另一家
```

这样即可看到 Multi-AI 的独立判断与方向一致度。

### 推荐测试

```text
DeepSeek
Qwen
GLM
```

### 更完整

```text
DeepSeek
OpenAI
Qwen
GLM
Kimi
```

五家全开会增加 API 调用成本，请按需要启用。

---

# 1. DeepSeek

官方平台：

https://platform.deepseek.com/

创建 API Key 后，在软件：

```text
AI 设置 → DeepSeek
```

配置。

默认：

```text
Base URL
https://api.deepseek.com

模型
deepseek-v4-flash
```

V0.6 默认仍把 DeepSeek 作为联网 Research Provider。

---

# 2. OpenAI

官方 API 平台：

https://platform.openai.com/

在 Dashboard / API Keys 创建 API Key。

软件中：

```text
AI 设置 → OpenAI
```

默认：

```text
Base URL
https://api.openai.com/v1

模型
gpt-5-mini
```

模型输入框是可编辑的，因此以后模型名更新时可以直接输入新模型名，
不必等软件发版。

OpenAI 在 V0.6 既能参与 Multi-AI 分析，也可以选择作为联网 Research Provider。

---

# 3. Qwen / 阿里云百炼

官方控制台：

https://bailian.console.aliyun.com/

开通百炼后创建 API Key。

重要：

阿里云百炼不同地域、Workspace、按量付费 / Token Plan
可能对应不同 API Host。

创建 API Key 时，如果控制台显示了 API Host，
建议直接把该地址复制到：

```text
AI 设置 → Qwen → Base URL
```

V0.6 提供的默认兼容地址：

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

但你的控制台地址优先。

推荐模型：

```text
qwen3.7-plus
qwen3.7-max
qwen3.6-flash
qwen-plus
```

---

# 4. GLM / 智谱

官方平台：

https://open.bigmodel.cn/

登录后：

```text
个人中心 → API Keys
```

创建 API Key。

默认：

```text
Base URL
https://open.bigmodel.cn/api/paas/v4

模型
glm-4.7
```

可选：

```text
glm-5.2
glm-4.7
glm-4.7-flash
```

---

# 5. Kimi / Moonshot

官方开放平台：

https://platform.kimi.com/

在开放平台控制台创建 API Key。

默认：

```text
Base URL
https://api.moonshot.cn/v1

模型
kimi-k2.6
```

可选：

```text
kimi-k3
kimi-k2.6
kimi-k2.5
```

K3 更强但调用成本通常也更高，因此软件默认仍使用 K2.6。

---

# API Key 安全

API Key 不会写进源码或 GitHub。

程序继续使用：

```text
keyring
```

将不同 Provider 的 API Key 分别保存到操作系统凭据管理器。

普通配置，例如：

```text
模型名
Base URL
是否启用
```

保存在：

```text
%APPDATA%\StockEventRadar\settings.json
```

---

# V0.6 分析机制

不是：

```text
DeepSeek 搜自己的新闻
OpenAI 搜自己的新闻
Qwen 搜自己的新闻
```

而是：

```text
Research Provider
       ↓
同一份实时联网证据
       ↓
┌────────┬────────┬────────┬────────┬────────┐
DeepSeek OpenAI   Qwen     GLM      Kimi
独立分析 独立分析 独立分析 独立分析 独立分析
└────────┴────────┴────────┴────────┴────────┘
                       ↓
                Consensus Engine
                       ↓
         平均评分 / 方向一致度 / 离散度
                       ↓
              可选 Judge AI
                       ↓
                共识与分歧总结
```

Judge 不允许修改数学聚合出来的分数。

---

# 成本建议

开发测试阶段：

```text
只勾 1~2 个板块
+
启用 2~3 个 AI
+
Judge 先关闭
```

确认稳定后再逐渐增加模型。

这样既方便调试，也避免一次测试产生过多 API 消耗。
