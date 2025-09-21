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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import tempfile
import asyncio
from playwright.async_api import async_playwright
import shutil
import os

_LOG = logging.getLogger(__name__)


class Porn91:
    username = ''
    password = ''
    max_page = 50
    baseUrl = "https://www.91porn.com"
    cdnUrl = "https://vthumb.killcovid2021.com"
    uploadUrl = "https://fc-mp-e1a4ddb5-a7a7-4152-8292-d63e2cc3f4e4.next.bspapp.com/http/uploads"
    cookieFileName = "cookie.txt"
    lastPageIds = []
    global_cookies = RequestsCookieJar()
    timer = None

    def __init__(self, username, password, max_page = 50):
        self.username = username
        self.password = password
        self.max_page = max_page
        self.timer = Utc8Timer()
        # self.load_cookie()
        self.http = Http(self.baseUrl)
        # 判断是否有cookie
        cookies = self.http.session.cookies

    # 访问https://2025.ip138.com/，获得自己真是ip
    async def fetch_ip(self):
        url = "https://2025.ip138.com/"
        response = await self.http.make_request(  # Await the coroutine
            method="GET", endpoint=url
        )
        # 解析 HTML 内容
        soup = BeautifulSoup(response, 'html.parser')
        # 获取所有的视频列表 <div class="well well-sm videos-text-align">
        div = soup.find("div", class_="view")
        # 提取a标签中的文本内容
        ip = div.find('a').get_text(strip=True)
        return ip
    
    def fetch_video_list2(self, page=1):
        # 模拟真实浏览器的请求头
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        try:
            driver.get("https://www.google.com")
            print(driver.title)
        finally:
            driver.quit()

    # 获取打卡记录
    async def fetch_video_list(self, page=1):
        endpoint = "/v.php?category=rf&viewtype=basic&page=" + str(page)
        response =await self.http.make_request(
            method="GET", endpoint=endpoint
        )
        # print(response.text)
        # 把打卡记录转化为数组
        # 解析 HTML 内容
        soup = BeautifulSoup(response, 'html.parser')
        # 获取所有的视频列表 <div class="well well-sm videos-text-align">
        rows = soup.find_all("div", class_="col-xs-12 col-sm-4 col-md-3 col-lg-3")
        # 初始化一个数组来存储打卡记录
        video_records = []

        # 遍历每一行，提取打卡时间和上下班别
        for row in rows:
            cells = row.find_all('a')
            # 获取href
            href = cells[0]['href']
            record = cells[0].get_text(strip=True)
            # Extract the thumbnail
            thumbnail = row.find('img',class_='img-responsive')['src']
            id = row.find('div', class_='thumb-overlay')['id'].split('_')[-1]
            video_thumb_mp4 = self.cdnUrl + "/thumb/" + id + ".mp4"
            title = row.find('span', class_='video-title').get_text(strip=True)
            # 提取作者
            author = ""
            author_span = row.find('span', class_='info', string='作者:')
            if author_span:
                author = author_span.next_sibling.strip()
            # 提取热度
            hot = 0
            hot_span = row.find('span', class_='info', string='热度:')
            if hot_span:
                hot = int(hot_span.next_sibling.strip().replace('\xa0','').replace(',',''))

            video_records.append({
                "id": id,
                # base64 编码
                "title": base64.b64encode(title.encode()).decode(),
                "url": urllib.parse.urljoin(self.baseUrl, href),
                "thumbnail": urllib.parse.urljoin(self.baseUrl, thumbnail),
                "video_thumb_mp4": video_thumb_mp4,
                "video_mp4": "",  # Placeholder for the actual video URL
                "author": author,
                "hot": hot
            })
        # 打印打卡记录数组
        # _LOG.info(video_records)
        return video_records
    # 获取详情页面的视频播放地址
    async def fetch_video_page(self, video):
        _LOG.info("获取视频页面：%s", video['url'])
        endpoint = video['url']
        response = await self.http.make_request(
            method="GET", endpoint=endpoint
        )
        # 解析 HTML 内容
        soup = BeautifulSoup(response, 'html.parser')
        # 获取视频播放地址
        video_tag = soup.find('video', id='player_one_html5_api')
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag and 'src' in source_tag.attrs:
                video['video_mp4'] = source_tag['src']
                _LOG.info("找到视频地址：%s", video['video_mp4'])
            else:
                _LOG.warning("未找到视频源标签")
        else:
            _LOG.warning("未找到视频标签")



    # 下载mp4视频
    async def download_video(self, video_url):
        _LOG.info("下载视频：%s", video_url)

    # 下载图片
    async def download_image(self,image_url,id,flag="thumbnail"):
        _LOG.info("下载图片：%s", image_url)
        # 图片保存路径的相对地址
        image_path = "/upload/video/"+id+"/"+flag+".jpg"
        await self.http.download_file_playwright(image_url, image_path)

    # 下载文件进程
    async def download_file(self, url, file_path):
        _LOG.info("下载文件：%s", url)


    async def auto_sign(self):
        _LOG.info("今天是：%s", datetime.now().strftime("%Y-%m-%d"))
        ip = await self.fetch_ip()  # Await fetch_ip
        _LOG.info("当前IP：%s", ip)
        await self.fetch_videos(1)
        # 所有都执行完毕
        await self.http.close_playwright()


        
    async def fetch_videos(self, page=1):
        if page > self.max_page:
            _LOG.info("达到最大页码，停止翻页")
            return
        video_list = await self.fetch_video_list(page)  # Await fetch_video_list
        _LOG.info("找到 %d 个视频", len(video_list))
        if video_list:
            headers = {}
            payload = {
                "source": "91porn",
                "check":1,
                "videos": video_list
            }
            # 先检查哪些没有保存
            # response = requests.post(self.uploadUrl, json=payload, headers=headers)
            # if response.status_code == 200:
            #     result = response.json()
            #     # 需要上传的id ：result['data']=[111,222,333]
            #     _LOG.info("检查视频列表成功")
            #     _LOG.info(result)
            #     if 'data' in result and isinstance(result['data'], list):
            #         ids_to_upload = result['data']
            #         _LOG.info("需要上传的视频ID列表：%s", ids_to_upload)
            #         # 过滤出需要上传的视频
            #         video_list = [video for video in video_list if video['id'] in ids_to_upload]
            #         _LOG.info("需要上传的视频数量：%d", len(video_list))
            #     else:
            #         _LOG.warning("返回数据格式不正确，无法检查已保存视频")
            # for video in video_list:
            #     await self.fetch_video_page(video)

            # 发送列表到uploadUrl
            payload['check'] = 0
            # _LOG.info(payload)
            if len(video_list) == 0:
                _LOG.info("没有需要上传的视频")
            else:
                response = requests.post(self.uploadUrl, json=payload, headers=headers)
                if response.status_code == 200:
                    _LOG.info("上传视频列表成功")
                else:
                    _LOG.error("上传视频列表失败，状态码：%d", response.status_code)
        else:
            _LOG.info("没有找到视频列表")

        # 如果本页的id和上页的id超过一半一样，说明已经到底了
        if self.lastPageIds:
            same_count = len(set(self.lastPageIds) & set([video['id'] for video in video_list]))
            if same_count > len(video_list) / 2:
                _LOG.info("视频已经到底了，停止翻页")
                return
        # 翻页
        self.lastPageIds = [video['id'] for video in video_list]
        _LOG.info("处理下一页：%d", page+1)
        await self.fetch_videos(page+1)

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
        self.cache_path = os.path.join(os.path.dirname(__file__), "./playwright-cache")
        # 删除缓存文件夹
        try:
            if os.path.exists(self.cache_path):
                shutil.rmtree(self.cache_path)
        except FileNotFoundError:
            pass
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)    
        self.playwright_browser = None
        self.playwright_context = None
        self.playwright_page = None
        self.playwright = None

    async def init_playwright(self):
        if self.playwright_browser is None:
            self.playwright = await async_playwright().start()
            self.playwright_browser = await self.playwright.chromium.launch(headless=True)
            self.playwright_context = await self.playwright_browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                viewport={"width": 1366, "height": 768},
                device_scale_factor=2,
                has_touch=False,
                is_mobile=False,
            )
            # 清空 cookies 和缓存
            await self.playwright_context.clear_cookies()
            await self.playwright_context.clear_permissions()
            self.playwright_page = await self.playwright_context.new_page()
        return self.playwright_page
    
    async def close_playwright(self):
        if self.playwright_browser:
            await self.playwright_browser.close()
        if self.playwright:
            await self.playwright.stop()   

    async def download_file_playwright(self, url, file_path, timeout=30):
        # 判断目录是否存在，并且构造绝对地址
        # 当前目录+/upload/video/12345/thumbnail.jpg
        file_path = os.path.join(os.path.dirname(__file__), file_path.lstrip("/"))
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 直接browser下载
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        # page = await self.init_playwright()
        # await page.goto(url, timeout=timeout * 1000)
        # content = await page.content()
        # with open(file_path, "wb") as f:
        #     f.write(content.encode('utf-8'))
        _LOG.debug("文件已保存到 %s", file_path)

    async def make_request(
            self,
            method,
            endpoint,
            headers=None,
            params=None,
            cookies=None,
            data=None,
            verify=True,
            allow_redirects=True,
            retries=3,  # Retry mechanism
            timeout=10,  # Timeout for requests
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

        for attempt in range(retries):
            try:
                page = await self.init_playwright()
                await page.goto(url, timeout=timeout * 1000)  # Set timeout
                content = await page.content()
                resp = requests.Response()
                resp.status_code = 200  # Mock status code for success
                resp._content = content.encode('utf-8')  # Mock response content
                _LOG.debug("请求 %s 返回状态码 %s", url, resp.status_code)

                if resp.status_code == 200:
                    d = self.session.cookies.get_dict()
                    self.dump_cookie(base64.b64encode(json.dumps(d).encode()))
                    return resp.text
            except Exception as err:
                _LOG.error("请求失败: %s (尝试 %d/%d)", err, attempt + 1, retries)
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2)  # Exponential backoff can be added here

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
