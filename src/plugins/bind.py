"""QQ 绑定 — 用户在网站生成绑定码，发给 bot 完成关联"""

import json
import os
from pathlib import Path

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .league_api import api_post

__plugin_meta__ = PluginMetadata(
    name="QQ 绑定",
    description="用网站生成的绑定码关联 QQ 与游戏账号",
    usage="发送「绑定 绑定码」「我的绑定」「解绑」",
)

BIND_FILE = Path(__file__).parent.parent.parent / "data" / "qq_bindings.json"

bind_cmd = on_command("绑定", priority=5, block=True)
my_bind_cmd = on_command("我的绑定", aliases={"查绑定", "查询绑定"}, priority=5, block=True)
unbind_cmd = on_command("解绑", aliases={"取消绑定", "解除绑定"}, priority=5, block=True)


def _load_bindings() -> dict:
    if BIND_FILE.exists():
        return json.loads(BIND_FILE.read_text(encoding="utf-8"))
    return {}


def _save_bindings(data: dict):
    BIND_FILE.parent.mkdir(parents=True, exist_ok=True)
    BIND_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@bind_cmd.handle()
async def handle_bind(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    code = args.extract_plain_text().strip().upper()
    if not code:
        await bind_cmd.finish(
            "用法: 绑定 <绑定码>\n"
            "绑定码在联赛网站个人页生成（5分钟有效）"
        )

    bot_key = os.environ.get("BOT_API_KEY", "")
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

    # 保存映射
    bindings = _load_bindings()
    bindings[qq_id] = {"battleTag": battle_tag, "displayName": display_name}
    _save_bindings(bindings)

    logger.info(f"QQ 绑定: {qq_id} → {battle_tag}")
    await bind_cmd.finish(f"绑定成功！\n{display_name} ↔ QQ:{qq_id}")


@my_bind_cmd.handle()
async def handle_my_bind(bot: Bot, event: MessageEvent):
    qq_id = str(event.user_id)
    bindings = _load_bindings()
    info = bindings.get(qq_id)

    if info:
        await my_bind_cmd.finish(
            f"你已绑定: {info['displayName']} ({info['battleTag']})"
        )
    else:
        await my_bind_cmd.finish(
            "你还没有绑定。\n"
            "1. 登录联赛网站 → 个人页 → 生成绑定码\n"
            "2. 发送「绑定 <绑定码>」完成绑定"
        )


@unbind_cmd.handle()
async def handle_unbind(bot: Bot, event: MessageEvent):
    qq_id = str(event.user_id)
    bindings = _load_bindings()
    info = bindings.pop(qq_id, None)

    if not info:
        await unbind_cmd.finish("你还没有绑定，无需解绑。")

    _save_bindings(bindings)
    logger.info(f"QQ 解绑: {qq_id} ← {info['battleTag']}")
    await unbind_cmd.finish(f"已解绑 {info['displayName']}，之后问题对局通知将不再 @ 你。")
