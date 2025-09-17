import datetime
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

_LOG = logging.getLogger(__name__)


# 时间戳转换为北京时间
class Utc8Timer:
    def __init__(self):
        self.tz = pytz.timezone('Asia/Shanghai')

    def timestamp_to_time(self, timestamp):
        # timestamp是时间戳
        time = datetime.datetime.fromtimestamp(timestamp, self.tz)
        return time

    def time_to_timestamp(self, time):
        # time是datetime格式
        timestamp = int(time.timestamp())
        return timestamp

    def get_now_time(self):
        # 获取当前时间
        now_time = datetime.datetime.now(self.tz)
        return now_time

    def get_now_timestamp(self):
        # 获取当前时间戳
        now_timestamp = int(datetime.datetime.now(self.tz).timestamp())
        return now_timestamp

    def get_now_time_str(self):
        # 获取当前时间字符串
        now_time_str = datetime.datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S')
        return now_time_str

    # 2024年09月29日　星期日　09:21:19
    def get_now_time_str_cn(self):
        # 获取当前时间字符串
        week_day = ['一', '二', '三', '四', '五', '六', '日', ]
        week_name = week_day[datetime.datetime.now(self.tz).weekday()]
        now_time_str = datetime.datetime.now(self.tz).strftime('%Y年%m月%d日 星期') + week_name + datetime.datetime.now(
            self.tz).strftime(' %H:%M:%S')
        return now_time_str

    def get_now_date_str(self):
        # 获取当前日期字符串
        now_date_str = datetime.datetime.now(self.tz).strftime('%Y-%m-%d')
        return now_date_str

    def get_now_time_str_no_space(self):
        # 获取当前时间字符串
        now_time_str = datetime.datetime.now(self.tz).strftime('%Y%m%d%H%M%S')
        return now_time_str

    def get_now_date_str_no_space(self):
        # 获取当前日期字符串
        now_date_str = datetime.datetime.now(self.tz).strftime('%Y%m%d')
        return now_date_str

    def get_now_time_str_no_space_no_colon(self):
        # 获取当前时间字符串
        now_time_str = datetime.datetime.now(self.tz).strftime('%Y%m%d%H%M%S')
        return now_time_str

    def get_now_date_str_no_space_no_colon(self):
        # 获取当前日期字符串
        now_date_str = datetime.datetime.now(self.tz).strftime('%Y%m%d')
        return now_date_str

    def get_now_time_str_no_space_no_colon_no_dash(self):
        # 获取当前时间字符串
        now_time_str = datetime.datetime.now(self.tz).strftime('%Y%m%d%H%M%S')
        return now_time_str

    def get_now_date_str_no_space_no_colon_no_dash(self):
        # 获取当前日期字符串
        now_date_str = datetime.datetime.now(self.tz).strftime('%Y%m%d')
        return

    def get_time_from_str(self, time_str):
        # 从字符串获取时间并解决时差问题
        naive_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        localized_time = self.tz.localize(naive_time)
        return localized_time

    def get_timestamp_from_str(self, time_str):
        # 从字符串获取时间戳
        time = self.get_time_from_str(time_str)
        timestamp = int(time.timestamp())
        return timestamp


class SendEmail:
    def __init__(self, email, password):
        self.server = 'smtp.163.com'
        self.port = 465
        self.email = email
        self.password = password

    def send_email(self, to_email, subject, content):
        # 创建一个带附件的实例
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to_email
        msg['Subject'] = subject
        # 邮件正文内容
        msg.attach(MIMEText(content, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP_SSL(self.server, self.port)
            server.login(self.email, self.password)
            server.sendmail(self.email, to_email, msg.as_string())
            server.quit()
            _LOG.info("邮件发送成功")
        except smtplib.SMTPException as e:
            _LOG.info("Error: 无法发送邮件", e)
