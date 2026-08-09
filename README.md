# 抖音多好友定时自动发送

使用 Python 和 Playwright 自动打开抖音网页版，依次向多个好友发送文字、图片或抖音原生表情。支持 Windows、Linux 和 GitHub Actions。

## 最简单用法

只需要两个本地文件：

```text
config.json          好友和消息
storage-state.json   抖音登录状态
```

### 1. 安装

Windows：

```powershell
py -3.11 -m venv .venv
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
python scripts/login.py
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

同一个任务在同一天再次运行时，已成功或发送结果不确定的消息都会跳过，避免网络超时后重复发送。确认需要重发时，人工检查聊天记录后再删除 `artifacts/history.json` 中对应记录。

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

仓库包含 `.github/workflows/send.yml`：

- 默认 UTC 00:00，即北京时间 08:00 定时触发。
- 支持 Actions 页面手动触发和 dry-run。
- 需要创建 `DOUYIN_STORAGE_STATE` Secret，值为 `storage-state.json` 的完整 JSON 内容。
- 需要创建 `DOUYIN_CONFIG` Secret，值为 `config.json` 的完整 JSON 内容。

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

- `storage-state.json` 等同登录凭证，不要提交或发送给别人。
- `.env`、`config.json`、`storage-state.json` 已加入 `.gitignore`。
- 截图和 trace 可能包含聊天内容，失败产物应短期保存。
- 出现验证码或安全验证时程序停止，不尝试绕过平台风控。
