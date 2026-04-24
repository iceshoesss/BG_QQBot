"""帮助命令 — 显示所有可用命令"""

from nonebot import on_command, get_loaded_plugins
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="帮助",
    description="显示所有可用命令",
    usage="发送「帮助」或「菜单」",
)

help_cmd = on_command("帮助", aliases={"help", "菜单", "指令"}, priority=1, block=True)


@help_cmd.handle()
async def handle_help(bot: Bot, event: MessageEvent):
    lines = ["📖 联赛机器人命令一览\n"]

    for plugin in get_loaded_plugins():
        meta = plugin.metadata
        if not meta:
            continue
        # 跳过帮助插件自身
        if meta.name == "帮助":
            continue
        lines.append(f"  {meta.name} — {meta.description}")
        if meta.usage:
            lines.append(f"    用法: {meta.usage}")
        lines.append("")

    lines.append("发送具体命令即可使用")
    await help_cmd.finish("\n".join(lines))
