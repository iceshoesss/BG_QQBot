#!/usr/bin/env python3
"""炉石战棋联赛 QQ 机器人"""

from dotenv import load_dotenv
load_dotenv()  # 加载 .env

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)

nonebot.load_builtin_plugins("echo")
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()
