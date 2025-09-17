# 引入rollApi
from daka.rollApi import RollApi
# 引入portal 模块
from daka.portal import Portal
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

    def __init__(self, username, password, app_id, app_secret, email, email_password, to_email):
        self.username = username
        self.password = password
        self.app_id = app_id
        self.app_secret = app_secret
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
        roll = RollApi(self.app_id, self.app_secret)
        working = roll.is_working_day(today)
        if working:
            # 判断现在是打上班卡还是下班卡，9:00-9:30之前是上班卡，18:00之後是下班卡
            go_to_work_begin = self.timer.get_timestamp_from_str(today + ' 09:00:00')
            go_to_work_end = self.timer.get_timestamp_from_str(today + ' 09:30:00')
            off_work_begin = self.timer.get_timestamp_from_str(today + ' 18:00:00')
            off_work_end = self.timer.get_timestamp_from_str(today + ' 19:00:00')
            now = self.timer.get_now_time_str()
            now_timestamp = self.timer.get_now_timestamp()
            _LOG.info("现在是：%s %s 上班时间是：%s 下班时间是：%s", now, now_timestamp,
                      go_to_work_begin, off_work_begin)
            # 判断是否是非打卡时间，9点之前，9点到18点之间都是不是打卡时间
            if (now_timestamp < go_to_work_begin or
                    go_to_work_end < now_timestamp < off_work_begin):
                _LOG.info('现在不是打卡时间')
                return

            portal = Portal(self.username, self.password)
            # 获取打卡记录
            last_card_date = portal.fetch_card_list()
            card_result = False
            # 判断今天是否已经打卡
            if go_to_work_begin < now_timestamp < go_to_work_end:
                if self.has_already_clocked(last_card_date, now_timestamp, go_to_work_begin, go_to_work_end):
                    _LOG.info('今天已经打过上班卡了')
                else:
                    card_result = portal.fetch_goto_work(go_to_work_end)
            elif off_work_begin < now_timestamp < off_work_end:
                if self.has_already_clocked(last_card_date, now_timestamp, off_work_begin, off_work_end):
                    _LOG.info('今天已经打过下班卡了')
                else:
                    card_result = portal.fetch_off_work(off_work_end, off_work_begin)
            else:
                _LOG.info('现在不是打卡时间')

            if card_result:
                # 发送邮件
                SendEmail(self.email, self.email_password).send_email(self.to_email, "打卡完成" + today, card_result)
