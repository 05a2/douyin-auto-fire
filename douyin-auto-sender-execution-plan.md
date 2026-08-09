# 抖音多好友定时自动发送工具执行计划

## 一、项目目标

实现一个基于 Python 3.11 和 Playwright 的跨平台抖音私信自动发送工具。

核心能力：

1. 支持 Windows、Linux 和 GitHub Actions。
2. 每天按配置的时间自动执行。
3. 一次任务可向多个指定好友依次发送消息。
4. 支持纯文字、Unicode Emoji、本地图片和抖音原生表情包。
5. 单个好友失败时继续处理其他好友。
6. 记录好友级执行结果，失败时保存截图和 Playwright trace。
7. 防止同一天重复向同一好友发送相同任务。
8. Cookie、登录状态和好友信息不能泄漏到代码仓库或日志。

项目定位：

> 一个轻量、可控、跨平台运行的个人抖音多好友定时私信工具。

## 二、范围与约束

### 2.1 第一版必须实现

- 恢复已有抖音登录状态。
- 检查登录是否有效。
- 配置多个目标好友。
- 按好友完整名称搜索并打开私信。
- 发送文字。
- 发送本地 PNG、JPG 或 GIF 图片。
- 打开抖音表情面板并发送指定原生表情包。
- 逐个好友串行发送。
- 好友级错误隔离。
- 本地执行历史和重复发送保护。
- Windows 任务计划程序部署说明。
- Linux systemd timer 部署文件。
- GitHub Actions 手动和定时工作流。
- 结构化日志、失败截图和 trace。

### 2.2 第一版不实现

- Web 管理面板。
- 手机 App 自动化。
- 视频和普通文件发送。
- 多账号并发。
- 多好友并发发送。
- 自动破解验证码或绕过平台风控。
- 自动重新登录。
- 钉钉和邮件等复杂通知渠道。

### 2.3 重要约束

- Unicode Emoji、GIF 图片和抖音原生表情包是三种不同的消息类型。
- 抖音原生表情必须从抖音聊天表情面板中选择，不能用上传图片替代。
- GitHub Actions 的 `schedule` 使用 UTC，且不保证精确到某一分钟启动。
- GitHub-hosted runner 每次使用临时环境和可能变化的出口 IP，存在登录验证和风控风险。
- Linux systemd timer 和 GitHub Actions schedule 不应同时作为正式调度器，除非已经接入共享状态和分布式锁。
- 遇到验证码、设备验证或明确风控时停止运行，不尝试绕过。

## 三、运行架构

程序本身只负责执行一次完整发送任务：

```text
读取配置
恢复登录状态
检查登录状态
检查当天发送历史
遍历目标好友
发送好友配置的消息
记录每个好友的结果
更新发送历史
退出程序
```

各平台负责定时触发同一个入口：

```text
python run.py
```

调度方式：

```text
Windows        -> 任务计划程序
Linux          -> systemd timer（推荐正式运行）或 cron
GitHub Actions -> schedule + workflow_dispatch
```

推荐正式部署：

```text
代码托管和测试       GitHub
正式运行机器         Linux
正式定时器           systemd timer 或 GitHub Actions，二选一
远程手动补发         workflow_dispatch
GitHub Actions Runner Linux self-hosted runner
开发和调试           Windows 或带桌面的 Linux
```

## 四、技术方案

### 4.1 技术栈

```text
Python 3.11+
Playwright async API
python-dotenv
pytest
JSON 配置文件
```

第一版不引入数据库。运行历史暂时保存为 JSON 文件；需要多个运行节点同时调度时，再接入共享数据库或对象存储。

### 4.2 浏览器策略

- 使用 Chromium。
- 使用 Playwright `storage_state` 恢复登录状态。
- 保留 Cookie JSON 作为兼容输入。
- 本地调试默认使用有头模式。
- Linux 服务器和 GitHub Actions 默认使用无头模式。
- 如果抖音在无头模式下行为不同，Linux 使用 `xvfb-run` 启动有界面 Chromium。

登录状态加载优先级：

1. `DOUYIN_STORAGE_STATE`。
2. `DOUYIN_COOKIE`。
3. 两者都没有时直接报错。

## 五、项目结构

```text
douyin-auto-sender/
├── app/
│   ├── __init__.py
│   ├── main.py              # 单次任务编排
│   ├── config.py            # 配置加载与校验
│   ├── models.py            # 任务、消息和结果数据结构
│   ├── browser.py           # 浏览器启动与登录恢复
│   ├── douyin.py            # 搜索好友和打开聊天窗口
│   ├── sender.py            # 文字、图片和原生表情发送
│   ├── selectors.py         # 集中管理页面定位器
│   ├── history.py           # 防重复记录和本地运行锁
│   └── logger.py            # 日志、截图和 trace
├── config/
│   ├── tasks.example.json   # 非敏感任务配置示例
│   └── stickers.json        # 抖音原生表情定位映射
├── data/
│   └── images/              # 待发送图片
├── scripts/
│   ├── install-linux.sh
│   ├── run-linux.sh
│   └── run-windows.ps1
├── deploy/
│   └── systemd/
│       ├── douyin-sender.service
│       └── douyin-sender.timer
├── tests/
├── artifacts/
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── send.yml
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py
```

## 六、配置设计

### 6.1 环境变量

`.env.example`：

```dotenv
DOUYIN_STORAGE_STATE=
DOUYIN_COOKIE=
TASK_CONFIG=config/tasks.json
HEADLESS=true
BROWSER_PATH=
ARTIFACTS_DIR=artifacts
```

规则：

- `.env` 不得提交到 Git。
- 不在日志中打印 `DOUYIN_STORAGE_STATE` 或 `DOUYIN_COOKIE`。
- Windows、Linux 和 GitHub Actions 可以分别维护自己的登录状态。
- GitHub Actions 中的登录状态必须保存在 Actions Secrets。

### 6.2 任务配置

`config/tasks.example.json`：

```json
{
  "timezone": "Asia/Shanghai",
  "task_id": "daily-streak",
  "targets": [
    {
      "name": "好友A",
      "messages": [
        {
          "type": "text",
          "content": "早上好"
        },
        {
          "type": "douyin_sticker",
          "sticker": "比心"
        }
      ]
    },
    {
      "name": "好友B",
      "messages": [
        {
          "type": "image",
          "path": "data/images/good-morning.png"
        }
      ]
    },
    {
      "name": "好友C",
      "messages": [
        {
          "type": "random",
          "choices": [
            {
              "type": "text",
              "content": "今天也要开心"
            },
            {
              "type": "douyin_sticker",
              "sticker": "开心"
            }
          ]
        }
      ]
    }
  ],
  "send_interval_seconds": {
    "min": 3,
    "max": 8
  },
  "continue_on_error": true
}
```

第一版使用好友完整昵称定位。若出现重名，配置模型需要扩展为抖音号、主页 URL 或其他唯一标识，不能依靠搜索结果顺序猜测好友。

### 6.3 原生表情映射

`config/stickers.json`：

```json
{
  "比心": {
    "category": "常用",
    "accessible_name": "比心",
    "fallback_index": 3
  },
  "开心": {
    "category": "常用",
    "accessible_name": "开心",
    "fallback_index": 5
  }
}
```

表情定位优先级：

1. `aria-label` 或 `title`。
2. 可见名称。
3. 图片 `alt`。
4. 稳定的 `data-*` 属性。
5. 表情类别和序号。
6. 图像匹配仅作为最后备选。

## 七、核心模块

### 7.1 配置模块

职责：

- 读取环境变量和任务 JSON。
- 校验目标好友非空。
- 校验所有消息类型。
- 校验图片文件存在且格式受支持。
- 校验原生表情存在于映射文件。
- 校验等待时间范围。
- 输出明确但不包含敏感信息的错误。

### 7.2 浏览器模块

职责：

- 启动 Chromium。
- 根据运行环境选择有头或无头模式。
- 恢复 `storage_state` 或注入 Cookie。
- 打开抖音私信页面。
- 检查登录状态。
- 启动和停止 Playwright trace。
- 正确关闭页面、Context 和浏览器。

登录检查结果：

```text
authenticated
login_required
risk_controlled
unknown
```

### 7.3 抖音页面模块

职责：

- 清空并输入好友名称。
- 等待搜索结果。
- 完整匹配好友名称。
- 打开发消息页面。
- 确认当前聊天对象与目标好友一致。
- 为发送模块提供稳定的输入框、上传控件和表情面板定位器。

不要只依赖压缩后的 CSS 类名。页面定位优先级：

1. `role`、`placeholder`、`aria-label`。
2. 可见文本。
3. 稳定的 `data-*` 属性。
4. DOM 相对关系。
5. CSS 类名。

### 7.4 消息发送模块

统一入口：

```python
async def send_message(page, message):
    match message.type:
        case "text":
            await send_text(page, message.content)
        case "image":
            await send_image(page, message.path)
        case "douyin_sticker":
            await send_douyin_sticker(page, message.sticker)
```

文字发送流程：

```text
定位聊天输入框
点击输入框
填入文本或 Unicode Emoji
按 Enter
确认聊天记录出现新消息
```

图片发送流程：

```text
定位文件上传 input
调用 set_input_files
等待预览或上传完成
点击发送
确认聊天记录出现新图片消息
```

抖音原生表情发送流程：

```text
点击表情按钮
等待抖音表情面板可见
选择表情分类
根据名称或映射定位表情
点击原生表情
确认聊天记录出现新表情消息
```

### 7.5 历史和防重复模块

运行键格式：

```text
task_id + 日期 + 好友标识 + 消息序号
```

示例：

```text
daily-streak:2026-08-09:friend-a:0
```

发送前检查该运行键是否已成功；成功过则返回 `duplicate`，不再次发送。

状态必须在确认发送成功后写入。若点击发送后程序超时，且无法确认是否送达，记录为 `unknown`，不得立即自动重发。

第一版本地保存：

```text
artifacts/history.json
artifacts/run.lock
```

本地锁只能防止同一机器并发运行。Linux 和 GitHub-hosted runner 同时调度时，必须使用共享数据库或对象存储实现全局防重。

### 7.6 日志和产物模块

好友级结果示例：

```json
{
  "target": "好友A",
  "status": "success",
  "message_type": "douyin_sticker",
  "started_at": "2026-08-09T08:00:03+08:00",
  "finished_at": "2026-08-09T08:00:08+08:00",
  "attempts": 1,
  "error": null
}
```

状态定义：

```text
success
failed
skipped
duplicate
login_required
risk_controlled
unknown
```

运行产物：

```text
artifacts/run.log
artifacts/result.json
artifacts/history.json
artifacts/screenshots/<timestamp>-<target>.png
artifacts/traces/<timestamp>.zip
```

截图和 trace 可能包含好友名称和聊天内容，必须限制保存期限和访问权限。

## 八、多好友执行策略

第一版必须串行执行：

```text
好友A -> 搜索 -> 校验 -> 打开聊天 -> 发送 -> 记录结果
等待随机间隔
好友B -> 搜索 -> 校验 -> 打开聊天 -> 发送 -> 记录结果
等待随机间隔
好友C -> 搜索 -> 校验 -> 打开聊天 -> 发送 -> 记录结果
```

规则：

- 好友搜索失败只影响该好友。
- 找不到聊天输入框时保存该好友截图。
- 每次发送前确认当前聊天对象。
- 每条消息成功后立即记录，避免进程中断后全部重发。
- 不并发打开多个聊天窗口。
- 不在无法确认发送结果时盲目重试。

## 九、重试策略

```text
页面加载超时       重试 1 次
搜索结果未出现     重试 1 次
图片上传超时       重试 1 次
登录失败           不重试
验证码或风控       不重试
好友名称不匹配     不重试
点击发送后结果未知 不自动重发
```

重试必须针对当前步骤，不能无条件重新执行整个好友任务。

## 十、平台部署

### 10.1 Windows

安装：

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m playwright install chromium
```

手动执行：

```powershell
.venv\Scripts\python.exe run.py
```

定时任务使用 Windows 任务计划程序：

- 操作指向 `.venv\Scripts\python.exe`。
- 参数为 `run.py`。
- 起始目录为项目根目录。
- 每天固定时间触发。
- 禁止在上一次任务仍在运行时启动新实例。

### 10.2 Linux

安装：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium
```

`deploy/systemd/douyin-sender.service`：

```ini
[Unit]
Description=Douyin Auto Sender
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/douyin-auto-sender
EnvironmentFile=/opt/douyin-auto-sender/.env
ExecStart=/opt/douyin-auto-sender/.venv/bin/python run.py
```

`deploy/systemd/douyin-sender.timer`：

```ini
[Unit]
Description=Run Douyin Auto Sender Daily

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true
RandomizedDelaySec=0

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now douyin-sender.timer
systemctl list-timers douyin-sender.timer
```

`Persistent=true` 允许机器错过预定时间后在恢复运行时补跑。程序仍必须通过发送历史判断当天是否已经发送。

### 10.3 GitHub Actions

`.github/workflows/send.yml` 目标结构：

```yaml
name: Send Douyin Messages

on:
  workflow_dispatch:
    inputs:
      dry_run:
        description: Only validate login and targets
        required: false
        default: true
        type: boolean
  schedule:
    - cron: "0 0 * * *"

concurrency:
  group: douyin-daily-sender
  cancel-in-progress: false

jobs:
  send:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    env:
      DOUYIN_STORAGE_STATE: ${{ secrets.DOUYIN_STORAGE_STATE }}
      HEADLESS: "true"
      TZ: Asia/Shanghai
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python -m playwright install --with-deps chromium

      - name: Run sender
        run: python run.py

      - name: Upload failure artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: douyin-failure-${{ github.run_id }}
          path: artifacts/
          retention-days: 3
```

北京时间 08:00 对应 UTC 00:00。更换时区或执行时间时必须重新换算 cron。

GitHub Actions 安全规则：

- `DOUYIN_STORAGE_STATE` 只存放在 Actions Secrets。
- 真实任务不能由 fork PR 触发。
- 不在测试工作流中执行真实发送。
- 日志中不得输出登录状态内容。
- 失败截图和 trace 只短期保留。
- `concurrency` 只防止同一 Actions 工作流并发，不能防止 Linux systemd 同时发送。

正式运行推荐 self-hosted runner：

```yaml
runs-on: [self-hosted, linux, douyin-sender]
```

self-hosted runner 的优势：

- 出口 IP 和设备环境相对稳定。
- 浏览器依赖无需每次重新安装。
- 登录状态可保存在受控机器上。
- 仍可使用 GitHub 的定时、日志和手动触发功能。

## 十一、测试计划

### 11.1 单元测试

- 缺少登录状态。
- storage state JSON 格式错误。
- Cookie JSON 格式错误。
- 目标好友为空。
- 好友配置格式错误。
- 未知消息类型。
- 图片不存在。
- 原生表情未配置。
- 随机消息列表为空。
- 已存在当天成功历史。
- 日期和时区计算正确。

### 11.2 浏览器集成测试

- storage state 可以恢复登录。
- 登录失效能正确识别。
- 风控页面能正确识别。
- 搜索框可以定位。
- 好友完整名称匹配正确。
- 当前聊天对象校验正确。
- 文字可以发送。
- 图片可以上传和发送。
- 原生表情面板可以打开。
- 指定原生表情可以定位和发送。

### 11.3 失败场景测试

- 不存在的好友。
- 同名好友。
- 页面加载超时。
- 搜索结果超时。
- 编辑框不存在。
- 图片上传失败。
- 表情面板未打开。
- 表情映射失效。
- 浏览器异常关闭。
- 网络中断。
- 点击发送后无法确认结果。
- 任务被重复触发。

### 11.4 平台测试

- Windows 有头模式。
- Windows 无头模式。
- Linux 无头模式。
- Linux `xvfb-run` 模式。
- Linux systemd 手动启动。
- Linux systemd timer 定时启动。
- GitHub Actions `workflow_dispatch`。
- GitHub Actions `schedule`。
- GitHub-hosted runner。
- Linux self-hosted runner。

## 十二、实施阶段

### 阶段 0：核心可行性验证

预计时间：1 至 2 天。

工作项：

- 使用一个测试好友恢复登录。
- 发送一条文字。
- 发送一张本地图片。
- 打开抖音原生表情面板。
- 发送一个指定原生表情。
- 检查发送后的 DOM 变化。
- 记录可用定位器和失败页面截图。

验收标准：

```text
文字连续成功 5 次
图片连续成功 5 次
指定原生表情连续成功 5 次
```

这是最高优先级阶段。原生表情的网页支持和稳定定位没有验证前，不进入大规模工程开发。

### 阶段 1：跨平台程序骨架

预计时间：2 至 3 天。

工作项：

- 创建项目结构。
- 实现配置模型与校验。
- 实现 storage state 和 Cookie 加载。
- 实现浏览器启动和关闭。
- 实现登录状态检查。
- 实现 `--dry-run`。
- 处理 Windows 和 Linux 文件路径。

验收标准：

```bash
python run.py --dry-run
```

Windows 和 Linux 均能检查登录及目标配置，不发送消息。

### 阶段 2：多好友和三类消息

预计时间：3 至 5 天。

工作项：

- 实现好友搜索和完整名称匹配。
- 实现聊天对象二次确认。
- 实现多好友串行执行。
- 实现文字发送器。
- 实现图片发送器。
- 实现抖音原生表情发送器。
- 实现随机消息。
- 实现好友间随机等待。
- 实现单好友失败隔离。

验收标准：

- 至少配置 3 个好友。
- 其中一个好友不存在时，其他好友仍继续执行。
- 文字、图片和原生表情分别发送成功。
- 每个好友都有独立结果。

### 阶段 3：日志、防重复和恢复能力

预计时间：2 至 3 天。

工作项：

- 写入结构化运行日志。
- 保存好友级失败截图。
- 保存失败 trace。
- 实现当天发送历史。
- 实现本地进程锁。
- 实现步骤级重试。
- 对敏感信息脱敏。
- 正确处理发送结果未知状态。

验收标准：

- 同一天重复启动不会重复发送成功过的消息。
- 好友失败后可根据截图和 trace 定位原因。
- 日志不包含 Cookie 或完整 storage state。
- 程序中断后可跳过已经成功的消息继续执行。

### 阶段 4：Linux 正式部署

预计时间：1 至 2 天。

工作项：

- 编写 Linux 安装脚本。
- 安装 Chromium 系统依赖。
- 创建 systemd service 和 timer。
- 配置日志保留策略。
- 测试重启后的补跑和防重复。

验收标准：

- systemd 能手动启动任务。
- timer 能在指定时间触发。
- 机器错过时间后恢复时不会重复发送。
- 连续运行 3 天不需要人工干预。

### 阶段 5：GitHub Actions

预计时间：2 至 3 天。

工作项：

- 创建测试工作流。
- 创建 `workflow_dispatch` 手动发送工作流。
- 配置 Secrets。
- 安装 Playwright Chromium。
- 上传失败产物。
- 配置 `concurrency`。
- 验证 GitHub-hosted runner。
- 部署并验证 Linux self-hosted runner。
- 最后决定正式调度器使用 systemd 还是 Actions schedule。

验收标准：

- 手动触发可运行 dry-run。
- 手动触发真实任务可发送。
- 定时触发可以运行。
- 登录状态不会出现在日志中。
- 失败产物可以下载且只短期保留。

### 阶段 6：稳定性观察

预计时间：至少 7 天。

观测指标：

```text
运行次数
登录成功率
好友搜索成功率
文字发送成功率
图片发送成功率
原生表情发送成功率
平均执行时间
风控出现次数
重复发送次数
结果未知次数
```

正式启用标准：

- 连续 7 天按计划执行。
- 没有重复发送。
- 单个好友失败不影响其他好友。
- 登录失效时不会继续操作。
- 原生表情成功率达到可接受范围。
- 日志和产物中没有敏感凭证。

## 十三、执行清单

按以下顺序推进，不跨阶段开发：

- [ ] 准备一个专用测试好友。
- [ ] 在带桌面的环境手动登录抖音网页版。
- [ ] 导出 Playwright storage state。
- [ ] 验证抖音网页版私信入口。
- [ ] 验证文字发送。
- [ ] 验证图片上传和发送。
- [ ] 验证抖音原生表情面板。
- [ ] 找到至少一个原生表情的稳定定位方式。
- [ ] 完成阶段 0 的三项连续 5 次测试。
- [ ] 创建 Python 项目骨架。
- [ ] 实现配置校验和 dry-run。
- [ ] 实现多好友串行处理。
- [ ] 实现三类消息发送器。
- [ ] 实现日志、截图和 trace。
- [ ] 实现历史记录和本地锁。
- [ ] 完成 Windows 测试。
- [ ] 完成 Linux 测试。
- [ ] 部署 systemd timer。
- [ ] 创建 GitHub Actions 手动工作流。
- [ ] 配置 GitHub Actions Secrets。
- [ ] 验证 GitHub-hosted runner。
- [ ] 部署 Linux self-hosted runner。
- [ ] 选择唯一的正式自动调度器。
- [ ] 连续观察至少 7 天。

## 十四、风险与应对

| 风险 | 影响 | 应对措施 |
|---|---|---|
| 抖音网页版不支持原生表情 | 核心需求无法通过网页实现 | 阶段 0 优先验证；失败后再评估桌面客户端自动化 |
| DOM 结构变化 | 定位器失效 | 定位器集中管理，优先使用语义属性，保留 trace |
| Cookie 或 storage state 失效 | 定时任务无法登录 | 明确返回 `login_required`，停止运行并提示人工更新 |
| GitHub-hosted IP 变化 | 登录验证或风控 | 正式运行优先使用 Linux self-hosted runner |
| Actions 定时延迟 | 不能准点运行 | 严格准点任务使用 Linux systemd timer |
| 多调度器同时运行 | 重复发送 | 正式环境只启用一个自动调度器，或接入共享锁 |
| 点击发送后状态未知 | 重试造成重复消息 | 记录 `unknown`，不自动重发 |
| 好友昵称重名 | 发错对象 | 增加唯一标识，发送前二次确认聊天对象 |
| trace 或截图泄露聊天信息 | 隐私风险 | 限制上传条件、访问权限和保留期限 |
| 账号触发验证码或风控 | 任务失败或账号风险 | 串行发送、合理间隔、停止自动操作，不绕过风控 |

## 十五、最终验收标准

项目完成需同时满足：

1. 同一套代码可在 Windows 和 Linux 运行。
2. GitHub Actions 可以手动触发和按 cron 触发。
3. 支持至少 3 个好友的串行发送。
4. 支持文字、Unicode Emoji、本地图片和抖音原生表情。
5. 单个好友失败不影响后续好友。
6. 每个好友和每条消息都有明确结果。
7. 同一天重复触发不会重复发送已成功消息。
8. 登录失败、验证码和风控会停止运行。
9. 失败时能获得截图、日志和 trace。
10. 代码仓库和日志中没有 Cookie、storage state 等敏感信息。
11. 选定且只启用一个正式自动调度器。
12. 正式环境连续运行 7 天且无重复发送。

## 十六、推荐落地顺序

```text
原生表情技术验证
        ↓
Windows/Linux 单次 dry-run
        ↓
单好友三类消息发送
        ↓
多好友串行发送
        ↓
日志、失败产物和防重复
        ↓
Linux systemd 正式定时
        ↓
GitHub Actions 手动触发
        ↓
Linux self-hosted runner
        ↓
7 天稳定性验证
```

第一项实际开发任务应是阶段 0 的原生表情技术验证，而不是先搭建 Web 面板或完整调度系统。
