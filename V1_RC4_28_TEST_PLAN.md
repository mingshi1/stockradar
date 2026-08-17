# V1.0.0 RC4.28

## 自动任务保存

点击“保存任务”后，应出现：

```text
正在保存任务…
```

然后必须进入以下两种结果之一：

### 正常

```text
✓ 任务 #N 已保存到本机。当前状态：已启用。
```

并且任务列表立即出现该任务。

### 保存成功但列表刷新异常

```text
✓ 任务 #N 已保存到本机；
列表刷新失败，请点“刷新”或切换页面后再看。
```

不允许永远停在：

```text
正在保存任务…
```

## 更新已有任务

保存成功后修改名称或时间，再次点保存。

应更新同一个 task_id，不创建重复记录。

## CI

Android Actions 新增：

```text
Test scheduled task SQLite save
```

应输出：

```text
Scheduled task SQLite save/update test: OK
```

## RC4.28 流式网络回归

- Android：DeepSeek 联网研究持续超过 7 分钟时，不应再出现约 903 秒的整单双重重试。
- Windows：DeepSeek 联网研究使用 Responses SSE，不再按旧的 180 秒整单等待模式处理。
- Android / Windows：DeepSeek、GLM、Qwen、Kimi、MiniMax 独立分析与 Judge 使用 Chat Completions SSE。
- 流式请求中途断开后，不自动从头重复执行整单长请求。
- 联网研究只有收到 `response.completed` 才视为成功。

## RC4.28 Android SSE EOF 回归

- Responses SSE：最终 `response.completed` 后即使直接 EOF、没有额外空行，也必须成功结束。
- Chat Completions SSE：最终 `data: [DONE]` 后即使直接 EOF、没有额外空行，也必须成功结束。
- 真正提前 EOF 时，错误信息应包含已收到事件数和最后事件类型。
