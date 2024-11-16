import nonebot
from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler
from datetime import datetime
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="定时群打卡",
    description="定时打卡指定的群",
    usage="自动执行群打卡任务",
    type="application",
    homepage="https://github.com/NoneBot/NoneBot",
    config="群打卡API接口配置"
)

# 配置群列表，只打卡指定群
config = {
    "group_list": [123456789, 987654321],  # 需要打卡的群ID
}

# 群打卡函数
async def check_in_group(bot: Bot, group_id: int):
    try:
        # 调用 OneBot API 打卡
        await bot.call_api('set_group_sign', group_id=group_id)
        logger.info(f"群 {group_id} 签到成功！")
    except Exception as e:
        logger.error(f"群 {group_id} 打卡失败: {e}")

# 定时任务：每天晚上12点01分进行打卡
@scheduler.scheduled_job("cron", hour=0, minute=1)  # 每天 00:01 执行打卡
async def scheduled_check_in():
    # 获取当前时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"定时任务开始，时间：{now}")

    # 获取当前Bot实例
    bot = nonebot.get_bot()

    # 遍历配置中的群ID进行打卡
    for group_id in config["group_list"]:
        await check_in_group(bot, group_id)
