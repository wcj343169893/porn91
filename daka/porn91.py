from datetime import datetime
import requests
from requests.cookies import RequestsCookieJar
import time
from bs4 import BeautifulSoup
import random
import logging
from daka.util import Utc8Timer
import re
import os
import sys
import base64
import json
import urllib.parse

_LOG = logging.getLogger(__name__)


class Porn91:
    username = ''
    password = ''
    baseUrl = "https://www.91porn.com"
    cdnUrl = "https://vthumb.killcovid2021.com"
    cookieFileName = "cookie.txt"
    global_cookies = RequestsCookieJar()
    timer = None

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.timer = Utc8Timer()
        # self.load_cookie()
        self.http = Http(self.baseUrl)
        # 判断是否有cookie
        cookies = self.http.session.cookies
        # self.fetch_cookies()
        # self.fetch_ip()

    # 访问https://2025.ip138.com/，获得自己真是ip
    def fetch_ip(self):
        url = "https://2025.ip138.com/"
        response = self.http.make_request(
            method="GET", endpoint=url

        )
        # print(response.text)
        # 解析 HTML 内容
        soup = BeautifulSoup(response, 'html.parser')
        # 获取所有的视频列表 <div class="well well-sm videos-text-align">
        div = soup.find("div", class_="view")
        # 提取a标签中的文本内容
        ip = div.find('a').get_text(strip=True)
        return ip
    # 定义一个函数来获取cookie
    def fetch_cookies(self):
        url = self.baseUrl + "/ehrportal/loginFOpen.asp"

        data = {
            "op": "act",
            "hidIsCheckOTP": "0",
            "companyno": "54661506",
            "companyid": "7",
            "username": self.username,
            "password": self.password,
            "Mangoket_OTP": "",
            "selLanguage": "0",
            "imageField.x": "40",
            "imageField.y": "7",
            "string1": "瀏覽器請使用Chrome、Microsoft Edge、Firefox、Brave、Safari、IE 11以上版本，螢幕解析度請設為1024*768",
            "string2": "本系統由一零四科技股份有限公司創設。內容享有著作權，禁止侵害，違者必究"
        }

        # 发送POST请求并设置cookie
        # response = requests.post(url, data=data, cookies=self.global_cookies)
        response = self.http.make_request(
            method="POST", endpoint="/ehrportal/loginFOpen.asp", data=data
        )
        # 打印内容
        # print(response.text) 使用者認證失敗,無法登入
        if "使用者認證失敗,無法登入" in response:
            _LOG.error("登录失败")
            return False

        _LOG.info("登录成功")
        return True

    # 获取打卡记录
    def fetch_video_list(self, page=1):
        endpoint = "/v.php?category=rf&viewtype=basic&page=" + str(page)
        # print(url)
        # 发送GET请求
        cookies = 'CLIPSHARE=ec3e6783e7f1eba2340ef90c8d0cc201; ga=97633SGph1S5HeZcTfmczJNgccMj%2B5TTBE20AwAhsYr0pb5CefIzAg; __utma=50351329.1112671635.1758095559.1758095559.1758095559.1; __utmc=50351329; __utmz=50351329.1758095559.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.1.1406325012.1758095638; mode=m; evercookie_etag=undefined; evercookie_cache=undefined; cf_clearance=fgFB_m2r88OM.5mwReHTbDT44agLiAJYrqVZ7vcj6dg-1758110797-1.2.1.1-VClBM_robWMO1LcC165GzGoOcdOn4Yq0Clt30cjm0dJY7P1PX7yt6jiztW.xWWfIwTLryxcBRvQ1bhhVrZCOMBcgaxz9HPtuQJssf8sOl1oTXphyhQCbN3SIznbU6vYjWTdcb7llZN7RFJBZWG7mCXjK2FPk3O0gcPpEvav76f4hILuVuIQ5Ldji3tzHhVFZcmVezmpbsiZlL8IaFjUO7PiON8aQTpyUIltyt9U5h3o; _ga_K5S02BRGF0=GS2.1.s1758110798$o2$g0$t1758110798$j60$l0$h0'
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",    
            "Accept-Language": "zh-CN,zh;q=0.9",
            "cookie": cookies,
        }
        # response = requests.get(url, cookies=self.global_cookies)
        response = self.http.make_request(
            method="GET", endpoint=endpoint, headers=headers 

        )
        # print(response.text)
        # 把打卡记录转化为数组
        # 解析 HTML 内容
        soup = BeautifulSoup(response, 'html.parser')
        # 获取所有的视频列表 <div class="well well-sm videos-text-align">
        rows = soup.find_all("div", class_="well well-sm videos-text-align")
        # 初始化一个数组来存储打卡记录
        video_records = []

        # 遍历每一行，提取打卡时间和上下班别
        for row in rows:
            cells = row.find_all('a')
            # 获取href
            href = cells[0]['href']
            record = cells[0].get_text(strip=True)
            # Extract the thumbnail
            thumbnail = record.find('img')['src']
            id = record.find('div', class_='thumb-overlay')['id'].split('_')[-1]
            video_thumb_mp4 = self.cdnUrl + "/thumb/" + id + ".mp4"

            video_records.append({
                "id": id,
                "title": record.find('span', class_='video-title').get_text(strip=True),
                "url": urllib.parse.urljoin(self.baseUrl, href),
                "thumbnail": urllib.parse.urljoin(self.baseUrl, thumbnail),
                "video_thumb_mp4": video_thumb_mp4,
            })
        # 打印打卡记录数组
        _LOG.info(video_records)

    def fetch_new_red(self):
        # 切换选项卡
        # https://portal.gamehours.com/ehrportal/eWorkFlow/eWorkFlow_NewRed.asp?URL=~/Workflow_Frontend/Search/Default.aspx
        endpoint = "/ehrportal/eWorkFlow/eWorkFlow_NewRed.asp?URL=~/Workflow_Frontend/Search/Default.aspx"
        # _LOG.info(url)
        # response = requests.get(url, cookies=self.global_cookies)
        response = self.http.make_request(
            method="GET", endpoint=endpoint
        )
        # print(response.text)
        #  document.frm.action = $($("<div/>").html('https://portal.gamehours.com:443/WorkflowWeb/default.aspx?PORTAL_USER_ID=2001&amp;PORTAL_SYS_ADMIN=0&amp;PORTAL_COMPANY_ID=7&amp;PORTAL_SNO=54661506&amp;URL=~/Workflow_Frontend/Search/Default.aspx&amp;USER_CNAME=%E6%96%87%E6%9C%9D%E5%9D%87&amp;Portal_Language=0')).text();
        # 正则表达式提取URL
        # Define the regular expression pattern
        pattern = r"https://portal\.gamehours\.com:443/WorkflowWeb/default\.aspx\?P.*?['\"]"
        # pattern = r"\$\(\$\(\'<div/>\'\)\.html\((.*?)\)\)"
        # Search for the pattern in the text
        match = re.search(pattern, response)

        # Extract and print the matched URL
        if match:
            url = match.group(0).strip("'\"")
            _LOG.info(url)
            # 需要url decode转码
            url = url.replace("&amp;", "&")
            _LOG.info(url)
            # 访问url，获得新cookie

            response = self.http.make_request(
                method="POST", endpoint=url, headers={
                    "Origin": "https://portal.gamehours.com",
                    "Referer": "https://portal.gamehours.com/ehrportal/eWorkFlow/eWorkFlow_NewRed.asp?URL=~/Workflow_Frontend/Search/Default.aspx",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                }
            )
            # print(response)
            soup = BeautifulSoup(response, 'html.parser')
            # 提取内容ScriptManager1
            # 提取 __EVENTVALIDATION 的值
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
            # print(event_validation)
            # 提取 __VIEWSTATE 的值
            view_state = soup.find('input', {'name': '__VIEWSTATE'})['value']
            # 提取 ctl00$ContentPlaceHolderContent$txtEmpName 的值
            emp_name = soup.find('input', {'name': 'ctl00$ContentPlaceHolderContent$txtEmpName'})['value']
            # print(emp_name)
            # 提取 __VIEWSTATEGENERATOR 的值
            view_state_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
            # print(view_state_generator)
            # 从Sys.WebForms.PageRequestManager._initialize('ctl00$ScriptManager1', 'aspnetForm', ['tctl00$ContentPlaceHolderContent$UpdatePanel1',''], ['ctl00$ContentPlaceHolderContent$ibtnGo',''], [], 900, 'ctl00'); 正则提取ctl00$ScriptManager1 的值
            script_manager1 = 'ctl00$ContentPlaceHolderContent$ibtnGo'
            # print(script_manager1)
            _LOG.info("提交筛选数据")
            # @todo 没有切换成功，需要再仔细研究，理论上这边切换成功后，列表就能得到所有的数据
            # 访问https://portal.gamehours.com/WorkflowWeb/Workflow_Frontend/Search/Default.aspx?Portal_Language=0

            response = self.http.make_request(
                method="POST", endpoint="/WorkflowWeb/Workflow_Frontend/Search/Default.aspx?Portal_Language=0", data={
                    'ctl00$ScriptManager1': script_manager1,
                    'ctl00$ContentPlaceHolderContent$txtWORKSHEET_DATA_VIEW_ID': '',
                    'ctl00$ContentPlaceHolderContent$ddlStatus:': 0,
                    'ctl00$ContentPlaceHolderContent$ddlWorkSheetNAME': 'ALL',
                    'ctl00$ContentPlaceHolderContent$txtEmpName': emp_name,
                    'ctl00$ContentPlaceHolderContent$ucDateStart$TextBox1': '',
                    'ctl00$ContentPlaceHolderContent$ucDateEnd$TextBox1': '',
                    'ctl00$ContentPlaceHolderContent$Accordion1_AccordionExtender_ClientState': 0,
                    '__EVENTTARGET': '',
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATE': view_state,
                    '__VIEWSTATEGENERATOR': view_state_generator,
                    '__EVENTVALIDATION': event_validation,
                    '__ASYNCPOST': 'true',
                    'ctl00$ContentPlaceHolderContent$ibtnGo.x': 16,
                    'ctl00$ContentPlaceHolderContent$ibtnGo.y': 4,
                }, headers={
                    "Referer": "https://portal.gamehours.com/WorkflowWeb/Workflow_Frontend/Search/Default.aspx?Portal_Language=0",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "X-Microsoftajax": "Delta=true",
                    "X-Requested-With": "XMLHttpRequest",
                })
            # print(response)
            # 打印cookie
            for cookie in self.http.session.cookies:
                _LOG.info(f"{cookie.name}: {cookie.value}")

            return True
        else:
            _LOG.info("没有找到URL")
            _LOG.info(response)
            return False

    def fetch_workflow_options(self):
        endpoint = "/WorkflowWeb/Workflow_Frontend/Search/Default.aspx?Portal_Language=0"

    # 获取请假记录
    def fetch_workflow_list(self):
        check_result = self.fetch_new_red()
        if not check_result:
            return
        # return False
        # https://portal.gamehours.com/WorkflowWeb/Workflow_Frontend/Search/SearchDataListByWorkSheet.aspx?WorksheetID=384
        endpoint = "/WorkflowWeb/Workflow_Frontend/Search/SearchDataListByWorkSheet.aspx?WorksheetID=384"
        response = self.http.make_request(
            method="GET", endpoint=endpoint, headers={
                "Referer": "https://portal.gamehours.com/WorkflowWeb/Workflow_Frontend/Search/Default.aspx?Portal_Language=0",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
            }
        )

        # response = requests.get(url, cookies=self.global_cookies)
        # print(response)
        # 把打卡记录转化为数组
        # 解析 HTML 内容
        soup = BeautifulSoup(response, 'html.parser')
        # 获取所有请假记录 <tr id="tbWorkSheetDataList_116144" wsdInfoText="假勤項目：忘刷卡 忘帶卡
        # 開始日期：2024/09/14
        # 開始時間：0930
        # 結束日期：2024/09/14
        # 結束時間：1800
        # 固定職務代理人：CQ001  郭喜领
        # "
        rows = soup.find_all("tr", id=True, wsdinfotext=True)
        # 初始化一个数组来存储请假记录
        workflow_records = []
        # 读取wsdInfoText属性
        for row in rows:
            wsd_info_text = row['wsdinfotext']
            # 提取开始时间和节数时间
            begin_date = re.search(r"開始日期：(\d{4}/\d{2}/\d{2})", wsd_info_text).group(1)
            begin_time = re.search(r"開始時間：(\d{4})", wsd_info_text).group(1)
            end_date = re.search(r"結束日期：(\d{4}/\d{2}/\d{2})", wsd_info_text).group(1)
            end_time = re.search(r"結束時間：(\d{4})", wsd_info_text).group(1)

            workflow_records.append({
                "begin_time": datetime.strptime(begin_date + " " + begin_time + ":00", "%Y/%m/%d %H%M:%S").strftime(
                    "%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.strptime(end_date + " " + end_time + ":00", "%Y/%m/%d %H%M:%S").strftime(
                    "%Y-%m-%d %H:%M:%S"),
            })
        # 打印请假记录数组
        _LOG.info("请假记录：")
        _LOG.info(workflow_records)
        return workflow_records

    # 上班打卡
    def fetch_goto_work(self, last_goto_timestamp):
        # 打卡
        return self.fetch_clock(0, last_goto_timestamp)

    # 下班打卡
    def fetch_off_work(self, last_off_timestamp, off_work_begin):
        # 打卡
        # https://portal.gamehours.com/ehrportal//DEPT/Personal_CardData_Check.asp?strCARD_TYPE=1&strSubmitTemp=
        return self.fetch_clock(1, off_work_begin)

    # 检查打卡状态
    def check_clock(self, card_type, last_timestamp):
        workflow_records = self.fetch_workflow_list()
        # 如果当前时间在workflow_records内，则表示已经请假了
        for record in workflow_records:
            begin_time = self.timer.get_timestamp_from_str(record['begin_time'])
            end_time = self.timer.get_timestamp_from_str(record['end_time'])
            if begin_time <= last_timestamp <= end_time:
                _LOG.info('已经请假了')
                return '已经请假了'
        endpoint = "/ehrportal/DEPT/Personal_CardData_Check.asp?strCARD_TYPE=" + str(card_type) + "&strSubmitTemp="
        # 发送GET请求
        response = self.http.make_request(
            method="GET", endpoint=endpoint
        )
        # _LOG.info(response)
        # 不可重複刷卡
        if "不可重複刷卡" in response or "是否覆蓋" in response:
            _LOG.info("不可重複刷卡")
            return False
        else:
            _LOG.info("检查完成")
            return True

    # 获取刷卡页面信息
    def fetch_clock_default(self):
        endpoint = "/ehrportal/DEPT/Personal_CardData_Default.asp"
        # 获取刷卡页面信息
        response = self.http.make_request(
            method="GET", endpoint=endpoint
        )
        # _LOG.info(response)
        # 解析HTML内容
        soup = BeautifulSoup(response, 'html.parser')
        # 提取字段的值
        hidServerClock = soup.find('input', {'name': 'hidServerClock'})['value']
        txtEMP = soup.find('input', {'name': 'txtEMP'})['value']
        txtSECTION = soup.find('input', {'name': 'txtSECTION'})['value']
        # _LOG.info(hidServerClock)
        # _LOG.info(txtEMP)
        # _LOG.info(txtSECTION)
        return [hidServerClock, txtEMP, txtSECTION]

    # 统一打卡函数
    def fetch_clock(self, card_type, last_timestamp):
        # 检查是否已经打卡
        check_result = self.check_clock(card_type, last_timestamp)
        if not check_result:
            return False
        # hidSubmitTemp=&hidServerClock=2024-09-29+09%3A21%3A12&hidClientClock=2024-09-29+09%3A21%3A19&hidintSecond=&OP=Insert&hidMSG=ave&hidCARD_TYPE=0&hidCARD_DATA_ID=&hidCARD_DATA_ID_Q=&txtEMP=CQ007%E3%80%80%E6%96%87%E6%9C%9D%E5%9D%87&txtSECTION=2024%E5%B9%B409%E6%9C%8829%E6%97%A5%E3%80%80%E9%87%8D%E6%85%B6%E7%8F%AD%E5%88%A5%E3%80%8009%3A30%7E18%3A00&clock=2024%E5%B9%B409%E6%9C%8829%E6%97%A5%E3%80%80%E6%98%9F%E6%9C%9F%E6%97%A5%E3%80%8009%3A21%3A19&radiobutton=0
        endpoint = "/ehrportal/DEPT/Personal_CardData_Default.asp"
        hidServerClock, txtEMP, txtSECTION = self.fetch_clock_default()

        response = self.http.make_request(
            method="POST", endpoint=endpoint, data={
                "hidSubmitTemp": "",
                "hidServerClock": hidServerClock,
                "hidClientClock": self.timer.get_now_time_str(),
                "hidintSecond": "",
                "OP": "Insert",
                "hidMSG": "ave",
                "hidCARD_TYPE": card_type,
                "hidCARD_DATA_ID": "",
                "hidCARD_DATA_ID_Q": "",
                "txtEMP": txtEMP,
                "txtSECTION": txtSECTION,
                "clock": self.timer.get_now_time_str_cn(),
                "radiobutton": 0
            }
        )
        if "刷卡成功" in response:
            _LOG.info("刷卡成功")
            return "刷卡成功 " + self.timer.get_now_time_str_cn()
        else:
            _LOG.info("打卡失败")
            return response


class Http:
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/95.0.4638.54 Safari/537.36",
        }
        self.load_cookie()
        self.cookie_saved = False

    def make_request(
            self,
            method,
            endpoint,
            headers=None,
            params=None,
            cookies=None,
            data=None,
            verify=True,
            allow_redirects=True,
            **kwargs,
    ):
        # 合并全局 headers 和本次请求的 headers
        merged_headers = self.session.headers.copy()
        if headers:
            # self.session.headers.update(headers)
            merged_headers.update(headers)
        if cookies:
            self.session.cookies.update(cookies)
        if not endpoint.startswith("http"):
            url = self.base_url + endpoint
        else:
            url = endpoint
        resp = self.session.request(
            method,
            url=url,
            params=params,
            data=data,
            headers=merged_headers,
            verify=verify,
            allow_redirects=allow_redirects,
            **kwargs,
        )
        resp.raise_for_status()
        try:
            # 请求成功，保存cookie，下次直接从文件读取
            if resp.status_code == 200:
                d = self.session.cookies.get_dict()
                self.dump_cookie(base64.b64encode(json.dumps(d).encode()))

            return resp.text
        except ValueError as err:
            _LOG.error(err)

    def file_path(self) -> str:
        """
        获取cookie保存的目录
        """
        if sys.platform == "win32":
            base_path = os.environ.get("APPDATA")
        elif sys.platform == "linux":
            base_path = os.path.join(os.environ.get("HOME", "."), ".config")
        elif sys.platform == "darwin":
            base_path = os.path.join(os.environ.get("HOME", "."), ".config")
        else:
            base_path = ""
        path = os.path.join(base_path, "daka-sign")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def dump_cookie(self, cookie):
        """
        保存cookie到文件
        """
        file_path = os.path.join(self.file_path(), "cookie")
        with open(file_path, "wb") as f:
            f.write(cookie)
            f.close()
            # _LOG.debug(cookie)
            # _LOG.debug("写入凭证到%s", file_path)

    def load_cookie(self, file=None):
        """
        从文件中加载cookie
        """
        if not file:
            file = os.path.join(self.file_path(), "cookie")
        if os.path.exists(file):
            with open(file, "rb") as f:
                cookie = f.read()
                f.close()
                try:
                    _cookie = json.loads(base64.b64decode(cookie))
                    _LOG.debug("[+]找到凭证")
                    _LOG.debug("[+]从%s加载凭证", file)
                    _LOG.debug(_cookie)
                    self.session.cookies.update(_cookie)
                except Exception as err:
                    _LOG.error(err)


class CaptchaError(Exception):
    ...


class SignFailError(Exception):
    ...


class TiebaStatuError(Exception):
    ...
