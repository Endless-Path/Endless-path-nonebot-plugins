import random
import asyncio
from nonebot import require, get_bot, on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger

# 定时任务所需的调度器
scheduler = require("nonebot_plugin_apscheduler").scheduler

# 自动群签到任务，每天9点触发
@scheduler.scheduled_job("cron", hour=9, minute=0)  # 每天早上9点
async def auto_group_sign_in():
    bot = get_bot()  # 获取机器人实例
    await group_sign_in(bot)

# 手动签到命令，仅超级用户可用
group_sign = on_command("群打卡", permission=SUPERUSER, priority=5)

# 手动打卡执行逻辑
@group_sign.handle()
async def handle_group_sign(bot: Bot):
    await group_sign_in(bot)

# 群签到任务执行函数
async def group_sign_in(bot: Bot):
    try:
        # 获取机器人所在的所有群信息
        group_list = await bot.call_api("get_group_list")
        for group in group_list:
            group_id = str(group["group_id"])  # 确保 group_id 是字符串类型

            # 随机等待一段时间，避免连续操作触发风控
            delay = random.uniform(10, 30)  # 随机间隔10到30秒
            logger.info(f"等待 {delay:.2f} 秒后为群 {group_id} 签到...")
            await asyncio.sleep(delay)

            # 调用set_group_sign API接口进行签到
            try:
                await bot.call_api('set_group_sign', group_id=group_id)
                logger.info(f"群 {group_id} 签到成功！")
            except Exception as e:
                logger.error(f"群 {group_id} 签到失败: {e}")
    
    except Exception as e:
        logger.error(f"自动签到出错: {e}")

