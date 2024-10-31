from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg
import re
import logging

# 初始化日志记录器
logger = logging.getLogger("nonebot")

# 定义 "戳" 命令，严格匹配
poke_command = on_command("戳", permission=SUPERUSER, priority=5)

# 监听普通群消息，处理普通用户发送的命令
@poke_command.handle()
async def handle_poke(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 从消息中提取被艾特的用户
    at_users = [segment.data["qq"] for segment in args if segment.type == "at"]

    if not at_users:
        logger.error("没有艾特任何用户！")  # 记录日志
        return

    # 获取当前群号
    group_id = event.group_id

    # 使用正则表达式解析消息中指定的次数（支持空格后跟数字）
    match = re.search(r'\d+$', args.extract_plain_text().strip())  # 提取文本中的最后数字
    poke_times = int(match.group()) if match else 1  # 默认戳1次

    # 限制戳的次数在1到10次之间
    poke_times = max(1, min(poke_times, 10))

    # 循环对每一个艾特的用户执行指定次数的戳一戳操作
    for user_id in at_users:
        for _ in range(poke_times):
            try:
                # 调用 group_poke API 进行戳一戳
                await bot.call_api(
                    "group_poke",   # 调用 API
                    group_id=group_id,  # 传入群号
                    user_id=int(user_id)  # 被戳的用户QQ号
                )
            except Exception as e:
                logger.error(f"戳用户 {user_id} 时发生错误: {str(e)}")  # 记录错误日志
