from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State
import httpx
import asyncio
import time
import random
from collections import defaultdict

__plugin_meta__ = PluginMetadata(
    name="小姐姐视频",
    description="获取并发送小姐姐视频",
    usage='输入"小姐姐视频"或"小姐姐"触发，使用"@bot 小姐姐 n"指定数量，n默认3，最高5',
    type="application",
    homepage="https://github.com/Endless-Path/Endless-path-nonebot-plugins/tree/main/nonebot-plugin-xjj_video",
    supported_adapters={"~onebot.v11"},
)

last_use_time = defaultdict(float)
COOLDOWN_TIME = 60  # 冷却时间，单位：秒

xjj_video = on_command("小姐姐视频", aliases={"小姐姐"}, rule=to_me(), priority=5)

API_ENDPOINTS = [
    "https://tools.mgtv100.com/external/v1/pear/xjj",
    "http://api.yujn.cn/api/zzxjj.php?type=json",
    "http://www.wudada.online/Api/ScSp",
    "https://api.qvqa.cn/api/cos/?type=json",
    "https://jx.iqfk.top/api/sjsp.php"
]

async def get_video_url(client, url):
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        if url == API_ENDPOINTS[4]:  # 直接返回URL类型
            return url
        data = response.json()
        return data.get("data") if url != API_ENDPOINTS[3] else data.get("data", {}).get("video")
    except Exception as e:
        logger.error(f"Error fetching video from {url}: {str(e)}")
    return None

@xjj_video.handle()
async def handle_xjj_video(bot: Bot, event: MessageEvent, state: T_State):
    user_id = event.get_user_id()
    current_time = time.time()
    if current_time - last_use_time[user_id] < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - last_use_time[user_id]))
        await bot.send(event, f"命令冷却中，请在{remaining_time}秒后再试。")
        return
    last_use_time[user_id] = current_time

    # 获取视频数量参数
    args = str(event.get_message()).strip().split()
    video_count = min(max(int(args[1]), 1), 5) if len(args) > 1 and args[1].isdigit() else 3

    # 随机选择 API 端点并获取视频 URL
    random.shuffle(API_ENDPOINTS)
    video_urls = []
    async with httpx.AsyncClient() as client:
        for api_url in API_ENDPOINTS:
            video_url = await get_video_url(client, api_url)
            if video_url:
                video_urls.append(video_url)
            if len(video_urls) >= video_count:
                break

    if not video_urls:
        await bot.send(event, "获取视频失败，请稍后再试。")
        return

    # 根据消息类型发送
    if isinstance(event, GroupMessageEvent):
        messages = [
            {"type": "node", "data": {"name": "小姐姐视频", "uin": bot.self_id, "content": MessageSegment.video(file=url)}}
            for url in video_urls
        ]
        # 使用重试机制发送转发消息
        for attempt in range(3):
            try:
                await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=messages)
                logger.info(f"Sent {len(messages)} videos as a forward message")
                break
            except Exception as e:
                logger.error(f"Error sending group forward message attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(2)
        else:
            await bot.send(event, "无法生成转发消息，请稍后再试。")
    elif isinstance(event, PrivateMessageEvent):
        # 私聊逐条发送视频
        for video_url in video_urls:
            try:
                await bot.send(event, MessageSegment.video(file=video_url))
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error sending video in private chat: {str(e)}")
                await bot.send(event, "发送视频失败，请稍后再试。")
