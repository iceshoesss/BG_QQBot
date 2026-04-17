"""排行榜 / 选手查询插件"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .league_api import api_get

__plugin_meta__ = PluginMetadata(
    name="排行榜",
    description="查询联赛排行榜和选手信息",
    usage="发送「排行榜」或「战绩 玩家名#1234」",
)

leaderboard_cmd = on_command("排行榜", aliases={"排行", "rank"}, priority=5, block=True)
player_cmd = on_command("战绩", aliases={"查玩家", "玩家"}, priority=5, block=True)


@leaderboard_cmd.handle()
async def handle_leaderboard(bot: Bot, event: MessageEvent):
    try:
        data = await api_get("/api/players")
    except Exception as e:
        await leaderboard_cmd.finish(f"查询失败: {e}")

    if not data:
        await leaderboard_cmd.finish("暂无排行榜数据")

    lines = ["🏆 联赛排行榜 TOP 10\n"]
    for i, p in enumerate(data[:10], 1):
        name = p.get("displayName", "?")
        pts = p.get("totalPoints", 0)
        games = p.get("leagueGames", 0)
        chickens = p.get("chickens", 0)
        avg = p.get("avgPlacement", 0)
        win_rate = p.get("winRate", 0)

        lines.append(
            f"{i}. {name}\n"
            f"   {pts}分 | {games}场 | 场均{avg:.1f} | "
            f"前四{win_rate:.0%} | 吃鸡{chickens}"
        )

    await leaderboard_cmd.finish("\n".join(lines))


@player_cmd.handle()
async def handle_player(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    tag = args.extract_plain_text().strip()
    if not tag:
        await player_cmd.finish("用法: 战绩 玩家名#1234")

    try:
        data = await api_get(f"/api/players/{tag}")
    except Exception as e:
        await player_cmd.finish(f"查询失败: {e}")

    name = data.get("displayName", tag)
    pts = data.get("totalPoints", 0)
    games = data.get("leagueGames", 0)
    chickens = data.get("chickens", 0)
    avg = data.get("avgPlacement", 0)
    win_rate = data.get("winRate", 0)

    msg = (
        f"👤 {name}\n"
        f"积分: {pts} | 场次: {games}\n"
        f"吃鸡: {chickens} | 前四率: {win_rate:.0%}\n"
        f"场均排名: {avg:.1f}"
    )
    await player_cmd.finish(msg)
