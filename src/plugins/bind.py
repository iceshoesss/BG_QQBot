"""QQ 绑定 — 将 QQ 号关联到游戏账号"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .league_api import api_post

__plugin_meta__ = PluginMetadata(
    name="QQ 绑定",
    description="将 QQ 号关联到炉石战棋游戏账号",
    usage="发送「绑定 BattleTag#1234」获取验证码",
)

bind_cmd = on_command("绑定", priority=5, block=True)


@bind_cmd.handle()
async def handle_bind(bot: Bot, event: GroupMessageEvent, args=CommandArg()):
    battle_tag = args.extract_plain_text().strip()
    if not battle_tag:
        await bind_cmd.finish("用法: 绑定 BattleTag#1234")

    qq_id = str(event.user_id)

    try:
        data = await api_post(
            "/api/qq/bind-code",
            json={"qq_id": qq_id, "battle_tag": battle_tag},
        )
    except Exception as e:
        await bind_cmd.finish(f"绑定失败: {e}")

    code = data.get("verification_code", "???")
    await bind_cmd.finish(
        f"绑定码: {code}\n"
        f"请在 HDT 插件设置中输入此验证码完成绑定"
    )
