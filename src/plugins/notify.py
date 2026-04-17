"""联赛通知 — 对局结束推送 + Webhook 接收问题对局通知"""

import os
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .league_api import api_get

__plugin_meta__ = PluginMetadata(
    name="联赛通知",
    description="查看最近对局 + 接收问题对局 webhook 通知",
    usage="发送「最近对局」",
)

recent_cmd = on_command("最近对局", aliases={"对局", "战报"}, priority=5, block=True)

NOTIFY_GROUP_ID = os.environ.get("LEAGUE_NOTIFY_GROUP_ID", "")


@recent_cmd.handle()
async def handle_recent(bot: Bot, event: MessageEvent):
    try:
        data = await api_get("/api/matches", params={"limit": 5})
    except Exception as e:
        await recent_cmd.finish(f"查询失败: {e}")

    if not data:
        await recent_cmd.finish("暂无对局记录")

    lines = ["⚔️ 最近联赛对局"]
    for m in data:
        players = m.get("players", [])
        time_str = m.get("endedAt", "")[:16].replace("T", " ")
        player_list = " > ".join(
            f"{p.get('displayName', '?')}({p.get('placement', '?')}th)"
            for p in sorted(players, key=lambda x: x.get("placement", 9))
        )
        lines.append(f"\n{time_str}\n{player_list}")

    await recent_cmd.finish("\n".join(lines))


# --- Webhook 接收端 ---

driver = get_driver()


def _format_webhook(payload: dict) -> str | None:
    """将 webhook payload 格式化为群消息"""
    msg_type = payload.get("type", "")
    game_uuid = payload.get("gameUuid", "")
    players = payload.get("players", [])
    started_at = payload.get("startedAt", "")[:16].replace("T", " ")
    player_str = "、".join(players) if players else "未知"

    if msg_type == "timeout":
        return (
            f"⏰ 对局超时结束\n"
            f"开始时间: {started_at}\n"
            f"参与玩家: {player_str}\n"
            f"请管理员补录排名"
        )
    if msg_type == "abandoned":
        return (
            f"🔌 对局部分掉线\n"
            f"开始时间: {started_at}\n"
            f"参与玩家: {player_str}\n"
            f"请管理员补录排名"
        )
    return None


async def _send_to_group(msg: str):
    """发送消息到联赛通知群"""
    if not NOTIFY_GROUP_ID:
        logger.warning("LEAGUE_NOTIFY_GROUP_ID 未配置，跳过通知")
        return

    # 从已连接的 bot 中找一个能发群消息的
    from nonebot import get_bots
    bots = get_bots()
    for bot_id, bot in bots.items():
        if isinstance(bot, Bot):
            try:
                await bot.send_group_msg(group_id=int(NOTIFY_GROUP_ID), message=msg)
                logger.info(f"webhook 通知已发送到群 {NOTIFY_GROUP_ID}")
                return
            except Exception as e:
                logger.warning(f"发送到群失败: {e}")
    logger.warning("没有可用的 Bot 实例发送通知")


@driver.on_startup
async def register_webhook_route():
    """注册 webhook 接收路由"""
    app = driver.server_app  # FastAPI 实例

    @app.post("/webhook/league")
    async def league_webhook(request):
        from fastapi import Request
        from fastapi.responses import JSONResponse

        try:
            payload = await request.json()
        except Exception:
            return JSONResponse({"error": "invalid json"}, status_code=400)

        logger.info(f"收到 webhook: {payload.get('type')}")

        msg = _format_webhook(payload)
        if msg:
            await _send_to_group(msg)

        return JSONResponse({"ok": True})
