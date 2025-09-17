import requests
from datetime import datetime
import logging

_LOG = logging.getLogger(__name__)


class RollApi:
    app_id = ''
    app_secret = ''
    baseUrl = 'https://www.mxnzp.com/api'

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    # 判断是否是工作日
    def is_working_day(self, date):
        """
        Check if a given date is a working day.
        """
        # 日期字符串格式化yyyyMMdd
        date = datetime.strptime(date, '%Y-%m-%d')
        date = date.strftime('%Y%m%d')
        # https://www.mxnzp.com/doc/detail?id=1
        url = self.baseUrl + '/holiday/single/' + date + '?app_id=' + self.app_id + '&app_secret=' + self.app_secret
        _LOG.info(url)
        response = requests.get(url)
        # {"code":1,"msg":"数据返回成功！","data":{"date":"2024-09-15","weekDay":7,"yearTips":"甲辰","type":2,"typeDes":"中秋节","chineseZodiac":"龙","solarTerms":"白露后","avoid":"探病.开渠.安葬.伐木.作灶.入宅","lunarCalendar":"八月十三","suit":"祭祀.理发.会亲友.进人口.嫁娶.针灸.入殓.移柩","dayOfYear":259,"weekOfYear":37,"constellation":"处女座","indexWorkDayOfMonth":0}}
        # print(response.text)
        # 获取返回的json数据
        result = response.json()
        # 判断是否是工作日type	整型	类型 0 工作日 1 假日 2 节假日 如果ignoreHoliday参数为true，这个字段不返回
        # _LOG.info(result)
        if result['code'] != 1:
            _LOG.error('请求失败:' + result['msg'])
            return False
        if result['data']['type'] == 0:
            _LOG.info('是工作日')
        else:
            _LOG.info('不是工作日')
        return result['data']['type'] == 0
