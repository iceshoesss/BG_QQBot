"""排行榜 / 选手查询插件"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .league_api import api_get

__plugin_meta__ = PluginMetadata(
    name="排行榜",
    description="查询联赛排行榜和选手信息",
    usage="发送「排行榜」或「战绩 玩家名#1234」",
)

leaderboard_cmd = on_command("排行榜", aliases={"排行", "rank"}, priority=5, block=True)
player_cmd = on_command("战绩", aliases={"查玩家", "玩家"}, priority=5, block=True)


@leaderboard_cmd.handle()
async def handle_leaderboard(bot: Bot, event: GroupMessageEvent):
    try:
        data = await api_get("/api/players", params={"sort": "points", "order": "desc"})
    except Exception as e:
        await leaderboard_cmd.finish(f"查询失败: {e}")

    if not data:
        await leaderboard_cmd.finish("暂无排行榜数据")

    lines = ["🏆 联赛排行榜"]
    for i, p in enumerate(data[:10], 1):
        name = p.get("displayName", "?")
        pts = p.get("totalPoints", 0)
        games = p.get("totalGames", 0)
        wins = p.get("wins", 0)
        avg = p.get("avgPlacement", 0)
        win_rate = f"{wins / games * 100:.0f}%" if games > 0 else "-"
        lines.append(
            f"{i}. {name} | {pts}分 | {games}场 | "
            f"胜率{win_rate} | 场均{avg:.1f}"
        )

    await leaderboard_cmd.finish("\n".join(lines))


@player_cmd.handle()
async def handle_player(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    tag = args.extract_plain_text().strip()
    if not tag:
        await player_cmd.finish("用法: 战绩 玩家名#1234")

    try:
        data = await api_get(f"/api/players/{tag}")
    except Exception as e:
        await player_cmd.finish(f"查询失败: {e}")

    name = data.get("displayName", tag)
    pts = data.get("totalPoints", 0)
    games = data.get("totalGames", 0)
    wins = data.get("wins", 0)
    avg = data.get("avgPlacement", 0)
    win_rate = f"{wins / games * 100:.0f}%" if games > 0 else "-"

    msg = (
        f"👤 {name}\n"
        f"积分: {pts} | 场次: {games}\n"
        f"吃鸡: {wins} | 胜率: {win_rate}\n"
        f"场均排名: {avg:.1f}"
    )
    await player_cmd.finish(msg)
