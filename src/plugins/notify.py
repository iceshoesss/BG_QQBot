"""联赛通知 — 对局结束时推送结果到 QQ 群"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.plugin import PluginMetadata

from .league_api import api_get

__plugin_meta__ = PluginMetadata(
    name="最近对局",
    description="查看最近联赛对局结果",
    usage="发送「最近对局」",
)

recent_cmd = on_command("最近对局", aliases={"对局", "战报"}, priority=5, block=True)


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
