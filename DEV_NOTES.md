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

## 待开发

- [ ] QQ webhook 回调处理（LeagueWeb 推送对局结果 → bot 转发到群）
- [ ] 报名 / 退出队列命令
- [ ] 定时推送排行榜变动
- [ ] Docker Compose 集成到主部署
- [ ] 管理员命令（踢人、强制结束队列等）
