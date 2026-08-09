# 抖音多好友定时自动发送

使用 Python 和 Playwright 自动打开抖音网页版，依次向多个好友发送文字、图片或抖音原生表情。支持 Windows、Linux 和 GitHub Actions。

程序注入登录 Cookie 后直接打开抖音官方聊天页 `https://www.douyin.com/chat`，不依赖首页的私信按钮或首页登录标记。

## 最简单用法

只需要两个本地文件：

```text
config.json          好友和消息
storage-state.json   抖音登录状态
```

### 1. 安装

Windows：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m playwright install chromium
```

Linux：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium
```

### 2. 登录一次

```bash
.venv\Scripts\python.exe scripts\login.py
```

在浏览器完成登录并进入私信页面，回到终端按 Enter。程序会生成 `storage-state.json`。

### 3. 配置好友和消息

将 `config.example.json` 复制为 `config.json`，只修改好友和消息：

```json
{
  "friends": ["好友A", "好友B"],
  "messages": [
    {"type": "text", "value": "今天也要开心呀 😊"},
    {"type": "sticker", "value": "比心"}
  ],
  "stickers": {
    "比心": {"label": "比心", "category": "常用", "fallback_index": 3}
  },
  "send_interval_seconds": {"min": 3, "max": 8}
}
```

所有好友收到相同消息。如果不同好友需要不同消息，仍支持旧版 `targets` 高级配置，参考 `config/tasks.example.json`。

消息类型：

```json
{"type": "text", "value": "你好 😊"}
{"type": "image", "value": "data/images/test.png"}
{"type": "sticker", "value": "比心"}
```

### 4. 先检查，不发送

```bash
python run.py --dry-run
```

### 5. 正式发送

```bash
python run.py
```

默认允许重复执行和重复发送。需要开启当天防重复时，在 `config.json` 中配置 `"prevent_duplicates": true`；开启后，已成功或发送结果不确定的消息都会跳过。

## 原生表情

原生表情通过抖音表情面板发送，不是图片或 Unicode Emoji。优先用表情的可访问名称定位，`fallback_index` 只是页面没有名称时的备用序号。

首次使用必须设置 `HEADLESS=false`，只配置一个测试好友，观察发送的表情是否正确。抖音页面更新后，可能需要调整 `config.json` 中的表情映射或 `app/selectors.py`。

## 运行产物

```text
artifacts/run.log       运行日志
artifacts/result.json   本次结果
artifacts/history.json  当天防重复记录
artifacts/screenshots/  失败截图
artifacts/traces/       失败 trace
```

`run.lock` 防止同一台机器同时启动两个任务。若进程被强制结束并遗留锁，确认没有发送进程后删除 `artifacts/run.lock`。

## Linux 定时

将项目部署到 `/opt/douyin-auto-sender`，然后安装：

```bash
sudo useradd --system --home /opt/douyin-auto-sender --shell /usr/sbin/nologin douyin-sender
sudo chown -R douyin-sender:douyin-sender /opt/douyin-auto-sender
sudo cp deploy/systemd/douyin-sender.service /etc/systemd/system/
sudo cp deploy/systemd/douyin-sender.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now douyin-sender.timer
systemctl list-timers douyin-sender.timer
```

默认每天本机时间 08:00 执行。修改 `deploy/systemd/douyin-sender.timer` 中的 `OnCalendar` 可更换时间。

## Windows 定时

在任务计划程序中创建每日任务：

```text
程序：powershell.exe
参数：-ExecutionPolicy Bypass -File C:\项目路径\scripts\run-windows.ps1
起始于：项目根目录
```

设置为“如果任务已在运行，则不启动新实例”。

## GitHub Actions

仓库包含 `.github/workflows/send.yml`，使用 GitHub 托管的 Ubuntu Runner。Actions 不读取本地的 `storage-state.json`，需要配置下面两个 Repository Secret。

### 1. 获取抖音 Cookie

1. 在 Windows 的 Chrome 或 Edge 中打开 `https://www.douyin.com/chat` 并登录。
2. 安装 Cookie-Editor 浏览器扩展。
3. 保持抖音聊天页打开，点击 Cookie-Editor，选择 `Export`，再选择 `JSON`。
4. 复制导出的完整 JSON 数组。正确内容以 `[` 开头、以 `]` 结尾，不是请求头中的 `name=value` Cookie 字符串，也不是 `storage-state.json`。

导出内容的结构类似：

```json
[
  {
    "domain": ".douyin.com",
    "expirationDate": 1800175766.87008,
    "httpOnly": false,
    "name": "UIFID",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "value": "实际 Cookie 值"
  }
]
```

不要使用上面的示例值。必须导出自己已登录账号的完整 Cookie 数组，不能只保留 `UIFID` 一项。

### 2. 配置 GitHub Secrets

进入自己的 GitHub 仓库：

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

添加两个 Secret：

| 名称 | 内容 |
| --- | --- |
| `DOUYIN_COOKIE` | Cookie-Editor 导出的完整 JSON 数组 |
| `DOUYIN_CONFIG` | 本地 `config.json` 的完整 JSON 内容 |

Secret 名称必须完全一致。旧的 `DOUYIN_STORAGE_STATE` 和 `DOUYIN_STORAGE_STATE_GZIP_B64` 已不再使用，可以删除。

### 3. 手动检查

进入仓库的 Actions 页面：

```text
Actions -> Send Douyin Messages -> Run workflow
```

如果首次进入 Actions 页面，先点击 `I understand my workflows, go ahead and enable them`。第一次运行保持 `dry_run=true`，它只验证登录状态和好友，不发送消息。运行失败时，在该次任务的 `Artifacts` 中下载诊断文件并查看截图。

### 4. 正式发送和定时执行

dry-run 成功后，再手动运行一次并设置 `dry_run=false`。工作流还会在每天 UTC 00:00，即北京时间 08:00 自动正式发送；GitHub 的定时任务可能延迟。

Cookie 过期、退出登录或被抖音撤销后，需要在 Windows 浏览器重新登录、重新通过 Cookie-Editor 导出，并覆盖 `DOUYIN_COOKIE` Secret。

GitHub-hosted runner 的 IP 和浏览器环境会变化，可能触发抖音验证。正式运行优先选择 Linux self-hosted runner，并将工作流的 `runs-on` 改为：

```yaml
runs-on: [self-hosted, linux, douyin-sender]
```

Linux systemd 和 GitHub Actions schedule 不要同时启用，否则两个机器之间的本地防重记录不共享。

## 环境变量

本地通常不需要 `.env`。可选变量：

```dotenv
DOUYIN_STORAGE_STATE=storage-state.json
DOUYIN_COOKIE=
TASK_CONFIG=config.json
HEADLESS=false
BROWSER_PATH=
ARTIFACTS_DIR=artifacts
TRACE=true
```

## 测试

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

自动化测试不连接真实抖音。页面选择器、好友名称和原生表情仍必须用测试好友执行 `--dry-run` 和单好友真实发送验收。

## 安全

- `storage-state.json` 和 Cookie-Editor 导出的 Cookie 等同登录凭证，不要提交或发送给别人。
- `.env`、`config.json`、`storage-state.json` 已加入 `.gitignore`。
- 截图和 trace 可能包含聊天内容，失败产物应短期保存。
- 出现验证码或安全验证时程序停止，不尝试绕过平台风控。
