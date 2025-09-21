# 引入portal 模块
from daka.porn91 import Porn91
from datetime import datetime
import logging
# Utc8Timer
from daka.util import Utc8Timer, SendEmail

_LOG = logging.getLogger(__name__)


class Daka:
    username = ''
    password = ''
    app_id = ''
    app_secret = ''
    email = ''
    email_password = ''
    to_email = ''
    max_page = 5
    timer = None

    def __init__(self, username, password, email, email_password, to_email, max_page):
        self.username = username
        self.password = password
        self.email = email
        self.email_password = email_password
        self.to_email = to_email
        self.max_page = max_page
        self.timer = Utc8Timer()
        self.porn91 = Porn91(username, password, max_page)

    def has_already_clocked(self, last_card_date, timestamp, begin, end):
        if not last_card_date:
            return False
        last_card_time = self.timer.get_timestamp_from_str(last_card_date)
        return begin <= last_card_time <= end

    async def auto_sign(self):
        _LOG.info("开始自动打卡...")
        await self.porn91.auto_sign()  # Ensure this is awaited
        _LOG.info("打卡完成！")
