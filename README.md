# BG_QQBot

炉石战棋联赛 QQ 机器人 — 基于 [NoneBot2](https://nonebot.dev/) + OneBot V11。

配套仓库：
- [HDT_BGTracker](https://github.com/iceshoesss/HDT_BGTracker) — HDT 插件
- [LeagueWeb](https://github.com/iceshoesss/LeagueWeb) — 联赛网站

## 功能

| 命令 | 说明 |
|------|------|
| `排行榜` | 查看联赛排行榜 TOP 10 |
| `战绩 玩家名#1234` | 查询选手数据 |
| `队列` | 查看当前排队状态 |
| `最近对局` | 查看最近 5 场联赛 |
| `绑定 绑定码` | QQ 与游戏账号关联 |
| `我的绑定` | 查看当前绑定状态 |

## 项目结构

```
BG_QQBot/
├── bot.py                  # 入口
├── pyproject.toml          # NoneBot2 配置 + 依赖
├── .env.dev                # 开发环境配置（模板）
├── .env.prod               # 生产环境配置（模板）
├── Dockerfile
├── requirements.txt
└── src/plugins/
    ├── league_api.py       # API 客户端（共用）
    ├── bind.py             # QQ 绑定
    ├── stats.py            # 排行榜 / 选手查询
    ├── queue_cmd.py        # 队列查询
    └── notify.py           # 最近对局
```

## 快速启动

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 复制并编辑配置（开发环境用 .env.dev，生产用 .env.prod）
cp .env.dev .env

# 启动（需要 OneBot V11 客户端已连接）
python bot.py
```

### Docker

```bash
docker build -t bg-qqbot:latest .
docker run -d --env .env bg-qqbot:latest
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `LEAGUE_API_URL` | 联赛网站 API 地址 |
| `LEAGUE_NOTIFY_GROUP_ID` | 通知群号（问题对局 webhook 推送到此群） |
| `SUPERUSERS` | 管理员 QQ 号 |
| `ONEBOT_WS_URLS` | OneBot 反向 WS 地址 |
| `BOT_API_KEY` | 与 LeagueWeb 的 `BOT_API_KEY` 一致 |

## Webhook 通知

机器人提供 `/webhook/league` 端点接收 LeagueWeb 的问题对局通知（超时、掉线）。

LeagueWeb 配置环境变量：
```
WEBHOOK_URL=http://<机器人地址>:<端口>/webhook/league
```

## 版本管理

当前版本：`v0.1.0`（定义在 `pyproject.toml`）

## 更新日志

### v0.1.0 (2026-04-17)
- 初始版本
- 排行榜查询、选手查询、队列状态、QQ 绑定
