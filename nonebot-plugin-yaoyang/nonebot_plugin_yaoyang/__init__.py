import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Event
from pathlib import Path

# 定义指令 "耀阳"
yaoyang = on_command("耀阳")

# 指令触发时的处理逻辑
@yaoyang.handle()
async def handle_yaoyang(bot: Bot, event: Event):
    # 获取插件目录的data文件夹路径
    data_path = Path(__file__).parent / "data"
    
    # 获取 data 文件夹中的所有 MP3 文件
    mp3_files = list(data_path.glob("*.mp3"))

    # 判断是否有 MP3 文件
    if not mp3_files:
        await yaoyang.finish("音频文件不存在或未找到MP3文件！")

    # 随机选择一个 MP3 文件
    selected_file = random.choice(mp3_files)

    # 发送语音消息
    await bot.send(event, MessageSegment.record(f"file:///{selected_file.resolve()}"))
