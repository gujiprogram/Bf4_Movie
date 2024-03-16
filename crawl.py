import math
import random
import re
import time
import aiohttp
import asyncio
import requests
from PySide2.QtCore import Signal, QObject
# from selenium import webdriver
# from msedge.selenium_tools import EdgeOptions
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# edge_driver_path = 'D:/EdgeDriver/msedgedriver.exe'

# 设置 Edge 选项
# edge_options = EdgeOptions()
# edge_options.use_chromium = True

# 更新 DesiredCapabilities.EDGE 的配置到 edge_options
# edge_options.capabilities.update(DesiredCapabilities.EDGE)

# 设置 pageLoadStrategy 为 "none"
# edge_options.set_capability("pageLoadStrategy", "none")

# selenium设置最大等待时间为 10 秒
max_wait_time = 10

# 模拟多个UA
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.37',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61',
]

# 随机选择一个UA
selected_user_agent = random.choice(user_agents)

headers = {
    'User-Agent': selected_user_agent,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Referer': 'https://www.zhihu.com',  # 更改Referer为不同的网站
    'Cookie': 'fuid=6d17cdac117a35de2226a87a46a9bb30; Hm_lvt_5d3e7a242a65066db573612ae03026fe=1707814582,1708136731; _gid=GA1.2.1763287700.1708136732; _ga=GA1.2.1260259804.1707814582; Hm_lpvt_5d3e7a242a65066db573612ae03026fe=1708160827; _ga_GLWK4EWNVY=GS1.1.1708157603.3.1.1708161743.60.0.0',
}

# edge_options.add_argument(f'--user-agent={selected_user_agent}')


class Crawl(QObject):
    # 通过信号在线程之间通信
    link_signal = Signal(str)
    progress_signal = Signal(int)

    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=max_wait_time) as response:
                return await response.text()

    async def Crawl_Start(self, search_keyword, crawl_thread):

        found_resource = False  # 添加一个标志，用于标记是否找到资源

        backup_urls = ['https://yunpan1.fun/', 'https://yunpan1.cc/', 'https://yunpan1.xyz/', 'https://yunpan1.com/']

        T1 = time.perf_counter()
        for base_url in backup_urls:
            print(crawl_thread.stop_requested)
            if crawl_thread.stop_requested:
                print("退出")
                break
            try:
                search_url = f'{base_url}?q={search_keyword}'
                # 发送异步 GET 请求获取网页内容
                response = await self.fetch(search_url)
                if "<!doctype html>" in response:
                    print(search_url)
                    break
                else:
                    print("开始尝试备用地址")
            except asyncio.TimeoutError:
                # 请求超时异常处理
                print(f"请求超时，限制时间: {max_wait_time}秒")
                print("开始尝试备用地址")
                continue
            except Exception as e:
                # 异常处理，比如连接超时等情况
                print(f"连接地址时出现异常: {base_url}, 错误信息: {str(e)}")

        T2 = time.perf_counter()

        print(f'获取网页请求耗时：{T2 - T1}秒')

        # 检查响应状态码
        if "<!doctype html>" in response:
            found_resource = True
            T1 = time.perf_counter()
            # 使用正则表达式匹配href后面的网址和<h2>标签中的文本
            pattern = re.compile(r'<a href="([^"]+)"[^>]*>([^<]+)</a>')
            links = re.findall(pattern, response)
            T2 = time.perf_counter()
            print(f'寻找详情链接耗时：{T2 - T1}秒')

            i = 0

            tasks = []
            texts = []

            for link in links:
                href = link[0]
                text = link[1].strip().replace(" ", "").replace("\n", "")

                if search_keyword not in text:
                    continue

                texts.append(text)
                tasks.append(self.fetch(href))

            for future in asyncio.as_completed(tasks):
                print(crawl_thread.stop_requested)
                if crawl_thread.stop_requested:
                    print("退出")
                    break

                try:
                    response_new = await asyncio.wait_for(future, timeout=max_wait_time)
                    # 正常处理已完成的任务
                    T1 = time.perf_counter()
                    pattern = re.compile(
                        r'<a href="(https://[^"]+)" rel="ugc noopener nofollow" target="_blank" rel="ugc noopener nofollow" target="_blank">')
                    matches = re.findall(pattern, response_new)
                    T2 = time.perf_counter()
                    print(f'访问一个详情页面并获取电影链接耗时：{T2 - T1}秒')

                    # 设置进度条
                    i += 1
                    value = i / len(texts) * 100
                    self.progress_signal.emit(value)
                    print(texts[i - 1] + " " + str(matches))
                    hyperlink = ""
                    for url in matches:
                        print(url)
                        if "quark" in url:
                            icon_path = "D:/Bf4_Movie/image/kuake.png"
                        elif "aliyundrive" in url:
                            icon_path = "D:/Bf4_Movie/image/ali.jpg"
                        elif "baidu" in url:
                            icon_path = "D:/Bf4_Movie/image/baidu.png"
                        else:
                            icon_path = "D:/Bf4_Movie/image/wangpan.png"

                        hyperlink += f'<br><div><img src="{icon_path}" alt="Icon"> <a href="{url}" target="_blank">{url}</a></div>'

                    print(hyperlink)
                    self.link_signal.emit(texts[i - 1] + hyperlink)

                except asyncio.TimeoutError:
                    self.progress_signal.emit(100)
                    print("任务超时，放弃处理该任务")

    def crawl_movie_links(self, search_keyword, crawl_thread):
        # 创建一个事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # 运行异步任务
            loop.run_until_complete(self.Crawl_Start( search_keyword, crawl_thread))
        finally:
            # 取消设置事件循环
            asyncio.set_event_loop(None)


class Crawl_pansearch(QObject):
    # 通过信号在线程之间通信
    link_signal = Signal(str)
    progress_signal = Signal(int)

    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=max_wait_time) as response:
                return await response.text()

    async def Crawl_Start(self, search_keyword, crawl_thread):

        url = 'https://www.pansearch.me/search?keyword=' + search_keyword
        response = requests.get(url)

        html = response.text

        i = 0

        print("进入")
        # 检查响应状态码
        if response.status_code == 200:
            print("响应码正常")
            # 获取资源页数
            pattern_pages = r'搜索到约 <span class="font-bold">([^<]+)</span>'
            pages = re.findall(pattern_pages, html)
            print(int(pages[0]))

            tasks = []
            texts = []

            for page in range(0, int(pages[0]), 10):
                href = 'https://www.pansearch.me/search?keyword=' + search_keyword + "&offset=" + str(page)
                texts.append(search_keyword)
                tasks.append(self.fetch(href))

            for future in asyncio.as_completed(tasks):
                print(crawl_thread.stop_requested)
                if crawl_thread.stop_requested:
                    print("退出")
                    break

                try:
                    response_new = await asyncio.wait_for(future, timeout=max_wait_time)
                    # 正常处理已完成的任务
                    pattern = re.compile(r'<a class="resource-link" target="_blank" href="([^"]+)">')
                    matches = re.findall(pattern, response_new)
                    print(len(matches))
                    # 设置进度条
                    i += 1
                    value = i / len(texts) * 100
                    self.progress_signal.emit(value)

                    hyperlink = ""
                    unwanted_urls = ['https://t.me/aliyunys', 'https://yiso.fun']
                    for url in matches:
                        if url in unwanted_urls:
                            continue
                        print(url)
                        if "quark" in url:
                            icon_path = "D:/Bf4_Movie/image/kuake.png"
                        elif "aliyundrive" in url or "alipan" in url:
                            icon_path = "D:/Bf4_Movie/image/ali.jpg"
                        elif "baidu" in url:
                            icon_path = "D:/Bf4_Movie/image/baidu.png"
                        else:
                            icon_path = "D:/Bf4_Movie/image/wangpan.png"

                        hyperlink += f'<br><div><img src="{icon_path}" alt="Icon"> <a href="{url}" target="_blank">{url}</a></div>'

                    print(hyperlink)
                    self.link_signal.emit(texts[i - 1] + hyperlink)

                except asyncio.TimeoutError:
                    self.progress_signal.emit(100)
                    print("任务超时，放弃处理该任务")


    def crawl_movie_links(self,search_keyword, crawl_thread):
        # 创建一个事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # 运行异步任务
            loop.run_until_complete(self.Crawl_Start(search_keyword, crawl_thread))
        finally:
            # 取消设置事件循环
            asyncio.set_event_loop(None)


if __name__ == "__main__":
    search_keyword = input("请输入需要搜索的电影名字：\n")
