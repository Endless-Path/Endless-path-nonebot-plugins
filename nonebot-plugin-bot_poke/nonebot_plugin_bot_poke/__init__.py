from nonebot import on
from nonebot.adapters.onebot.v11 import Bot, Event
import re
import logging

# 初始化日志记录器
logger = logging.getLogger("nonebot")

# 统一处理 bot 自己发送的消息（群聊和私聊），只响应指令消息
message_sent_handler = on("message_sent", priority=5)

@message_sent_handler.handle()
async def handle_bot_message_sent(bot: Bot, event: Event):
    # 检查消息类型，区分群聊和私聊
    message_type = event.message_type

    # 提取Bot自身发送的原始消息
    raw_message = event.raw_message.strip()

    # 使用正则表达式严格匹配 "戳" 指令，允许 "戳" 后接 CQ 码或数字
    if not re.match(r"^戳\s*(\[CQ:at,qq=\d+\])?(\s+\d+)?$", raw_message):
        return  # 忽略不符合严格格式的指令

    # 从 raw_message 中提取出戳的次数，默认1次
    match = re.search(r'\d+$', raw_message)  # 提取末尾数字
    poke_times = int(match.group()) if match else 1  # 默认戳1次

    # 限制戳的次数在1到10次之间
    poke_times = max(1, min(poke_times, 10))

    if message_type == "group":
        # 处理群聊消息
        group_id = event.group_id

        # 从 raw_message 中提取出被艾特的用户（qq=... 的部分）
        at_users = re.findall(r'\[CQ:at,qq=(\d+)\]', raw_message)

        if not at_users:
            logger.error("群聊消息没有找到被艾特的用户！")  # 记录日志
            return

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

    elif message_type == "private":
        # 处理私聊消息
        target_user_id = event.target_id  # 提取 target_id（对方的QQ号）

        # 循环执行指定次数的戳一戳操作
        for _ in range(poke_times):
            try:
                # 调用 friend_poke API 进行戳一戳
                await bot.call_api(
                    "friend_poke",   # 调用 API
                    user_id=target_user_id  # 对方QQ号
                )
            except Exception as e:
                logger.error(f"戳用户 {target_user_id} 时发生错误: {str(e)}")  # 记录错误日志
