import random
import time
import asyncio
from pathlib import Path
from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State
from collections import defaultdict

__plugin_meta__ = PluginMetadata(
    name="小姐姐视频",
    description="送小姐姐视频",
    usage='输入"小姐姐视频"或"小姐姐"触发，使用"@bot 小姐姐 n"指定数量，n默认3，最高5',
    type="application",
    homepage="https://github.com/Endless-Path/Endless-path-nonebot-plugins/tree/main/nonebot-plugin-xjj_video",
    supported_adapters={"~onebot.v11"},
)

# 定义视频文件夹路径和最大文件编号
VIDEO_DIR = Path(__file__).parent / "video"
MAX_VIDEO_NUMBER = 997  # 文件夹中视频编号最大值

# 冷却时间管理
last_use_time = defaultdict(float)
COOLDOWN_TIME = 60  # 冷却时间，单位：秒

# 定义命令
xjj_video = on_command("小姐姐视频", aliases={"小姐姐"}, rule=to_me(), priority=5)

@xjj_video.handle()
async def handle_xjj_video(bot: Bot, event: MessageEvent, state: T_State):
    user_id = event.get_user_id()
    current_time = time.time()

    # 冷却时间检查
    if current_time - last_use_time[user_id] < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - last_use_time[user_id]))
        await bot.send(event, f"命令冷却中，请在{remaining_time}秒后再试。")
        return

    last_use_time[user_id] = current_time

    # 获取视频数量参数
    args = str(event.get_message()).strip().split()
    video_count = min(max(int(args[1]), 1), 5) if len(args) > 1 and args[1].isdigit() else 3

    # 随机选择文件编号
    selected_numbers = random.sample(range(1, MAX_VIDEO_NUMBER + 1), video_count)

    # 构建文件路径并逐条发送视频
    for number in selected_numbers:
        video_path = VIDEO_DIR / f"{number}.mp4"
        if not video_path.exists():
            logger.warning(f"视频文件 {video_path.name} 不存在，跳过。")
            continue
        
        try:
            await bot.send(event, MessageSegment.video(file=f"file:///{video_path.resolve()}"))
            await asyncio.sleep(1)  # 避免消息发送过快
        except Exception as e:
            logger.error(f"Error sending video {video_path.name}: {str(e)}")
            await bot.send(event, f"发送视频 {video_path.name} 失败，请稍后再试。")
