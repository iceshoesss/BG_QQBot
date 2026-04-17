"""QQ 绑定 — 用户在网站生成绑定码，发给 bot 完成关联"""

from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .league_api import api_post

driver = get_driver()

__plugin_meta__ = PluginMetadata(
    name="QQ 绑定",
    description="用网站生成的绑定码关联 QQ 与游戏账号",
    usage="发送「绑定 绑定码」（绑定码在网站个人页生成）",
)

bind_cmd = on_command("绑定", priority=5, block=True)


@bind_cmd.handle()
async def handle_bind(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    code = args.extract_plain_text().strip().upper()
    if not code:
        await bind_cmd.finish(
            "用法: 绑定 <绑定码>\n"
            "绑定码在联赛网站个人页生成（5分钟有效）"
        )

    bot_key = getattr(driver.config, "bot_api_key", "")
    qq_id = str(event.user_id)

    try:
        data = await api_post(
            "/api/bind-code/verify",
            json={"botKey": bot_key, "code": code},
        )
    except Exception as e:
        await bind_cmd.finish(f"绑定失败: {e}")

    if not data.get("ok"):
        await bind_cmd.finish(f"绑定失败: {data.get('error', '未知错误')}")

    battle_tag = data.get("battleTag", "")
    display_name = data.get("displayName", battle_tag)

    # TODO: 持久化 QQ → battleTag 映射（存到 league_players 或本地文件）
    # 目前先直接返回结果，后续再加存储
    logger.info(f"QQ 绑定: {qq_id} → {battle_tag}")

    await bind_cmd.finish(f"绑定成功！\n{display_name} ↔ QQ:{qq_id}")
