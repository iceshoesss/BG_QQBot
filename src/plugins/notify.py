"""联赛通知 — 对局结束推送 + Webhook 接收问题对局通知"""

import json
import os
from pathlib import Path

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
BIND_FILE = Path(__file__).parent.parent.parent / "data" / "qq_bindings.json"


def _load_bindings() -> dict:
    if BIND_FILE.exists():
        return json.loads(BIND_FILE.read_text(encoding="utf-8"))
    return {}


def _find_qq_by_display_name(bindings: dict, display_name: str) -> str | None:
    """通过 displayName 反查 QQ 号"""
    for qq_id, info in bindings.items():
        if info.get("displayName") == display_name:
            return qq_id
    return None


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


def _build_webhook_msg(payload: dict) -> list:
    """将 webhook payload 格式化为群消息（支持 @ 玩家）"""
    msg_type = payload.get("type", "")
    players = payload.get("players", [])  # displayName 列表
    started_at = payload.get("startedAt", "")[:16].replace("T", " ")

    bindings = _load_bindings()

    if msg_type == "timeout":
        title = "⏰ 对局超时结束"
    elif msg_type == "abandoned":
        title = "🔌 对局部分掉线"
    else:
        return []

    segments = [MessageSegment.text(f"{title}\n开始时间: {started_at}\n")]

    segments.append(MessageSegment.text("涉及玩家: "))
    for i, name in enumerate(players):
        if i > 0:
            segments.append(MessageSegment.text("、"))
        segments.append(MessageSegment.text(name))
        qq_id = _find_qq_by_display_name(bindings, name)
        if qq_id:
            segments.append(MessageSegment.text(" "))
            segments.append(MessageSegment.at(int(qq_id)))

    segments.append(MessageSegment.text("\n请以上玩家补录排名"))
    return segments


async def _send_to_group(msg_segments: list):
    """发送消息到联赛通知群"""
    if not NOTIFY_GROUP_ID:
        logger.warning("LEAGUE_NOTIFY_GROUP_ID 未配置，跳过通知")
        return

    from nonebot import get_bots
    for bot_id, bot in get_bots().items():
        if isinstance(bot, Bot):
            try:
                await bot.send_group_msg(
                    group_id=int(NOTIFY_GROUP_ID),
                    message=msg_segments,
                )
                logger.info(f"webhook 通知已发送到群 {NOTIFY_GROUP_ID}")
                return
            except Exception as e:
                logger.warning(f"发送到群失败: {e}")
    logger.warning("没有可用的 Bot 实例发送通知")


@driver.on_startup
async def register_webhook_route():
    """注册 webhook 接收路由"""
    from fastapi import Request
    from fastapi.responses import JSONResponse

    app = driver.server_app

    @app.post("/webhook/league")
    async def league_webhook(request: Request):

        try:
            payload = await request.json()
        except Exception:
            return JSONResponse({"error": "invalid json"}, status_code=400)

        logger.info(f"收到 webhook: {payload.get('type')}")

        msg_segments = _build_webhook_msg(payload)
        if msg_segments:
            await _send_to_group(msg_segments)

        return JSONResponse({"ok": True})
