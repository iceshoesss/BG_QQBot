"""联赛通知 — 对局结束推送 + Webhook 接收问题对局通知"""

import json
import os
from pathlib import Path

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot.log import logger

NOTIFY_GROUP_ID = os.environ.get("LEAGUE_NOTIFY_GROUP_ID", "")
BIND_FILE = Path(__file__).parent.parent.parent / "data" / "qq_bindings.json"


def _load_bindings() -> dict:
    if BIND_FILE.exists():
        return json.loads(BIND_FILE.read_text(encoding="utf-8"))
    return {}


def _find_qq_by_battle_tag(bindings: dict, battle_tag: str) -> str | None:
    """通过 battleTag 反查 QQ 号（battleTag 带 #tag，唯一）"""
    for qq_id, info in bindings.items():
        if info.get("battleTag") == battle_tag:
            return qq_id
    return None


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
    for i, p in enumerate(players):
        if isinstance(p, dict):
            display_name = p.get("displayName", "")
            battle_tag = p.get("battleTag", "")
        else:
            # 兼容旧格式（纯字符串）
            display_name = str(p)
            battle_tag = ""
        if i > 0:
            segments.append(MessageSegment.text("、"))
        segments.append(MessageSegment.text(display_name or battle_tag))
        qq_id = _find_qq_by_battle_tag(bindings, battle_tag) if battle_tag else None
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
