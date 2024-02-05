import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from PySide2.QtCore import Signal, QObject


class Crawl(QObject):
    # 通过信号在线程之间通信
    link_signal = Signal(str)
    progress_signal = Signal(int)

    def crawl_movie_links(self, search_keyword):
        base_url = 'https://yunpan1.cc/'
        search_url = f'{base_url}?q={search_keyword}'

        # 发送 GET 请求获取网页内容
        response = requests.get(search_url)

        # 检查响应状态码
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题中包含search_keyword的链接
            links = soup.select(f'ul li a:-soup-contains("{search_keyword}")')

            new_link = []
            i = 0

            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                # 访问每一个页面，获取资源链接
                response_new = requests.get(href)

                soup_new = BeautifulSoup(response_new.text, 'html.parser')

                # 使用正则表达式匹配链接
                pattern = re.compile(r'<a href="(https://[^"]+)" rel="ugc noopener nofollow" target="_blank">')
                matches = re.findall(pattern, str(soup_new))

                # 设置进度条
                i += 1
                value = i / len(links) * 100
                self.progress_signal.emit(value)
                print(text + " " + str(matches))
                hyperlink = ""
                for url in matches:
                    print(url)
                    if "quark" in url:
                        icon_path = "D:/Bf4_Movie/kuake.png"
                    elif "aliyundrive" in url:
                        icon_path = "D:/Bf4_Movie/ali.jpg"
                    elif "baidu" in url:
                        icon_path = "D:/Bf4_Movie/baidu.png"
                    else:
                        icon_path = "D:/Bf4_Movie/wangpan.png"

                    hyperlink += f'<br> <a href="{url}" target="_blank">{url}</a>'

                print(hyperlink)
                self.link_signal.emit(text + hyperlink)

        else:
            print(f'Error: {response.status_code}')


if __name__ == "__main__":
    search_keyword = input("请输入需要搜索的电影名字：\n")
