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
import boto3
from botocore.exceptions import NoCredentialsError
import hashlib
from PIL import Image

_LOG = logging.getLogger(__name__)


class Porn91:
    username = ''
    password = ''
    max_page = 50
    baseUrl = "https://www.91porn.com"
    cdnUrl = "https://vthumb.killcovid2021.com"
    uploadUrl = "https://www.example.com/http/uploads"
    cookieFileName = "cookie.txt"
    lastPageIds = []
    categories = {
        "ori": "原创",
        "hot": "当前最热",
        "top": "本月最热",
        "long": "10分钟",
        "longer": "20分钟",
        "tf": "本月收藏",
        # "hd": "高清", # 普通用户没权限
        "mf": "收藏最多",
        "rf": "精华",
    }
    global_cookies = RequestsCookieJar()
    timer = None

    def __init__(self, username, password, max_page, upload_url, access_key_id, secret_access_key, oss_bucket_name, oss_user_id):
        self.username = username
        self.password = password
        self.max_page = max_page
        self.timer = Utc8Timer()
        self.uploadUrl = upload_url
        # self.load_cookie()
        self.http = Http(self.baseUrl)
        self.oss = Oss(access_key_id, secret_access_key, oss_bucket_name, oss_user_id)
        

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
    
    def md5_encrypt(self,string):
        # 创建 MD5 对象
        md5 = hashlib.md5()
        # 更新要加密的字符串，需先编码为字节
        md5.update(string.encode('utf-8'))
        # 返回加密后的十六进制字符串
        return md5.hexdigest()

    # 获取打卡记录
    async def fetch_video_list(self,type="rf", page=1):
        endpoint = "/v.php?category="+type+"&viewtype=basic&page=" + str(page)
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
                "type": type, # 分类
                "url": urllib.parse.urljoin(self.baseUrl, href),
                "thumbnail": {
                    "url": urllib.parse.urljoin(self.baseUrl, thumbnail),
                    "width": 0,
                    "height": 0,
                    "size": 0
                },
                "video_thumb_mp4": video_thumb_mp4,
                "video_mp4": "",  # Placeholder for the actual video URL
                "author": author,
                "hot_count": hot
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
                # 下载图片
                size,image_path,width,height = await self.download_image(video['thumbnail']['url'])
                video['thumbnail'] = {
                    "url": image_path,
                    "width": width,
                    "height": height,
                    "size": size
                }
                # 下载mp4视频
                video['video_mp4'] = await self.download_mp4(source_tag['src'],video)
                _LOG.info("找到视频地址：%s", video['video_mp4'])
            else:
                _LOG.warning("未找到视频源标签")
        else:
            _LOG.warning("未找到视频标签")



    # 下载mp4视频
    async def download_video(self, video_url):
        _LOG.info("下载视频：%s", video_url)

    # 下载图片
    async def download_image(self, image_url):
        _LOG.info("下载图片：%s", image_url)
        # md5 作为文件名
        file_name = self.md5_encrypt(image_url)
        # 图片保存路径的相对地址
        image_path = "/upload/" + file_name + "."+ image_url.split(".")[-1]
        real_path = await self.http.download_file_playwright(image_url, image_path)
        # //获取图片的宽高和大小
        image = Image.open(real_path)
        width, height = image.size
        size = os.path.getsize(real_path)
        # 上传文件
        self.oss.upload_file_and_clean(real_path, image_path)
        return size,image_path,width,height

    # 下载文件进程
    async def download_mp4(self, url, video):
        _LOG.info("下载文件：%s", url)
        # md5 作为文件名
        file_name = self.md5_encrypt(url)
        # 文件保存路径的相对地址
        file_path = "/upload/" + file_name + ".mp4"
        real_path = await self.http.download_file_playwright(url, file_path)
        # 上传文件
        return self.oss.upload_file_and_clean(real_path, file_path)


    async def auto_sign(self):
        _LOG.info("今天是：%s", datetime.now().strftime("%Y-%m-%d"))
        ip = await self.fetch_ip()  # Await fetch_ip
        _LOG.info("当前IP：%s", ip)
        # 循环分类
        for type, category in self.categories.items():
            _LOG.info("开始处理分类：%s (%s)", category, type)
            await self.fetch_videos(type,1)
        # 所有都执行完毕
        await self.http.close_playwright()


        
    async def fetch_videos(self,type, page=1):
        if page > self.max_page:
            _LOG.info("达到最大页码，停止翻页")
            return
        video_list = await self.fetch_video_list(type,page)  # Await fetch_video_list
        _LOG.info("找到 %d 个视频", len(video_list))
        if video_list:
            headers = {}
            payload = {
                "source": "91porn",
                "check":1,
                "type": type,
                "videos": video_list
            }
            # 先检查哪些没有保存
            response = requests.post(self.uploadUrl, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                # 需要上传的id ：result['data']=[111,222,333]
                _LOG.info("检查视频列表成功")
                _LOG.info(result)
                if 'data' in result and isinstance(result['data'], list):
                    ids_to_upload = result['data']
                    _LOG.info("需要上传的视频ID列表：%s", ids_to_upload)
                    # 过滤出需要上传的视频
                    video_list = [video for video in video_list if video['id'] in ids_to_upload]
                    _LOG.info("需要上传的视频数量：%d", len(video_list))
                else:
                    _LOG.warning("返回数据格式不正确，无法检查已保存视频")
            for video in video_list:
                await self.fetch_video_page(video)

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
        await self.fetch_videos(type,page+1)

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

    async def download_file_playwright(self, url, file_path, encrypt=False):
        # 判断目录是否存在，并且构造绝对地址
        # 当前目录+/upload/video/12345/thumbnail.jpg
        file_path = os.path.join(os.path.dirname(__file__), file_path.lstrip("/"))
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 直接browser下载
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        # 文件base64转码后，再把前10个字符与结尾10个字符交换
        if encrypt:
            # 读取文件内容并进行 Base64 编码
            encoded_data = base64.b64encode(response.content)
            # 交换前 10 个字符与结尾 10 个字符
            if len(encoded_data) > 20:  # 确保长度足够
                encoded_data = (
                    encoded_data[-10:] + encoded_data[10:-10] + encoded_data[:10]
                )

            # 将修改后的 Base64 数据重新保存为文件
            with open(file_path, "wb") as f:
                f.write(encoded_data)
        else:
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            _LOG.debug("文件已保存到 %s", file_path)
        return file_path

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

class Oss:
    def __init__(self, access_key_id, secret_access_key, bucket_name, user_id):
        # Cloudflare R2 的配置
        self.s3 = boto3.client(
            's3',
            aws_access_key_id= access_key_id, # 任意值
            aws_secret_access_key= secret_access_key, # 使用 API Token
            region_name="auto",  # Cloudflare R2 使用 "auto"
            endpoint_url="https://"+user_id+".r2.cloudflarestorage.com"  # 替换为您的 R2 API 地址
        )
        self.bucket_name = bucket_name
        
        
    def upload_file_and_clean(self, real_path, file_path):
         # 上传文件
        self.upload_file(real_path, file_path)
        # 删除本地文件
        try:
            if os.path.exists(real_path):
                os.remove(real_path)
                _LOG.info("删除本地文件 %s 成功", real_path)
        except FileNotFoundError:
            _LOG.error("删除本地文件 %s 失败，文件未找到", real_path)
            pass
        return file_path
    
    
    def upload_file(self, file_path, object_name=None):
        try:
            # object_name去掉最前面斜杠
            if object_name is None:
                object_name = os.path.basename(file_path)
            elif object_name.startswith("/"):
                object_name = object_name[1:]
            # 上传文件到指定路径
            self.s3.upload_file(file_path, self.bucket_name, object_name)
            _LOG.info("上传文件 %s 到桶 %s 成功", file_path, self.bucket_name)
            return True
        except FileNotFoundError:
            _LOG.error("文件 %s 未找到", file_path)
            return False
        except NoCredentialsError:
            _LOG.error("凭证错误")
            return False
        except Exception as e:
            _LOG.error("上传文件失败: %s", e)
            return False

class CaptchaError(Exception):
    ...


class SignFailError(Exception):
    ...


class TiebaStatuError(Exception):
    ...
