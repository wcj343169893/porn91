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
    timer = None

    def __init__(self, username, password, email, email_password, to_email):
        self.username = username
        self.password = password
        self.email = email
        self.email_password = email_password
        self.to_email = to_email
        self.timer = Utc8Timer()

    def has_already_clocked(self, last_card_date, timestamp, begin, end):
        if not last_card_date:
            return False
        last_card_time = self.timer.get_timestamp_from_str(last_card_date)
        return begin <= last_card_time <= end

    def auto_sign(self):
        # 自动生成今天的日期
        today = self.timer.get_now_date_str()
        _LOG.info("今天是：%s", today)
        now = self.timer.get_now_time_str()
        now_timestamp = self.timer.get_now_timestamp()

        porn = Porn91(self.username, self.password)
        ip = porn.fetch_ip()
        _LOG.info("当前IP：%s", ip)
        # 获取打卡记录
        last_card_date = porn.fetch_video_list()
