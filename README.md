# 🔥 抖音自动续火花

[![GitHub stars](https://img.shields.io/github/stars/unmev/douyin-auto-fire?style=flat-square)](https://github.com/unmev/douyin-auto-fire/stargazers)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=unmev.douyin-auto-fire)

> 定时自动向抖音好友发送消息，保持火花不断。基于 Playwright 模拟真实浏览器操作，配合 GitHub Actions 定时运行，**无需服务器长期在线**。

![douyin-auto-fire-banner.svg](https://img.908988.xyz/file/教程/douyin-auto-fire/5pdab8It.svg)

## 项目介绍

`douyin-auto-fire` 是一个基于 Python + Playwright 的抖音私信自动发送工具。

通过模拟浏览器操作，可以按照配置自动向指定好友发送文字、图片或抖音原生表情，并配合 GitHub Actions 实现每天定时运行。

如果只是使用 GitHub Actions，**不需要自己购买服务器，也不需要电脑长期保持开机**。Fork 项目、配置登录 Cookie 和发送内容后即可运行。

> ⚠️ 本项目使用 Cookie 作为登录凭证。请只将 Cookie 保存在 GitHub Secrets 等安全位置，不要提交到公开仓库，也不要分享给他人。

## ✨ 已实现功能

- ⏰ **定时自动发送**：通过 GitHub Actions 定时触发，支持自定义 cron 和时区
- 💬 **多种消息类型**：支持文字、图片（PNG/JPG/GIF/WebP）和抖音原生表情
- 🎲 **随机消息**：支持从多条候选消息中随机选择
- 👥 **多好友支持**：可以同时为多个好友配置发送任务
- 👤 **多账号支持**：GitHub Actions 当前最多支持 5 个抖音账号
- 🧪 **Dry Run 模式**：只验证登录状态和好友定位，不真实发送消息
- 🔒 **防重复发送**：支持记录发送历史，减少重复触发导致的重复发送
- 🔔 **钉钉通知**：支持通过钉钉机器人接收任务结果
- 🛡️ **失败诊断**：失败时可保存日志、页面截图和 Playwright Trace
- 🔐 **登录凭证灵活**：支持 Cookie 或浏览器 Storage State
- ⏱️ **模拟真人操作**：支持随机发送间隔和输入节奏

## 🚀 使用教程

推荐使用 **GitHub Actions** 部署，无需准备服务器。

### 📖 [GitHub Actions 完整图文教程 →](docs/github-actions.md)

教程包含：

- Fork 并启用 GitHub Actions
- 获取抖音 Cookie
- 生成发送配置
- 配置 GitHub Secrets
- Dry Run 测试
- 真实发送测试
- 修改每天自动运行时间
- Cookie 失效后的处理方法
- 钉钉通知
- 多账号配置
- 失败日志与诊断文件

> 第一次使用建议先配置 **1 个账号 + 1 个好友 + 1 条文字消息**，确认运行正常后再增加其他配置。

## 🧰 技术栈

| 类别 | 内容 |
| --- | --- |
| 语言 | Python 3.11+ |
| 浏览器自动化 | [Playwright](https://playwright.dev/python/) + Chromium |
| 定时调度 | GitHub Actions |
| 环境变量 | python-dotenv |
| 时区 | tzdata |
| 通知 | 钉钉机器人 Webhook |
| 支持平台 | Windows / macOS / Linux |

主要依赖：

```text
playwright>=1.54,<2
python-dotenv>=1.1,<2
tzdata>=2025.2
```

## ⚠️ 注意事项

- Cookie 和发送配置不要直接提交到公开仓库。
- 修改好友、消息或表情配置后，建议先运行一次 Dry Run。
- 同一个抖音账号不要同时运行多个自动发送任务，避免重复发送。
- GitHub-hosted Runner 的网络环境可能触发抖音安全验证。
- 如果 Cookie 失效或抖音要求验证码，需要本人重新完成登录并更新 Cookie。
- 抖音网页结构发生变化时，自动化功能可能需要同步适配。

## ⭐ Star History

<a href="https://www.star-history.com/?repos=unmev%2Fdouyin-auto-fire&type=timeline&logscale=&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=unmev/douyin-auto-fire&type=timeline&theme=dark&logscale&legend=top-left&sealed_token=mG37UD2jXGVQJy-H4cuDopHM4wILzzGQXTz_IEdDgAijz0DDijk1go72jyWmrUZlNRVibNgW6OTl-YQamgUPkpFo_gAO2EPSlVwuZUX3n_7AuKwAK40HMQ" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=unmev/douyin-auto-fire&type=timeline&logscale&legend=top-left&sealed_token=mG37UD2jXGVQJy-H4cuDopHM4wILzzGQXTz_IEdDgAijz0DDijk1go72jyWmrUZlNRVibNgW6OTl-YQamgUPkpFo_gAO2EPSlVwuZUX3n_7AuKwAK40HMQ" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=unmev/douyin-auto-fire&type=timeline&logscale&legend=top-left&sealed_token=mG37UD2jXGVQJy-H4cuDopHM4wILzzGQXTz_IEdDgAijz0DDijk1go72jyWmrUZlNRVibNgW6OTl-YQamgUPkpFo_gAO2EPSlVwuZUX3n_7AuKwAK40HMQ" />
 </picture>
</a>

## 友情链接

- [LINUX DO](https://linux.do/) - 新的理想型社区

## License

本项目采用 [MIT License](LICENSE)。
