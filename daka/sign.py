# 引入portal 模块
from daka.porn91 import Porn91
from datetime import datetime
import logging
# Utc8Timer
from daka.util import Utc8Timer, SendEmail

_LOG = logging.getLogger(__name__)


class Daka:
    max_page = 5
    timer = None

    def __init__(self, max_page, upload_url,access_key_id, secret_access_key, oss_bucket_name, oss_user_id):
        self.max_page = max_page
        self.timer = Utc8Timer()
        self.porn91 = Porn91(max_page, upload_url, access_key_id, secret_access_key, oss_bucket_name, oss_user_id)

    async def auto_sign(self):
        _LOG.info("开始自动打卡...")
        await self.porn91.auto_sign()  # Ensure this is awaited
        _LOG.info("打卡完成！")
