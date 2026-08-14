# AI板块事件雷达 v0.6.0

V0.6 正式进入 Multi-AI 阶段。

## 核心变化

- DeepSeek
- OpenAI
- Qwen
- GLM
- Kimi
- 同一份联网证据，多模型独立分析
- 多模型并行调用
- Consensus Engine
- 平均事件评分
- 方向一致度
- 评分离散度
- 共识置信度
- 可选 Judge AI
- Provider 失败自动降级，不影响其他成功模型
- SQLite 保存每家模型的独立结果
- 保持 V0.5 自定义板块、历史报告和 Event Pool

## 为什么 Multi-AI 不能各搜各的？

如果：

```text
DeepSeek 看新闻 A
OpenAI 看新闻 B
Qwen 看新闻 C
```

最终结果不同，无法区分：

- 是模型观点不同？
- 还是输入事实根本不同？

因此 V0.6 改成：

```text
联网 Research Provider
        ↓
同一份 Evidence
        ↓
多个 AI 独立分析
        ↓
Consensus Engine
```

这样差异才真正来自模型判断。

## Research Provider

当前允许：

```text
DeepSeek
OpenAI
```

默认：

```text
DeepSeek
```

研究模型负责：

```text
联网搜索
→ 来源
→ 日期
→ 新闻
→ 事件逻辑证据
```

其他 AI 不重新搜索，直接分析这份共享证据。

## 分析模式

### 单模型快速

```text
Research Provider
↓
自己分析
↓
结果
```

适合快速测试、控制成本。

### 多模型交叉验证

所有启用且配置了 API Key 的 Provider 会并行分析：

```text
DeepSeek
OpenAI
Qwen
GLM
Kimi
```

某一家失败时，不会让整次任务直接失败；
只要至少一个分析模型成功，就能继续生成报告。

## Consensus Engine

V0.6 的最终分数不是某个 Judge AI 随意决定。

例如：

```text
DeepSeek   +72
OpenAI     +61
Qwen       +69
GLM        +55
Kimi       +66
```

系统会计算：

- score 均值
- score 离散度
- 正 / 中 / 负方向桶
- 方向一致度
- 模型平均置信度
- 共识置信度

最后产生透明的共识结果。

## Judge AI

可选开启：

```text
AI 设置
→ 启用 Judge AI
```

Judge 只能：

- 总结共识
- 总结分歧
- 解释为什么评分不同

Judge 不允许覆盖：

- 平均 score
- agreement
- dispersion
- consensus confidence

这样避免“最后一个 AI 一票否决前面全部模型”。

## 数据库

V0.6 在 V0.5 的 SQLite 上新增：

```text
provider_results
```

一条历史分析可能对应：

```text
analysis_run #23

provider_results
├── DeepSeek
├── OpenAI
├── Qwen
├── GLM
└── Kimi
```

方便以后做：

- 模型长期准确性比较
- 某模型偏乐观/偏悲观统计
- 成本统计
- 模型权重学习

## 安装依赖

仍然只需要：

```powershell
python -m pip install -r requirements.txt
```

V0.6 没有要求安装：

```text
dashscope
zhipuai
kimi SDK
```

因为这些平台都通过 OpenAI-compatible API 接入。

## API 申请与配置

详见：

```text
API_SETUP.md
```

## 推荐第一次测试

1. 保留现有 DeepSeek。
2. 再申请 Qwen 或 GLM 中任意一个 API Key。
3. AI 设置里启用 DeepSeek + 第二个 Provider。
4. 分析模式选择 `多模型交叉验证`。
5. Judge 暂时关闭。
6. 首页只分析 `黄金 + 生物医药`。
7. 查看报告里的“各模型独立判断”和“方向一致度”。
8. 测试通过后再继续增加 Kimi / OpenAI。

## V0.7 计划

下一版重点转向报告产品化：

- 报告中心
- 30秒摘要
- 标准报告
- 深度报告
- Markdown 导出
- HTML 导出
- PDF 导出
- PNG 长图
- Multi-AI 共识报告
- Token / API 调用成本记录
