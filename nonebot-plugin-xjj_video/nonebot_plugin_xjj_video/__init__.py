from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State
import httpx
import asyncio
import time
from collections import defaultdict

__plugin_meta__ = PluginMetadata(
    name="小姐姐视频",
    description="获取并发送小姐姐视频",
    usage='输入"小姐姐视频"或"小姐姐"触发',
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
        response = await client.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        
        if url == API_ENDPOINTS[4]:
            return url
        
        data = response.json()
        
        if url == API_ENDPOINTS[0]:
            return data.get("data")
        elif url == API_ENDPOINTS[1]:
            return data.get("data")
        elif url == API_ENDPOINTS[2]:
            return data.get("data")
        elif url == API_ENDPOINTS[3]:
            return data.get("data", {}).get("video")
        
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

    video_urls = []
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for api_url in API_ENDPOINTS:
                video_url = await get_video_url(client, api_url)
                if video_url:
                    video_urls.append(video_url)
                if len(video_urls) >= 5:  # 获取到5个视频URL就停止
                    break
            
            logger.info(f"Retrieved {len(video_urls)} valid video URLs")
            
            if not video_urls:
                await bot.send(event, "获取视频失败，请稍后再试。")
                return

        # 创建转发消息节点列表
        messages = []
        for i, video_url in enumerate(video_urls, start=1):
            try:
                video_msg = MessageSegment.video(file=video_url)
                node = {
                    "type": "node",
                    "data": {
                        "name": "小姐姐视频",
                        "uin": bot.self_id,
                        "content": video_msg
                    }
                }
                messages.append(node)
            except Exception as e:
                logger.error(f"Error preparing video {i}: {str(e)}")

        if messages:
            # 发送转发消息
            await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=messages)
            logger.info(f"Sent {len(messages)} videos as a forward message")
        else:
            await bot.send(event, "无法生成转发消息，请稍后再试。")
    except Exception as e:
        logger.error(f"Error in handle_xjj_video: {str(e)}")
        await bot.send(event, f"发送视频失败：{str(e)}")
