# 抖音自动续火花

## 项目简介

这是一个通过 Playwright 操作抖音网页版、按配置向指定好友发送续火花私信的非官方个人工具。它适合少量指定好友，不适合营销群发或大规模自动化。

使用前请遵守抖音平台规则，并自行承担自动化操作可能带来的账号风险。

## 功能

- 发送文字和 Unicode Emoji
- 发送图片
- 发送抖音原生表情
- 从候选消息中随机选择一条
- 串行处理多个好友
- 使用 `--dry-run` 检查登录状态和好友定位
- 可选的本地按日防重复
- 提供 Windows、Linux systemd 和 GitHub Actions 调度入口

图片发送目前缺少可靠的页面结果确认。抖音原生表情依赖页面选择器，属于实验性能力，页面更新后可能失效。

## 环境要求

- Windows 或 Linux
- 推荐 Python 3.11 或 3.12
- 可正常访问抖音网页版的网络环境

以下命令都在项目根目录执行，并始终使用 `.venv` 中的 Python，避免与系统 Python 混用。

## Windows 安装

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m playwright install chromium
```

## Linux 安装

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium
```

## 保存登录状态

Windows：

```powershell
.venv\Scripts\python.exe scripts\login.py
```

Linux：

```bash
.venv/bin/python scripts/login.py
```

脚本会打开抖音首页：

1. 在浏览器中完成扫码登录，并确认已经进入抖音首页。
2. 回到终端按 Enter。
3. 脚本验证登录后生成 `storage-state.json`。

> `storage-state.json` 等同账号登录凭证。不要提交到 Git、公开内容或发送给他人。

## 最小配置

先复制示例配置。

Windows：

```powershell
Copy-Item config.example.json config.json
```

Linux：

```bash
cp config.example.json config.json
```

首次运行时，将 `config.json` 缩减为一个测试好友和一条文字消息：

```json
{
  "friends": ["测试好友昵称"],
  "messages": [
    {"type": "text", "value": "今天也要记得续火花呀 ✨"}
  ]
}
```

好友名称不是稳定的唯一用户标识，请填写尽量唯一、便于人工确认的昵称。`friends` 中的所有好友会收到相同的 `messages`；如需为不同好友配置不同消息，可参考 `config/tasks.example.json` 中的 `targets` 格式。

程序默认允许重复执行和重复发送。如需启用本机按日防重复，可在配置顶层加入：

```json
{
  "prevent_duplicates": true
}
```

这是一个偏向“不重发”的本地机制：程序在真正发送前先写入 `unknown` 预留记录，因此预留后即使发送失败或结果不确定，当天也会保守跳过。防重复键包含 `task_id`、配置时区下的当天日期、好友名、消息序号和消息内容哈希；同日修改任务 ID、好友名、消息顺序或内容都可能生成新键并再次发送。启用后当天不要修改或重排任务。记录只保存在当前机器，不能跨机器协调。

## 更多消息类型

文字（可以包含 Unicode Emoji）：

```json
{"type": "text", "value": "早上好 😊"}
```

图片：

```json
{"type": "image", "value": "data/images/streak.png"}
```

使用根目录的 `config.json` 时，相对路径可按项目根目录填写；支持 PNG、JPG、JPEG、GIF 和 WEBP，文件必须在运行前存在。

抖音原生表情（将下面字段合并到上方最小配置，不是完整的 `config.json`）：

```json
{
  "messages": [
    {"type": "sticker", "value": "比心"}
  ],
  "stickers": {
    "比心": {
      "label": "比心",
      "category": "常用",
      "fallback_index": 0
    }
  }
}
```

程序优先按可访问名称查找表情；`fallback_index` 是找不到名称时的备用序号，从 `0` 开始。首次测试原生表情时请保持 `HEADLESS=false`，并观察点击的表情是否正确。

随机选择消息：

```json
{
  "type": "random",
  "choices": [
    {"type": "text", "value": "早上好"},
    {"type": "text", "value": "今天也要开心"}
  ]
}
```

`random` 的 `choices` 中不能再嵌套 `random`。

## dry-run

首次检查时只保留一个测试好友，然后执行：

Windows：

```powershell
.venv\Scripts\python.exe run.py --dry-run
```

Linux：

```bash
.venv/bin/python run.py --dry-run
```

`--dry-run` 只检查登录状态和好友定位，不发送消息。请在打开的浏览器中人工确认定位的是正确好友。

当前好友搜索可能进行部分昵称匹配，并在存在多个候选时选择第一个结果。因此，dry-run 能降低但不能完全消除误发风险。

如需从指定的 `.env` 文件加载环境变量，可追加 `--env-file PATH`。自定义环境文件（例如 `auth.env`）可能包含登录凭证，且不一定被当前 `.gitignore` 忽略；请将其视为敏感文件，并在提交前检查 `git status`。

## 正式发送

确认单个测试好友定位正确后再正式发送：

Windows：

```powershell
.venv\Scripts\python.exe run.py
```

Linux：

```bash
.venv/bin/python run.py
```

确认首次真实发送成功后，再逐步增加好友。多个好友按配置顺序串行处理，不会并发发送。

## 运行结果

- `artifacts/run.log`：运行日志
- `artifacts/result.json`：本次运行的好友级结果
- `artifacts/history.json`：仅在启用本地防重复并产生记录时出现
- `artifacts/screenshots/`：失败截图，不一定每次生成
- `artifacts/traces/`：失败 trace，不一定每次生成

如果任务在日志和结果文件初始化前失败，例如初始配置加载失败或重复运行锁冲突，`artifacts/run.log` 和 `artifacts/result.json` 也可能尚未生成。

退出码按异常发生阶段区分：

| 退出码 | 含义 |
| --- | --- |
| `0` | 所有已处理好友成功 |
| `1` | 至少一个好友处理失败；好友处理阶段再次检查登录或风控失败也归入此类 |
| `2` | 主流程已捕获的初始配置、初始登录、初始风控或重复运行锁错误 |
| `130` | 用户中断 |

无效时区、损坏的历史记录等当前未被主流程专门捕获的异常，通常由 Python 以退出码 `1` 结束并显示 traceback。

## 定时运行

仓库提供以下入口：

- Windows：`scripts/run-windows.ps1`，可交给任务计划程序调用
- Linux：`scripts/run-linux.sh`，或使用 `deploy/systemd/` 中的 service 和 timer
- GitHub Actions：`.github/workflows/send.yml`

使用 GitHub Actions 前，必须同时配置 `DOUYIN_STORAGE_STATE` 和 `DOUYIN_CONFIG` 两个 Secrets，分别保存登录状态 JSON 和完整配置 JSON。工作流每天 `00:00 UTC`（北京时间 08:00）由 schedule 触发，并直接正式发送；只有从 Actions 页面手动触发且 `dry_run=true` 时才执行 dry-run。配置定时触发前务必先用手动 dry-run 和单好友真实发送完成核对，避免误启用后直接发送。

同一账号只应启用一个正式调度器。本地运行锁和防重复记录不能跨机器协调，同时启用 systemd、Windows 任务或 GitHub Actions 可能造成重复发送。

GitHub-hosted runner 的 IP 和浏览器环境会变化，可能触发安全验证；失败时上传的 Actions 产物也可能包含隐私。

## 常见问题

### 登录失效或出现安全验证

重新运行 `scripts/login.py` 保存登录状态。程序不会自动重新登录，也不会绕过验证码、风控或平台限制。

### 找不到聊天搜索框

确认账号已登录且抖音私信页面可以正常打开。若仍失败，抖音页面结构可能已经变化，请结合失败截图和 trace 检查选择器。

### 找不到好友或匹配错误

检查昵称是否准确，并改用更唯一的名称。首次只配置一个测试好友执行 dry-run，人工核对聊天对象；重名或子串昵称可能误匹配。

### 原生表情点击后无法确认

该能力依赖抖音表情面板和页面选择器。使用非无头模式检查 `label`、`category` 和从 `0` 开始的 `fallback_index`；即使已经点击，程序也可能无法可靠确认结果。

### 图片路径不存在

确认文件存在、扩展名受支持，并检查相对路径是否与配置文件位置相符。图片触发发送后目前没有可靠的页面结果确认。

### 异常终止后提示任务正在运行

程序用 `artifacts/run.lock` 防止同一台机器同时运行两个任务。先确认没有其他发送进程，再删除残留的 `artifacts/run.lock`。

### 页面更新后无法操作

抖音页面变化可能使搜索框、消息输入框、图片上传或表情面板的选择器失效。查看 `artifacts/` 中的诊断材料后，再按当前页面调整选择器。

## 安全与限制

- `storage-state.json`、登录中断时可能残留的 `storage-state.json.tmp`、`config.json`、自定义 `--env-file`、日志、结果、截图和 trace 都可能包含账号信息、登录凭证或聊天隐私，不要公开或长期保留。
- 当前 `.gitignore` 不一定覆盖 `storage-state.json.tmp` 或自定义环境文件（例如 `auth.env`）；本任务不修改忽略规则，请在每次提交前运行 `git status`，确认没有误暂存敏感文件。
- GitHub Actions 上传的失败产物同样可能包含隐私，应限制访问并及时删除。
- 没有自动重新登录、验证码绕过、多账号、多好友并发、自动重试或跨机器防重复。
- 好友名称不是稳定的唯一用户标识，重名和子串昵称存在误匹配风险。
- 图片发送缺少可靠的结果确认；原生表情属于实验性能力。
- 抖音页面变化可能随时使选择器失效。
- 仓库目前没有 `LICENSE` 文件，本 README 不授予或声明许可证。

## 测试

安装开发依赖后运行单元测试。

Windows：

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
```

Linux：

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

单元测试不会访问真实抖音，也不能证明真实页面上的好友定位和消息发送长期稳定。真实使用前仍需对一个测试好友执行 dry-run 和人工确认的单好友发送测试。

## 项目结构

```text
app/                  核心配置、浏览器操作和发送逻辑
config/               高级任务配置示例
scripts/              登录及 Windows、Linux 运行脚本
deploy/systemd/       Linux systemd 配置
tests/                单元测试
.github/workflows/     GitHub Actions 工作流
```
