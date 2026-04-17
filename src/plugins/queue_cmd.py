"""队列查询 — 查看当前联赛队列状态"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.plugin import PluginMetadata

from .league_api import api_get

__plugin_meta__ = PluginMetadata(
    name="队列查询",
    description="查看联赛队列当前状态",
    usage="发送「队列」查看当前排队情况",
)

queue_cmd = on_command("队列", aliases={"排队", "queue"}, priority=5, block=True)


@queue_cmd.handle()
async def handle_queue(bot: Bot, event: MessageEvent):
    try:
        signup = await api_get("/api/queue")
        waiting = await api_get("/api/waiting-queue")
    except Exception as e:
        await queue_cmd.finish(f"查询失败: {e}")

    lines = []
    if waiting:
        for group in waiting:
            players = group.get("players", [])
            lines.append(f"⏳ 等待开赛 ({len(players)}/8):")
            for p in players:
                name = p.get("name", "?")
                lines.append(f"  {name}")
    else:
        lines.append("⏳ 暂无等待组")

    if signup:
        lines.append(f"\n📝 报名中 ({len(signup)}):")
        for p in signup:
            name = p.get("name", "?")
            lines.append(f"  {name}")
    else:
        lines.append("\n📝 暂无报名")

    await queue_cmd.finish("\n".join(lines))
