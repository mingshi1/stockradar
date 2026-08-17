# V1.0.0 RC4.26

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
