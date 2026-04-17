"""排行榜 / 选手查询插件"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .league_api import api_get

__plugin_meta__ = PluginMetadata(
    name="排行榜",
    description="查询联赛排行榜和选手信息",
    usage="发送「排行榜」或「战绩 玩家名」",
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
        chicken_rate = p.get("chickenRate", 0)

        lines.append(
            f"{i}. {name}\n"
            f"   {pts}分 | {games}场 | 场均{avg:.1f} | "
            f"前四{win_rate:.0%} | 吃鸡{chicken_rate:.0%}({chickens})"
        )

    await leaderboard_cmd.finish("\n".join(lines))


@player_cmd.handle()
async def handle_player(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if not query:
        await player_cmd.finish("用法: 战绩 玩家名")

    # 拿排行榜数据做匹配
    try:
        all_players = await api_get("/api/players")
    except Exception as e:
        await player_cmd.finish(f"查询失败: {e}")

    if not all_players:
        await player_cmd.finish("暂无数据")

    # 精确匹配 displayName 或 battleTag
    exact = [p for p in all_players if p.get("displayName") == query or p.get("battleTag") == query]
    if len(exact) == 1:
        await _send_player_info(player_cmd, exact[0])
        return
    if len(exact) > 1:
        lines = [f"找到 {len(exact)} 个同名选手，请用完整 BattleTag 查询:"]
        for p in exact:
            lines.append(f"  战绩 {p['battleTag']}")
        await player_cmd.finish("\n".join(lines))
        return

    # 模糊匹配 displayName
    fuzzy = [p for p in all_players if query in p.get("displayName", "")]
    if len(fuzzy) == 1:
        await _send_player_info(player_cmd, fuzzy[0])
        return
    if len(fuzzy) > 1:
        lines = [f"找到 {len(fuzzy)} 个匹配选手:"]
        for p in fuzzy:
            lines.append(f"  战绩 {p['battleTag']}")
        await player_cmd.finish("\n".join(lines))
        return

    await player_cmd.finish(f"未找到「{query}」")


async def _send_player_info(matcher, data: dict):
    name = data.get("displayName", "?")
    tag = data.get("battleTag", "")
    pts = data.get("totalPoints", 0)
    games = data.get("leagueGames", 0)
    chickens = data.get("chickens", 0)
    avg = data.get("avgPlacement", 0)
    win_rate = data.get("winRate", 0)
    chicken_rate = data.get("chickenRate", 0)

    msg = (
        f"{name} ({tag})\n"
        f"积分: {pts} | 场次: {games}\n"
        f"前四率: {win_rate:.0%} | 吃鸡率: {chicken_rate:.0%}({chickens})\n"
        f"场均排名: {avg:.1f}"
    )
    await matcher.finish(msg)
