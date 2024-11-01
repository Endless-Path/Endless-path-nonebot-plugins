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
    description="获取并发送小姐姐视频",
    usage='输入"小姐姐视频"或"小姐姐"触发，使用"@bot 小姐姐 n"指定数量，n默认3，最高5',
    type="application",
    homepage="https://github.com/Endless-Path/Endless-path-nonebot-plugins/tree/main/nonebot-plugin-xjj_video",
    supported_adapters={"~onebot.v11"},
)

# 定义 URL 文件路径
URL_FILE_PATH = Path(__file__).parent / "visited_urls.txt"

# 冷却时间管理
last_use_time = defaultdict(float)
COOLDOWN_TIME = 60  # 冷却时间，单位：秒

# 定义命令
xjj_video = on_command("小姐姐视频", aliases={"小姐姐"}, rule=to_me(), priority=5)

# 缓存 URL 列表
video_urls = []

def load_video_urls():
    """加载视频 URL 文件到内存"""
    global video_urls
    if URL_FILE_PATH.exists():
        with open(URL_FILE_PATH, "r", encoding="utf-8") as f:
            video_urls = [line.strip() for line in f if line.strip()]
            logger.info(f"已加载 {len(video_urls)} 个视频 URL")
    else:
        logger.warning("视频 URL 文件不存在，请检查路径和文件。")

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

    # 加载视频 URL 列表（仅在缓存为空时加载）
    if not video_urls:
        load_video_urls()

    if not video_urls:
        await bot.send(event, "没有可用的视频 URL，请检查配置文件。")
        return

    # 随机选择指定数量的视频 URL
    selected_urls = random.sample(video_urls, min(video_count, len(video_urls)))

    # 逐条发送视频 URL
    for url in selected_urls:
        try:
            await bot.send(event, MessageSegment.video(file=url))
            await asyncio.sleep(1)  # 避免消息发送过快
        except Exception as e:
            logger.error(f"Error sending video from URL {url}: {str(e)}")
            await bot.send(event, f"发送视频失败，请稍后再试。")
