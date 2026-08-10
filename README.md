# 抖音自动续火花 - GitHub Actions 配置教程

本 README 只介绍如何使用 **GitHub Actions** 运行本项目。

配置完成后，不需要自己的服务器或电脑长期在线，GitHub Actions 会按设定时间自动运行脚本。

> [!WARNING]
> 本项目通过浏览器自动化操作抖音网页版。请遵守抖音平台规则，并自行承担登录失效、安全验证、页面改版等风险。
>
> `DOUYIN_COOKIE` 相当于你的抖音登录凭证，**绝对不要提交到仓库、Issue、日志或发送给其他人**。

---

## 一、Fork 项目

点击仓库右上角的 **Fork**，把项目 Fork 到自己的 GitHub 账号。

后面的 Secrets、Actions 和定时任务，都需要在你自己的 Fork 仓库中配置。

Fork 完成后进入自己的仓库，例如：

```text
https://github.com/你的用户名/douyin-auto-fire
```

然后打开顶部的 **Actions**。

如果 GitHub 提示需要启用工作流，点击：

```text
I understand my workflows, go ahead and enable them
```

---

## 二、获取抖音 Cookie

GitHub Actions 使用 `DOUYIN_COOKIE` 登录抖音。

### 1. 浏览器登录抖音

先在电脑浏览器中正常登录抖音网页版，并确认能够正常打开私信页面。

### 2. 导出 Cookie

可以使用 Cookie-Editor 一类的浏览器 Cookie 导出工具。

在已经登录抖音的页面中：

1. 打开 Cookie 导出工具；
2. 选择导出 Cookie；
3. 选择 **JSON** 格式；
4. 复制完整的 JSON 数组。

格式大致如下：

```json
[
  {
    "name": "example_cookie",
    "value": "example_value",
    "domain": ".douyin.com",
    "path": "/"
  }
]
```

注意：

- 必须复制完整的 `[ ... ]` JSON 数组；
- 不要只复制某一个 Cookie；
- 不要把 Cookie 写进仓库文件；
- 不要把 Cookie 发给别人。

当前 GitHub Actions 工作流使用的是：

```text
DOUYIN_COOKIE
```

而不是 `DOUYIN_STORAGE_STATE`。

---

## 三、准备发送配置

GitHub Actions 使用 `DOUYIN_CONFIG` 保存发送配置。

第一次测试强烈建议只配置：

- 1 个好友；
- 1 条普通文字消息。

例如：

```json
{
  "friends": ["测试好友昵称"],
  "messages": [
    {
      "type": "text",
      "value": "今天也要记得续火花呀 ✨"
    }
  ],
  "send_interval_seconds": {
    "min": 3,
    "max": 8
  },
  "prevent_duplicates": false
}
```

把：

```text
测试好友昵称
```

改成你真实的抖音好友昵称。

好友名称并不是稳定的唯一账号 ID，存在重名或部分匹配的可能，所以第一次不要直接加入很多好友。

### 多个好友示例

确认单好友测试没有问题后，可以改成：

```json
{
  "friends": [
    "好友A",
    "好友B",
    "好友C"
  ],
  "messages": [
    {
      "type": "text",
      "value": "续火花 ✨"
    }
  ],
  "send_interval_seconds": {
    "min": 3,
    "max": 8
  },
  "prevent_duplicates": false
}
```

`friends` 中的好友会按顺序处理。

---

## 四、配置 GitHub Secrets

进入你 Fork 后的仓库：

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

至少需要配置下面两个 Secret：

| Secret 名称 | 填写内容 | 是否必需 |
| --- | --- | --- |
| `DOUYIN_COOKIE` | 抖音 Cookie 的完整 JSON 数组 | 必需 |
| `DOUYIN_CONFIG` | 完整发送配置 JSON | 必需 |
| `DINGTALK_WEBHOOK` | 钉钉机器人 Webhook | 可选 |
| `DINGTALK_SECRET` | 钉钉机器人加签 Secret | 可选 |

如果不需要钉钉通知，只配置前两个即可。

如果需要钉钉通知，`DINGTALK_WEBHOOK` 和 `DINGTALK_SECRET` 必须同时配置。

### Secret 1：DOUYIN_COOKIE

点击：

```text
New repository secret
```

Name 填：

```text
DOUYIN_COOKIE
```

Secret 粘贴刚才导出的完整 Cookie JSON。

然后点击 **Add secret**。

### Secret 2：DOUYIN_CONFIG

再次点击：

```text
New repository secret
```

Name 填：

```text
DOUYIN_CONFIG
```

Secret 粘贴完整配置 JSON，例如：

```json
{
  "friends": ["测试好友昵称"],
  "messages": [
    {
      "type": "text",
      "value": "续火花 ✨"
    }
  ]
}
```

然后点击 **Add secret**。

> GitHub Secret 保存后不会再次完整显示内容。如果 Cookie 或配置需要修改，直接进入对应 Secret 重新更新即可。

---

## 五、第一次运行：先执行 Dry Run

Secrets 配置完成后，**不要马上正式发送**。

先进入：

```text
Actions
→ Send Douyin Messages
→ Run workflow
```

将：

```text
dry_run
```

设置为：

```text
true
```

然后点击绿色的：

```text
Run workflow
```

### Dry Run 会做什么？

Dry Run 会检查：

- Cookie 是否还能正常登录；
- 是否能够进入抖音私信页面；
- 是否能够找到配置中的好友。

Dry Run **不会发送消息**。

运行完成后：

- 绿色 `✓`：任务执行成功；
- 红色 `✗`：任务执行失败。

如果失败，点击本次 Workflow Run，再点击 `send` Job 查看具体日志。

---

## 六、进行一次真实发送测试

Dry Run 成功后，建议仍然只保留 **1 个测试好友**。

再次进入：

```text
Actions
→ Send Douyin Messages
→ Run workflow
```

这次把：

```text
dry_run
```

设置为：

```text
false
```

然后运行。

这次会执行真实发送。

确认：

1. 找到的是正确好友；
2. 消息内容正确；
3. 对方确实收到消息；

全部没有问题以后，再把其他好友加入 `DOUYIN_CONFIG`。

> [!CAUTION]
> 手动运行时，只有 `dry_run = true` 才不会发送消息。
>
> `dry_run = false` 会直接执行真实发送。

---

## 七、配置每天自动运行时间

GitHub Actions 工作流文件位于：

```text
.github/workflows/send.yml
```

当前仓库配置为：

```yaml
schedule:
  - cron: "0 0 * * *"
    timezone: "Asia/Shanghai"
```

表示：

```text
每天北京时间 00:00 自动运行
```

定时任务触发时会直接执行真实发送，不会先执行 Dry Run。

### 改成每天北京时间 08:00

把它修改成：

```yaml
schedule:
  - cron: "0 8 * * *"
    timezone: "Asia/Shanghai"
```

### 改成每天北京时间 09:30

```yaml
schedule:
  - cron: "30 9 * * *"
    timezone: "Asia/Shanghai"
```

### 改成每天北京时间 23:50

```yaml
schedule:
  - cron: "50 23 * * *"
    timezone: "Asia/Shanghai"
```

Cron 格式为：

```text
分钟 小时 日期 月份 星期
```

例如：

```text
30 9 * * *
```

就是每天 `09:30`。

因为已经指定：

```yaml
timezone: "Asia/Shanghai"
```

所以这里的小时可以直接按北京时间填写。

修改 `.github/workflows/send.yml` 后，提交更改，新时间才会生效。

---

## 八、如何修改好友或消息

不需要修改仓库里的 `config.json`。

直接进入：

```text
Settings
→ Secrets and variables
→ Actions
→ Repository secrets
→ DOUYIN_CONFIG
```

点击更新，把新的完整 JSON 配置粘贴进去即可。

例如增加好友：

```json
{
  "friends": [
    "好友A",
    "好友B"
  ],
  "messages": [
    {
      "type": "text",
      "value": "续火花 ✨"
    }
  ]
}
```

修改 `DOUYIN_CONFIG` 后，建议先再次手动执行一次：

```text
dry_run = true
```

确认好友定位没有问题，再等待定时任务正式运行。

---

## 九、Cookie 失效后如何更新

如果 Actions 日志出现类似：

```text
抖音登录状态已失效
```

或者：

```text
未检测到抖音私信页面
```

或者抖音要求安全验证，就重新获取 Cookie。

步骤：

1. 在电脑浏览器重新登录抖音；
2. 确认抖音网页版和私信页面可以正常打开；
3. 重新导出 Cookie JSON；
4. 进入 GitHub 仓库 `Settings`；
5. 打开 `Secrets and variables` → `Actions`；
6. 更新 `DOUYIN_COOKIE`；
7. 手动执行一次 `dry_run = true`。

GitHub Actions 不会自动扫码登录，也不会绕过验证码或抖音安全验证。

---

## 十、查看 Actions 运行日志

进入：

```text
Actions
→ Send Douyin Messages
```

可以看到所有运行记录。

点击某一次运行，再点击：

```text
send
```

即可查看：

- 安装 Python；
- 安装 Playwright；
- 写入配置；
- 运行脚本；
- 错误日志。

如果任务失败，优先查看 `Run` 这一步的报错。

---

## 十一、下载失败诊断文件

工作流执行失败时，会自动上传 `artifacts/` 目录。

在失败的 Workflow Run 页面底部，可以看到类似：

```text
douyin-failure-123456789
```

下载后可能包含：

```text
artifacts/
├── run.log
├── result.json
├── screenshots/
└── traces/
```

失败诊断 Artifact 当前保留 **3 天**。

> [!WARNING]
> 日志、截图和 trace 可能包含好友昵称、聊天页面或其他隐私内容，请不要公开上传或分享。

---

## 十二、可选：配置钉钉通知

如果你不需要钉钉通知，可以跳过这一节。

如果需要，请在 GitHub Secrets 中同时添加：

```text
DINGTALK_WEBHOOK
```

和：

```text
DINGTALK_SECRET
```

这两个必须同时存在，只配置其中一个会导致配置错误。

---

## 十三、常见问题

### 1. Actions 页面没有 Run workflow

确认：

- workflow 已启用；
- `.github/workflows/send.yml` 位于默认分支；
- 当前打开的是 `Send Douyin Messages` 工作流。

然后刷新 Actions 页面。

### 2. 提示 Cookie JSON 错误

`DOUYIN_COOKIE` 必须是完整 JSON 数组：

```json
[
  {
    "name": "xxx",
    "value": "xxx",
    "domain": ".douyin.com"
  }
]
```

不要粘贴成普通的：

```text
name=value; name2=value2
```

### 3. 提示 DOUYIN_CONFIG 不是有效 JSON

检查：

- 是否漏了逗号；
- 是否用了中文引号；
- 是否多写了注释；
- 是否漏了 `{}`、`[]`；
- Secret 中是否粘贴了 Markdown 的 ```json 代码块标记。

`DOUYIN_CONFIG` 中只需要保存纯 JSON 内容。

### 4. Dry Run 成功，但是定时任务没有立即运行

Dry Run 是手动触发。

定时运行由 `.github/workflows/send.yml` 中的 `schedule` 决定，两者互不影响。

### 5. 为什么定时任务时间到了没有精确到秒运行？

GitHub Actions 的 schedule 属于定时调度任务，在平台繁忙时可能出现一定延迟，因此不适合要求秒级准时的任务。

### 6. 为什么重新 Fork 后 Secrets 没了？

Secrets 不会跟随仓库代码一起复制。每个 Fork 都需要自己重新配置：

```text
DOUYIN_COOKIE
DOUYIN_CONFIG
```

### 7. `prevent_duplicates` 能防止 GitHub Actions 多次运行重复发送吗？

不要依赖它做跨 Workflow Run 的防重复。

当前工作流每次使用新的 GitHub-hosted runner，也没有恢复上一次运行生成的 `history.json`。因此最重要的是：**同一个账号只保留一个正式定时任务，不要同时在多处调度。**

---

## 十四、推荐的首次配置顺序

建议严格按照下面顺序操作：

```text
1. Fork 仓库
        ↓
2. 启用 GitHub Actions
        ↓
3. 浏览器登录抖音
        ↓
4. 导出 Cookie JSON
        ↓
5. 添加 DOUYIN_COOKIE
        ↓
6. 添加 DOUYIN_CONFIG
        ↓
7. 只配置 1 个测试好友
        ↓
8. 手动运行 dry_run = true
        ↓
9. 手动运行 dry_run = false 测试一次真实发送
        ↓
10. 确认无误后增加其他好友
        ↓
11. 设置需要的定时时间
        ↓
12. 之后交给 GitHub Actions 自动运行
```

---

## 安全提醒

- 不要把 `DOUYIN_COOKIE` 写进 README、代码或 Issue；
- 不要把 Cookie 提交到 Git；
- 不要公开 Actions 失败截图和 trace；
- 修改好友或消息以后，建议重新 Dry Run；
- Cookie 失效后需要重新登录并更新 Secret；
- 抖音页面结构发生变化后，自动化选择器可能失效；
- GitHub-hosted runner 的网络环境可能触发抖音安全验证；
- 同一个账号不要同时启用多个正式调度器，以免重复发送。

配置完成后，日常只需要关注 GitHub Actions 是否运行成功，以及抖音 Cookie 是否仍然有效。