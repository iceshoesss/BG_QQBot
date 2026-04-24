# BG_QQBot 开发笔记

## 技术栈

- Python 3.12
- NoneBot2 + OneBot V11 适配器
- httpx（异步 HTTP 客户端）

## 踩坑记录

### NoneBot2 配置

- `LEAGUE_API_URL` 需要在 `.env` 中配置，插件通过 `driver.config.league_api_url` 读取
- OneBot V11 适配器需要 `nonebot-adapter-onebot` 包

### OneBot V11

- 使用反向 WebSocket 模式（NoneBot2 作为服务端，OneBot 客户端连接）
- 群消息事件用 `GroupMessageEvent`
- 用户 ID 通过 `event.user_id` 获取

### FastAPI webhook 路由

- 在 `driver.server_app` 上注册自定义路由时，参数**必须**标注 `fastapi.Request` 类型
- 没有类型注解时 FastAPI 把参数当请求体 schema 校验，收到 JSON body 直接返回 422
- 坑：普通 Flask/FastAPI 写法 `def handler(request)` 可以省略注解，但 NoneBot2 环境下不行

### Webhook 通知流程

```
LeagueWeb cleanup 线程（每 CLEANUP_INTERVAL 秒）
  → cleanup_stale_games() / cleanup_partial_matches()
  → send_webhook(POST → bot 的 /webhook/league)
  → bot _build_webhook_msg() 格式化
  → bot.send_group_msg() 发到 LEAGUE_NOTIFY_GROUP_ID
```

- 通知只发一次：标记 `status` 后不再重复匹配
- abandoned 类型只通知 placement=null 的玩家

## 已停用命令

排行榜、战绩查询、队列查询、最近对局、帮助/菜单 — 代码移至 `disabled_plugins/` 目录，需要时移回 `src/plugins/` 即可恢复。

## 待开发

- [x] QQ webhook 回调处理（LeagueWeb 推送问题对局 → bot 转发到群）
- [ ] 报名 / 退出队列命令
- [ ] 定时推送排行榜变动
- [ ] Docker Compose 集成到主部署
- [ ] 管理员命令（踢人、强制结束队列等）
